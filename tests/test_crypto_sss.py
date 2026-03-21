import unittest
import secrets
from tachyon.core.sss import split_secret, reconstruct_secret

class TestShamirSecretSharing(unittest.TestCase):
    """
    Regression tests for Shamir's Secret Sharing (SSS) implementation.
    Ensures that root key recovery is mathematically bulletproof.
    """

    def test_basic_reconstruction(self):
        """Test simple split and reconstruct with exact threshold."""
        # The new implementation requires exactly 32-byte secrets
        secret = b"TACHYON_ROOT_SEED_2026_TEST_SEED" 
        self.assertEqual(len(secret), 32)
        
        threshold = 3
        total = 5
        
        shares = split_secret(secret, threshold, total)
        self.assertEqual(len(shares), total)
        
        # Use first 3 shares
        reconstructed = reconstruct_secret(shares[:3])
        self.assertEqual(reconstructed, secret)
        
        # Use last 3 shares
        reconstructed = reconstruct_secret(shares[2:])
        self.assertEqual(reconstructed, secret)
        
        # Use shuffled 3 shares
        subset = [shares[0], shares[2], shares[4]]
        reconstructed = reconstruct_secret(subset)
        self.assertEqual(reconstructed, secret)

    def test_insufficient_shares(self):
        """Test that reconstruction fails (produces wrong data) with < threshold shares."""
        secret = secrets.token_bytes(32)
        threshold = 3
        total = 5
        
        shares = split_secret(secret, threshold, total)
        
        # SSS guarantees that with < threshold, you get 0 info.
        reconstructed = reconstruct_secret(shares[:2])
        self.assertNotEqual(reconstructed, secret)

    def test_binary_blobs(self):
        """Test recovery of random binary data (e.g. Ed25519 seeds)."""
        for _ in range(10):
            secret = secrets.token_bytes(32)
            shares = split_secret(secret, 3, 5)
            self.assertEqual(reconstruct_secret(shares[:3]), secret)

if __name__ == "__main__":
    unittest.main()
