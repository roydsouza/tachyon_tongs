import unittest
import subprocess
import os

class TestCLIArgParsing(unittest.TestCase):
    """
    E2E regression tests for the 'tt' command argument parsing.
    Ensures that ceremonies and agent management commands are correctly routed.
    """

    def test_tt_help(self):
        """Test that 'tt --help' works and contains 'keys'."""
        result = subprocess.run(["tt", "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("keys", result.stdout)
        self.assertIn("Manage cryptographic keys", result.stdout)

    def test_tt_keys_help(self):
        """Test that 'tt keys --help' contains genesis and recover."""
        result = subprocess.run(["tt", "keys", "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("genesis", result.stdout)
        self.assertIn("recover", result.stdout)

    def test_cmd_routing(self):
        """Verify that basic commands return correct help or status without erroring on flags."""
        # Testing Typer-style commands (use --help to get 0 exit code for groups)
        result = subprocess.run(["tt", "keys", "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("genesis", result.stdout)

if __name__ == "__main__":
    # We use subprocess directly to test the installed 'tt' entrypoint
    # Ensure tt is in path
    unittest.main()
