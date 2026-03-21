import unittest
import subprocess
import os
import sys

class TestCLIArgParsing(unittest.TestCase):
    """
    E2E regression tests for the 'tt' command argument parsing.
    Ensures that ceremonies and agent management commands are correctly routed.
    """

    def test_tt_help(self):
        """Test that 'tt --help' works and contains 'keys'."""
        # Use sys.executable -m to ensure we test the SAME environment we are running in
        result = subprocess.run([sys.executable, "-m", "tachyon.cli.main", "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("keys", result.stdout)
        self.assertIn("Manage cryptographic keys", result.stdout)

    def test_tt_keys_help(self):
        """Test that 'tt keys --help' contains genesis and recover."""
        result = subprocess.run([sys.executable, "-m", "tachyon.cli.main", "keys", "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("genesis", result.stdout)
        self.assertIn("recover", result.stdout)

    def test_tt_keys_import(self):
        """Regression: Verify that the keys subcommand can actually import its logic."""
        result = subprocess.run([sys.executable, "-m", "tachyon.cli.main", "keys", "genesis", "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Execute the Root Key Genesis Ceremony", result.stdout)

    def test_cmd_routing(self):
        """Verify that basic commands return correct help or status without erroring on flags."""
        result = subprocess.run([sys.executable, "-m", "tachyon.cli.main", "keys", "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("genesis", result.stdout)

if __name__ == "__main__":
    # We use subprocess directly to test the installed 'tt' entrypoint
    # Ensure tt is in path
    unittest.main()
