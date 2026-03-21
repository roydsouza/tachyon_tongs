import unittest
import secrets
from tachyon.core.sss import split_secret, reconstruct_secret

class TestSSSRegression(unittest.TestCase):
    """
    Regression tests for Shamir's Secret Sharing in Phase 25.3.
    Ensures that generalized SSS works for both legacy (32B) and PQC (64B) secrets.
    """
    
    def test_legacy_32byte_secret(self):
        """Verify that 32-byte (ECC) secrets still work perfectly."""
        secret = secrets.token_bytes(32)
        shares = split_secret(secret, threshold=3, total_shares=5)
        self.assertEqual(len(shares), 5)
        
        # Reconstruct from 3 shares
        reconstructed = reconstruct_secret(shares[:3])
        self.assertEqual(secret, reconstructed)

    def test_pqc_64byte_secret(self):
        """Verify that 64-byte (PQC) secrets are correctly chunked and reconstructed."""
        secret = secrets.token_bytes(64)
        shares = split_secret(secret, threshold=3, total_shares=5)
        self.assertEqual(len(shares), 5)
        
        # Reconstruct from 3 shares
        reconstructed = reconstruct_secret(shares[2:])
        self.assertEqual(secret, reconstructed)

    def test_arbitrary_length_secret(self):
        """Verify that any length (e.g., 100 bytes) works."""
        secret = secrets.token_bytes(100)
        shares = split_secret(secret, threshold=3, total_shares=5)
        
        # Threshold: 3
        subset = [shares[0], shares[2], shares[4]]
        reconstructed = reconstruct_secret(subset)
        self.assertEqual(secret, reconstructed)

    def test_insufficient_shares(self):
        """Verify that 2 shares fail to reconstruct a 3-threshold secret."""
        secret = secrets.token_bytes(32)
        shares = split_secret(secret, threshold=3, total_shares=5)
        
        # This SHOULD fail to produce the correct secret
        reconstructed = reconstruct_secret(shares[:2])
        self.assertNotEqual(secret, reconstructed)

if __name__ == '__main__':
    unittest.main()
