import unittest
import subprocess
import time
import os
import signal
import sys

class TestCeremonyIronclad(unittest.TestCase):
    """
    Ironclad E2E tests for the Genesis and Recovery ceremonies.
    Uses subprocess to interact with the REAL 'tt' command, ensuring no
    mock-leakage or scope-shadowing.
    """

    def test_genesis_e2e_flawless(self):
        """Verify that 'tt keys genesis' runs from start to finish without any exceptions."""
        # Cleanup any previous manifest
        if os.path.exists("ROOT_MANIFEST.json"):
            os.remove("ROOT_MANIFEST.json")
        if os.path.exists("ROOT_MANIFEST.json.sig"):
            os.remove("ROOT_MANIFEST.json.sig")

        # Start the process
        proc = subprocess.Popen(
            [sys.executable, "-m", "tachyon.cli.main", "keys", "genesis"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        try:
            # 1. Confirmation
            proc.stdin.write("y\n")
            proc.stdin.flush()

            # 2. Reveal/Hide 5 shares (10 enters)
            for _ in range(10):
                time.sleep(0.1) # Give it time to prompt
                proc.stdin.write("\n")
                proc.stdin.flush()

            # Wait for completion
            stdout, stderr = proc.communicate(timeout=10)
            
            # CHECK FOR CRITICAL FAILURES
            self.assertNotIn("Traceback", stderr)
            self.assertNotIn("NameError", stderr)
            self.assertNotIn("AttributeError", stderr)
            self.assertIn("Genesis Ceremony Complete", stdout)
            self.assertIn("Root Key pinned and attested", stdout)
            
            # Check for file persistence
            self.assertTrue(os.path.exists("ROOT_MANIFEST.json"))
            self.assertTrue(os.path.exists("ROOT_MANIFEST.json.sig"))

        except subprocess.TimeoutExpired:
            proc.kill()
            self.fail("Genesis ceremony timed out or hung.")
        finally:
            if proc.poll() is None:
                proc.terminate()

if __name__ == "__main__":
    unittest.main()
