import unittest
import os
import tempfile
from tachyon.core.signing import IntegrityManager
from cryptography.hazmat.primitives.asymmetric import ed25519

class TestEd25519Signing(unittest.TestCase):
    """
    Regression tests for Phase 25.1 Ed25519 asymmetric signatures.
    """

    def setUp(self):
        # Initialize IntegrityManager without hardware for testing
        self.manager = IntegrityManager(use_hardware=False)
        # Create a dummy keypair for testing
        self.manager._private_key = ed25519.Ed25519PrivateKey.generate()
        self.manager._public_key = self.manager._private_key.public_key()

    def test_sign_and_verify_ed25519(self):
        """Test the full signing/verification cycle for Ed25519."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"SECRET_DATA_CONTENT")
            tmp_path = tmp.name
            
        try:
            # Sign
            sig = self.manager.sign_document(tmp_path)
            self.assertIsNotNone(sig)
            
            # Verify
            self.assertTrue(self.manager.verify_integrity(tmp_path))
            
            # Tamper
            with open(tmp_path, 'ab') as f:
                f.write(b"TAMPERED")
                
            with self.assertRaises(RuntimeError) as cm:
                self.manager.verify_integrity(tmp_path)
            self.assertIn("INTEGRITY COMPROMISED", str(cm.exception))
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if os.path.exists(tmp_path + ".sig"):
                os.remove(tmp_path + ".sig")

    def test_legacy_hmac_fallback(self):
        """Test that the manager can still verify legacy HMAC signatures."""
        # Force the manager into HMAC mode by clearing keys
        self.manager._private_key = None
        self.manager._public_key = None
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"LEGACY_HMAC_DATA")
            tmp_path = tmp.name
            
        try:
            # This should produce a legacy (no prefix) signature
            sig = self.manager.sign_document(tmp_path)
            self.assertFalse(sig.startswith("ed25519:"))
            
            # Verify should work
            self.assertTrue(self.manager.verify_integrity(tmp_path))
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if os.path.exists(tmp_path + ".sig"):
                os.remove(tmp_path + ".sig")

if __name__ == "__main__":
    unittest.main()
