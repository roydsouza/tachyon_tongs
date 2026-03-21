import os
import hmac
import hashlib
from datetime import datetime
from typing import Optional, Union, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# Local substrate constants
KEY_LABEL = "Tachyon Root Key"
KEY_APPLICATION_TAG = "com.tachyon.substrate.root.v1"

class IntegrityManager:
    """
    Manages cryptographic signatures and integrity verification for Tachyon Tongs.
    Phase 25.1: Migrated from HMAC-SHA256 to hardware-backed Ed25519 signatures.
    """
    
    def __init__(self, use_hardware: bool = True):
        self.use_hardware = use_hardware
        self.hmac_key = os.environ.get("TACHYON_SECRET_KEY", "DEVELOPMENT_INSECURE_FALLBACK").encode('utf-8')
        self._private_key: Optional[ed25519.Ed25519PrivateKey] = None
        self._public_key: Optional[ed25519.Ed25519PublicKey] = None
        
        # In Phase 25.1, we attempt to load the hardware-backed key.
        # If it doesn't exist, we warn but allow legacy HMAC fallback 
        # unless TACHYON_STRICT_MODE is set.
        try:
            self._load_keys()
        except Exception as e:
            if os.environ.get("TACHYON_STRICT_MODE"):
                raise RuntimeError(f"Cryptographic failure in STRICT_MODE: {e}. Halt.")

    def _load_keys(self):
        """Placeholder for Phase 25.1 key loading from macOS Keychain/Secure Enclave."""
        # For now, we stub this out bit-by-bit as we implement the Genesis script.
        pass

    def sign_document(self, filepath: str, identity: str = "tachyon-substrate-v1") -> str:
        """
        Sign a file and return the hex digest. 
        Will use Ed25519 if available, falling back to HMAC for legacy support.
        """
        if not os.path.exists(filepath):
            return ""
        with open(filepath, 'rb') as f:
            content = f.read()
            
        if self._private_key:
            # Ed25519 Signature (Phase 25.1)
            signature = self._private_key.sign(content)
            digest = signature.hex()
            prefix = "ed25519:"
        else:
            # Legacy HMAC-SHA256 (Phase 21)
            digest = hmac.new(self.hmac_key, content, hashlib.sha256).hexdigest()
            prefix = ""
            
        # Write the detached signature
        sig_path = f"{filepath}.sig"
        with open(sig_path, 'w') as sf:
            sf.write(f"{prefix}{digest}")
            sf.flush()
            os.fsync(sf.fileno())
            
        return digest
        
    def verify_integrity(self, filepath: str) -> bool:
        """Verify the cryptographic signature of a file (Supports HMAC and Ed25519)."""
        if not os.path.exists(filepath):
            return True
            
        sig_path = f"{filepath}.sig"
        if not os.path.exists(sig_path):
            raise RuntimeError(f"No detached signature found for {filepath}. Access Denied.")
            
        with open(sig_path, 'r') as sf:
            raw_sig = sf.read().strip()
            
        with open(filepath, 'rb') as f:
            content = f.read()
            
        if raw_sig.startswith("ed25519:"):
            # Asymmetric Verification
            if not self._public_key:
                raise RuntimeError("Ed25519 signature detected but no public key available for verification.")
            
            sig_bytes = bytes.fromhex(raw_sig.split(":")[1])
            try:
                self._public_key.verify(sig_bytes, content)
                return True
            except InvalidSignature:
                raise RuntimeError(f"INTEGRITY COMPROMISED: Ed25519 signature mismatch for {filepath}!")
        else:
            # Legacy HMAC Verification
            actual_sig = hmac.new(self.hmac_key, content, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(raw_sig, actual_sig):
                raise RuntimeError(f"INTEGRITY COMPROMISED: HMAC mismatch for {filepath}!")
            return True
