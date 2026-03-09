import unittest
import os
import subprocess
import time

class TestSentinelE2E(unittest.TestCase):
    """
    End-to-End integration tests for the Sentinel CLI.
    Ensures the Triad Supervisor and the Logger work in harmony.
    """
    
    def setUp(self):
        self.test_log = "test_e2e_log.md"
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def test_sentinel_runs_from_cli_without_fatal_errors(self):
        # Trigger the sentinel via CLI manually
        result = subprocess.run(
            ["python3", "sentinel.py", "--manual", "--log-file", self.test_log],
            capture_output=True,
            text=True
        )
        
        # Should exit cleanly
        self.assertEqual(result.returncode, 0, f"CLI execution failed: {result.stderr}")
        self.assertIn("Run finalized.", result.stdout)
        
        # Verify log exists and has the correct multi-agent content
        self.assertTrue(os.path.exists(self.test_log))
        with open(self.test_log, "r") as f:
            content = f.read()
            
        self.assertIn("Trigger Source: `MANUAL_CLI`", content)
        self.assertIn("Sites Polled: https://github.com/advisories", content)

    def test_sentinel_prepending_works(self):
        # Run once
        subprocess.run(["python3", "sentinel.py", "--manual", "--log-file", self.test_log])
        time.sleep(1.1)
        # Run again with a different source
        subprocess.run(["python3", "sentinel.py", "--cron", "--log-file", self.test_log])
        
        with open(self.test_log, "r") as f:
            lines = f.readlines()
            
        # Find the indices of the runs
        run_indices = [i for i, line in enumerate(lines) if "## Run:" in line]
        self.assertEqual(len(run_indices), 2)
        
        # The first run in the file should be the most recent one (cron)
        recent_run_header_idx = run_indices[0]
        # Check the trigger source in the block immediately following the first header
        run_content = "".join(lines[recent_run_header_idx : run_indices[1]])
        self.assertIn("Trigger Source: `CRON_SCHEDULED`", run_content)

if __name__ == "__main__":
    unittest.main()
