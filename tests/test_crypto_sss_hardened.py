import unittest
import secrets
from tachyon.core.sss import split_secret, reconstruct_secret, P

class TestSSSBulletproof(unittest.TestCase):
    """
    Ultra-rigorous unit tests for Shamir's Secret Sharing over the secp256k1 prime field.
    Ensures mathematical perfection for high-assurance recovery.
    """

    def test_prime_field_boundaries(self):
        """Verify that secrets near the edge of the prime field work correctly."""
        # 0 is the lowest value
        secret_low = (0).to_bytes(32, 'big')
        shares = split_secret(secret_low, 3, 5)
        self.assertEqual(reconstruct_secret(shares[:3]), secret_low)

        # P-1 is the highest valid value
        secret_high = (P - 1).to_bytes(32, 'big')
        shares = split_secret(secret_high, 3, 5)
        self.assertEqual(reconstruct_secret(shares[:3]), secret_high)

    def test_invalid_secrets(self):
        """Verify that secrets > P are rejected to prevent field overflow."""
        invalid_secret = (P + 1).to_bytes(32, 'big')
        with self.assertRaises(ValueError):
            split_secret(invalid_secret, 3, 5)

    def test_all_threshold_combinations(self):
        """Test every possible k-of-n combination for small n to ensure polynomial coverage."""
        secret = secrets.token_bytes(32)
        for n in range(2, 6):
            for k in range(1, n + 1):
                shares = split_secret(secret, k, n)
                # Any combination of size k should work
                import itertools
                for subset in itertools.combinations(shares, k):
                    self.assertEqual(reconstruct_secret(list(subset)), secret)

    def test_reconstruction_independence(self):
        """Verify that reconstruction is independent of share order."""
        secret = secrets.token_bytes(32)
        shares = split_secret(secret, 3, 5)
        subset = shares[:3]
        
        # Original order
        self.assertEqual(reconstruct_secret(subset), secret)
        # Reversed order
        self.assertEqual(reconstruct_secret(subset[::-1]), secret)
        # Shuffled
        import random
        random.shuffle(subset)
        self.assertEqual(reconstruct_secret(subset), secret)

    def test_duplicate_shares(self):
        """Verify that providing the same share twice does not count towards the threshold."""
        secret = secrets.token_bytes(32)
        shares = split_secret(secret, 3, 5)
        
        # 2 distinct shares + 1 duplicate = 2 total info
        invalid_subset = [shares[0], shares[1], shares[0]]
        # The math will successfully complete, but (usually) return WRONG data
        reconstructed = reconstruct_secret(invalid_subset)
        self.assertNotEqual(reconstructed, secret)

if __name__ == "__main__":
    unittest.main()
