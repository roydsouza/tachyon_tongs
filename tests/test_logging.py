import unittest
import os
from src.execution_logger import ExecutionLogger

class TestLoggingIntegration(unittest.TestCase):

    def setUp(self):
        self.test_log_file = "TEST_RUN_LOG.md"
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def tearDown(self):
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def test_execution_logger_creates_file_and_header(self):
        logger = ExecutionLogger(log_file=self.test_log_file)
        # File is created on finalize, not init
        logger.start_run(trigger="INIT_TEST")
        logger.finalize_run()
        
        self.assertTrue(os.path.exists(self.test_log_file))
        with open(self.test_log_file, "r") as f:
            content = f.read()
        self.assertIn("# 📜 Tachyon Tongs: Sentinel Execution Ledger", content)

    def test_execution_logger_appends_run_data(self):
        logger = ExecutionLogger(log_file=self.test_log_file)
        
        logger.start_run(trigger="MANUAL_TEST")
        logger.add_site_result("github.com", status="SUCCESS", signals=1)
        logger.add_threat_found()
        logger.add_file_updated("TASKS.md", details="Injected 1 task")
        logger.finalize_run()
        
        with open(self.test_log_file, "r") as f:
            content = f.read()
        self.assertIn("Trigger Source: `MANUAL_TEST`", content)
        self.assertIn("✅ `github.com` (1 signals)", content)
        self.assertIn("Threats Identified: 1", content)
        self.assertIn("- Files Modified:\n  - `TASKS.md`\n    - Injected 1 task", content)

if __name__ == '__main__':
    unittest.main()
