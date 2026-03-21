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

    def test_direct_api_instantiation(self):
        """Regression: Verify the cryptography API for Ed25519 is correctly called."""
        # This catches the from_seed vs from_private_bytes failure
        seed = os.urandom(32)
        try:
            priv = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
            self.assertIsNotNone(priv.public_key())
        except AttributeError as e:
            self.fail(f"Cryptography API failure: {e}")

if __name__ == "__main__":
    unittest.main()
