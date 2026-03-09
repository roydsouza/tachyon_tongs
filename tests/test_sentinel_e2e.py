import unittest
import os
from unittest.mock import patch
import sentinel

class TestSentinelE2E(unittest.TestCase):
    """
    End-to-End integration test for the Sentinel CLI.
    Ensures the sentinel can run autonomously without crashing,
    while isolating its logs to prevent spamming the production RUN_LOG.md.
    """
    def setUp(self):
        self.test_log_file = "test_e2e_log.md"
        # Ensure clean state before test
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def tearDown(self):
        # Clean up the test ledger to keep the repo tidy
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    @patch("sys.argv", ["sentinel.py", "--manual", "--log-file", "test_e2e_log.md"])
    def test_sentinel_runs_from_cli_without_fatal_errors(self):
        # When we run the main entry point
        sentinel.main()
        
        # Then the test log file should be created
        self.assertTrue(os.path.exists(self.test_log_file), "Sentinel failed to create the execution ledger.")
        
        # And it should not contain a CAUTION fatal error blocks
        with open(self.test_log_file, "r") as f:
            content = f.read()
            self.assertNotIn("[!CAUTION]", content, "Sentinel experienced a fatal crash during E2E testing.")
            self.assertIn("Trigger Source:** `MANUAL_CLI`", content)
            
    @patch("sys.argv", ["sentinel.py", "--manual", "--log-file", "test_e2e_log.md"])
    @patch("sentinel.run_sentinel")
    def test_sentinel_logs_fatal_errors_to_ledger(self, mock_run_sentinel):
        # Given a fatal error during the ADK run
        mock_run_sentinel.side_effect = Exception("Simulated ADK Core Meltdown")
        
        # When we run the main entry point
        sentinel.main()
        
        # Then the ledger should still be created
        self.assertTrue(os.path.exists(self.test_log_file))
        
        # And the ledger MUST capture the crash reason (The Breadcrumb check)
        with open(self.test_log_file, "r") as f:
            content = f.read()
            self.assertIn("[!CAUTION]", content)
            self.assertIn("Simulated ADK Core Meltdown", content)
