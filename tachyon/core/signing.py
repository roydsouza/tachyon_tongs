import os
import hmac
import hashlib
import warnings
from datetime import datetime
from typing import Optional, Union, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# Phase 25.3: Suppress liboqs version mismatch (Using 0.15.0-dev on M5)
warnings.filterwarnings("ignore", category=UserWarning, module="oqs")

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
        Derives a per-agent Ed25519 key from the Root Key and issue a 
        Hybrid-Signed Delegation Certificate binding it to the role.
        
        Returns: Tuple of (ed25519.Ed25519PrivateKey, dict[Certificate])
        """
        if not self._private_key:
            raise RuntimeError("Cannot derive agent key without a loaded Root Key.")
            
        from tachyon.core.keys.certificates import DelegationCertificateAuthority
        ca = DelegationCertificateAuthority(self)
        return ca.derive_and_issue(role=role, expiry_days=30, save_to_disk=save_to_disk)

    def load_agent_identity(self, role: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to load a delegated identity (Key + Cert) from disk.
        If successful, re-initializes the signer to use the agent's sub-key.
        """
        import json
        import base64
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        keys_dir = os.path.join(root_dir, "memory", "keys")
        path = os.path.join(keys_dir, f"agent_{role.lower()}.json")
        
        if not os.path.exists(path):
             return None
             
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

        # Delegate cryptography to the pure computational layer
        final_digest = self.signer.sign(content)
        
        sig_path = f"{filepath}.sig"
        with open(sig_path, 'w') as sf:
            sf.write(final_digest)
            sf.flush()
            os.fsync(sf.fileno())

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
                "has_pqc": bool(self._pqc_private_key_bytes),
                "has_ed25519": bool(self._private_key),
                "hybrid": (bool(self._pqc_private_key_bytes) and bool(self._private_key))
            }
        )
        return final_digest
    def sign_text(self, text: str) -> str:
        """Sign a raw string and return the signature."""
        return self.signer.sign(text.encode('utf-8'))

    def verify_text_signature(self, text: str, signature: str) -> bool:
        """Verify a signature against a raw string."""
        return self.signer.verify(text.encode('utf-8'), signature)

    def verify_integrity(self, filepath: str, enforce: bool = False) -> bool:
        """
        Verifies the file against its .sig sidecar.
        Implements a 3-stage retry loop to resolve PQC/Guardian race conditions.
        """
        import time
        sig_path = f"{filepath}.sig"
        strict = enforce or os.environ.get("TACHYON_STRICT_MODE") == "1"
        
        # 3-Stage Retry Loop (Total ~150ms buffer)
        for attempt in range(3):
            if os.path.exists(sig_path):
                break
            if attempt < 2:
                time.sleep(0.05 * (attempt + 1)) # 50ms, then 100ms
            else:
                # Final fail
                if strict:
                    err = f"INTEGRITY FAILURE: No detached signature found for mission-critical file: {filepath}. This change is UNTRUSTED."
                    from tachyon.core.state import StateManager
                    state = StateManager()
                    if not state.is_mutant_lock_active():
                        state.emit_alert("INTEGRITY_VIOLATION", err)
                        raise RuntimeError(err)
                    else:
                        return False # Suppressed due to lock
                return False

        # Attempt verification with retry for content-flush race
        for attempt in range(2):
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                with open(sig_path, 'r') as sf:
                    detached_sig = sf.read().strip()

                is_valid = self.signer.verify(content, detached_sig)
                if is_valid:
                    return True
                
                if attempt == 0:
                    time.sleep(0.05) # Brief pause and retry once
                    continue
                    
                # Final invalid verdit
                if strict:
                    err = f"INTEGRITY FAILURE: Signature mismatch for {filepath}. File has been tampered with or ritual was incomplete."
                    from tachyon.core.state import StateManager
                    state = StateManager()
                    if not state.is_mutant_lock_active():
                        state.emit_alert("SIGNATURE_MISMATCH", err)
                        raise RuntimeError(err)
                return False

            except Exception as e:
                if attempt == 0:
                    time.sleep(0.05)
                    continue
                if strict:
                    error_msg = str(e)
                    alert_type = "CRYPTO_ERROR"
                    if "Strip Attack" in error_msg:
                        alert_type = "INTEGRITY_VIOLATION"
                    
                    err = f"INTEGRITY FAILURE: Cryptographic error during verification of {filepath}: {e}"
                    from tachyon.core.state import StateManager
                    state = StateManager()
                    if not state.is_mutant_lock_active():
                        state.emit_alert(alert_type, err)
                        raise RuntimeError(err)
                return False
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
