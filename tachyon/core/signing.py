import os
import hmac
import hashlib
from datetime import datetime

class IntegrityManager:
    """
    Manages cryptographic signatures and integrity verification for Tachyon Tongs.
    Ensures that critical files like EXPLOITATION_CATALOG.md have not been tampered with.
    """
    
    def __init__(self, secret_key: str = None):
        # Use provided key or fallback to environment/default
        # REQUIRED: TACHYON_SECRET_KEY must be in environment for high-assurance signing
        # We use a placeholder only for basic non-critical labeling
        self.secret_key = os.environ.get("TACHYON_SECRET_KEY", "DEVELOPMENT_INSECURE_FALLBACK").encode('utf-8')
        if self.secret_key == b"DEVELOPMENT_INSECURE_FALLBACK" and os.environ.get("TACHYON_STRICT_MODE"):
            raise RuntimeError("TACHYON_SECRET_KEY missing in STRICT_MODE. Halt.")

    def sign_document(self, filepath: str) -> str:
        """Sign a file and return the hex digest. We store this in a parallel .sig file."""
        if not os.path.exists(filepath):
            return ""
        with open(filepath, 'rb') as f:
            content = f.read()
            
        digest = hmac.new(self.secret_key, content, hashlib.sha256).hexdigest()
        
        # Write the detached signature
        sig_path = f"{filepath}.sig"
        with open(sig_path, 'w') as sf:
            sf.write(digest)
            
        return digest
        
    def verify_integrity(self, filepath: str) -> bool:
        """Verify the cryptographic signature of a file."""
        if not os.path.exists(filepath):
            return True  # Brand new organism, nothing to verify
            
        sig_path = f"{filepath}.sig"
        if not os.path.exists(sig_path):
            raise RuntimeError(f"INTEGRITY FAILURE: No detached signature found for {filepath}. Access Denied.")
            
        with open(sig_path, 'r') as sf:
            expected_sig = sf.read().strip()
            
        with open(filepath, 'rb') as f:
            content = f.read()
            
        actual_sig = hmac.new(self.secret_key, content, hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise RuntimeError(f"INTEGRITY COMPROMISED: {filepath} was modified out-of-band! Halt.")
        
        return True
