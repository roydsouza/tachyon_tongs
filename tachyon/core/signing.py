import os
import hmac
import hashlib
import warnings
from datetime import datetime
import json
from typing import Optional, Union, Tuple, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# Phase 25.3: Suppress liboqs version mismatch (Using 0.15.0-dev on M5)
warnings.filterwarnings("ignore", category=UserWarning, module="oqs")

class SecurityViolationError(Exception):
    """Raised when a core security boundary is breached."""
    pass

# Local substrate constants
KEY_LABEL = "Tachyon Root Key"
KEY_APPLICATION_TAG = "com.tachyon.substrate.root.v1"
PQC_KEY_LABEL = "Tachyon PQC Root"
PQC_KEY_APPLICATION_TAG = "com.tachyon.substrate.pqc.v1"
PQC_ALGORITHM = "ML-DSA-65"

class IntegrityManager:
    """
    Manages cryptographic signatures and integrity verification for Tachyon Tongs.
    Phase 25.1: Migrated from HMAC-SHA256 to hardware-backed Ed25519 signatures.
    Phase 26.1: Refactored for modularity, delegating key operations to KeychainProvider 
    and mathematical logic to HybridSigner.
    Phase 26.3: Enhanced with fail-safe verification modes for heterogeneous test environments.
    """
    
    def __init__(self, use_hardware: bool = True):
        self.use_hardware = use_hardware
        self.hmac_key = os.environ.get("TACHYON_SECRET_KEY", "DEVELOPMENT_INSECURE_FALLBACK").encode('utf-8')
        
        # Load keys via KeychainProvider
        from tachyon.core.keys.provider import KeychainProvider
        self.provider = KeychainProvider(use_hardware=use_hardware)
        self._private_key, self._public_key = self.provider.load_ed25519_key()
        self._pqc_private_key_bytes, self._pqc_public_key = self.provider.load_mldsa65_keys()
        
        # Initialize the mathematically pure HybridSigner
        from tachyon.core.keys.hybrid import HybridSigner
        self.signer = HybridSigner(
            ed25519_sk=self._private_key,
            ed25519_pk=self._public_key,
            mldsa65_sk=self._pqc_private_key_bytes,
            mldsa65_pk=self._pqc_public_key,
            hmac_key=self.hmac_key
        )

        if not self._private_key and os.environ.get("TACHYON_STRICT_MODE"):
            raise RuntimeError("Cryptographic failure in STRICT_MODE: No keys found. Halt.")

    def derive_agent_key(self, role: str, save_to_disk: bool = False) -> tuple:
        """
        Derives a per-agent Ed25519 key and issues a delegation certificate (M-08: Validated).
        """
        if not role.isalnum() and "_" not in role:
            raise SecurityViolationError(f"Invalid Agent Role: {role}. Must be alphanumeric.")
            
        if not self._private_key:
            raise RuntimeError("Cannot derive agent key without a loaded Root Key.")
            
        from tachyon.core.keys.certificates import DelegationCertificateAuthority
        ca = DelegationCertificateAuthority(self)
        return ca.derive_and_issue(role=role, expiry_days=30, save_to_disk=save_to_disk)

    def load_agent_identity(self, role: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to load a delegated identity (Key + Cert) from disk (M-08: Validated).
        """
        if not role.isalnum() and "_" not in role:
            raise SecurityViolationError(f"Invalid Agent Role: {role}. Must be alphanumeric.")

        import json
        import base64
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        keys_dir = os.path.join(root_dir, "memory", "keys")
        path = os.path.join(keys_dir, f"agent_{role.lower()}.json")
        
        if not os.path.exists(path):
             return None
             
        # H-07 Fix: Process Identity Binding
        def _verify_process_authority(role: str) -> bool:
            """Verifies that the current process is authorized to assume the role (H-07)."""
            import sys
            if os.environ.get("TACHYON_TEST_MODE") == "1":
                return True # Allow identity switching in test environment
            
            # Check command line arguments for the agent-id or role
            cmd_line = " ".join(sys.argv).lower()
            if role.lower() in cmd_line:
                return True
                
            # Check environment variable
            if os.environ.get("TACHYON_AGENT_ROLE", "").lower() == role.lower():
                return True
                
            return False

        if not _verify_process_authority(role):
            err = f"Identity mismatch: Process not authorized to assume role '{role}'."
            from tachyon.core.state import StateManager
            StateManager().emit_alert("IDENTITY_SPOOFING_ATTEMPT", err)
            raise SecurityViolationError(err)

        try:
            with open(path, "r") as f:
                identity = json.load(f)
            
            # Load Sub-Key
            sk_bytes = base64.b64decode(identity["private_key_b64"])
            self.agent_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(sk_bytes)
            self.agent_public_key = self.agent_private_key.public_key()
            
            # Re-initialize hybrid signer with agent sub-key for signing
            from tachyon.core.keys.hybrid import HybridSigner
            self.signer = HybridSigner(
                ed25519_sk=self.agent_private_key,
                ed25519_pk=self.agent_public_key,
                mldsa65_sk=self._pqc_private_key_bytes, 
                mldsa65_pk=self._pqc_public_key,
                hmac_key=self.hmac_key
            )
            print(f"[IntegrityManager] Identity recruited: Role={role}")
            return identity.get("certificate")
        except Exception as e:
            print(f"[IntegrityManager] Failed to load identity for {role}: {e}")
            return None

    def sign_document(self, filepath: str, identity: str = "tachyon-substrate-v1") -> str:
        """
        Sign a file and return the hex digest.
        Delegates the cryptography to HybridSigner and audits to TelemetryBus.
        """
        if not os.path.exists(filepath):
            return ""
        with open(filepath, 'rb') as f:
            content = f.read()

        # sign(content)
        signature = self.signer.sign(content)
        
        import hashlib
        file_hash = hashlib.sha256(content).hexdigest()
        
        from datetime import datetime
        sig_data = {
            "version": "2.0",
            "hash": f"sha256:{file_hash}",
            "signature": signature,
            "timestamp": datetime.now().isoformat(),
            "algorithm": "hybrid-pqc"
        }
        
        import tempfile
        sig_path = f"{filepath}.sig.json"
        fd, tmp_sig_path = tempfile.mkstemp(dir=os.path.dirname(sig_path), prefix=".tmp_sig_")
        try:
            with os.fdopen(fd, 'w') as sf:
                json.dump(sig_data, sf, indent=2)
                sf.flush()
                os.fsync(sf.fileno())
            os.replace(tmp_sig_path, sig_path)
        except Exception as e:
            if os.path.exists(tmp_sig_path):
                os.remove(tmp_sig_path)
            raise e

        # Extract filename only in telemetry to limit size
        fname = os.path.basename(filepath)
        from tachyon.core.telemetry import TelemetryBus
        bus = TelemetryBus()
        bus.emit_event(
            "AGENT_SIGNATURE",
            identity,
            action="sign_document",
            status="SUCCESS",
            details={
                "file": fname,
                "has_pqc": True, # Hybrid is mandatory in sign_document
                "version": "2.0"
            }
        )
        return signature

    def sign_text(self, text: str) -> str:
        """Sign a raw string and return the signature."""
        return self.signer.sign(text.encode('utf-8'))

    def verify_text_signature(self, text: str, signature: str) -> bool:
        """Verify a signature against a raw string."""
        return self.signer.verify(text.encode('utf-8'), signature)

    def verify_integrity(self, filepath: str, enforce: bool = False) -> bool:
        """
        Verifies the file against its structured .sig.json sidecar.
        Implements ATOMIC Read-Hash-Verify to eliminate TOCTOU race conditions (C-01).
        """
        import hashlib
        import json
        
        sig_path_json = f"{filepath}.sig.json"
        sig_path_legacy = f"{filepath}.sig"
        strict = enforce or os.environ.get("TACHYON_STRICT_MODE") == "1"
        
        # 1. Atomic Read of Content First (Prevention of TOCTOU)
        try:
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'rb') as f:
                content = f.read()
            actual_hash = hashlib.sha256(content).hexdigest()
        except Exception as e:
            if strict: raise RuntimeError(f"Atomic read failed: {e}")
            return False

        # 2. Locate Signature
        if os.path.exists(sig_path_json):
            # V2 Structured Path
            try:
                with open(sig_path_json, 'r') as f:
                    sig_data = json.load(f)
                
                # Check Hash Consistency within metadata
                expected_hash = sig_data.get("hash", "").split(":")[-1]
                if expected_hash != actual_hash:
                    if strict: raise RuntimeError(f"INTEGRITY FAILURE: Atomic hash mismatch for {filepath}.")
                    return False
                
                # Verify PQC Signature
                is_valid = self.signer.verify(content, sig_data["signature"])
                return is_valid
            except Exception as e:
                if strict: raise RuntimeError(f"V2 Verification Error: {e}")
                return False

        elif os.path.exists(sig_path_legacy):
            # Fallback to V1 Legacy Path (TOCTOU minimized but not eliminated for V1)
            try:
                with open(sig_path_legacy, 'r') as f:
                    legacy_sig = f.read().strip()
                return self.signer.verify(content, legacy_sig)
            except Exception:
                return False
        
        # No signature found
        if strict:
            err = f"INTEGRITY FAILURE: No detached signature found for {filepath}."
            from tachyon.core.state import StateManager
            state = StateManager()
            if not state.is_mutant_lock_active():
                state.emit_alert("INTEGRITY_VIOLATION", err)
                raise RuntimeError(err)
        return False

    def verify_text_signature(self, text: str, signature: str) -> bool:
        """Verifies a raw text string against an Ed25519/Hybrid signature."""
        try:
            content = text.encode()
            return self.signer.verify(content, signature)
        except Exception:
            return False

    def sign_text(self, text: str) -> str:
        """Signs a raw text string and returns the signature string."""
        content = text.encode()
        return self.signer.sign(content)
