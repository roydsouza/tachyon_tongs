import unittest
import os
from src.execution_logger import ExecutionLogger

class TestLoggingIntegration(unittest.TestCase):

    def setUp(self):
        self.test_log_file = "TEST_RUN_LOG.md"
        # Ensure fresh start
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def tearDown(self):
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def test_execution_logger_creates_file_and_header(self):
        logger = ExecutionLogger(log_file=self.test_log_file)
        self.assertTrue(os.path.exists(self.test_log_file))
        
        with open(self.test_log_file, "r") as f:
            content = f.read()
            self.assertIn("# 📜 Tachyon Tongs: Sentinel Execution Ledger", content)

    def test_execution_logger_appends_run_data(self):
        logger = ExecutionLogger(log_file=self.test_log_file)
        
        logger.start_run(trigger_type="MANUAL_TEST")
        logger.add_site_polled("github.com")
        logger.add_threat_found()
        logger.add_file_updated("TASKS.md")
        logger.finalize_run()
        
        with open(self.test_log_file, "r") as f:
            content = f.read()
            self.assertIn("Trigger Source:** `MANUAL_TEST`", content)
            self.assertIn("Sites Polled:** github.com", content)
            self.assertIn("Threats Identified:** 1", content)
            self.assertIn("Files Modified:** TASKS.md", content)

if __name__ == '__main__':
    unittest.main()
