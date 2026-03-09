import unittest
import os
from src.execution_logger import ExecutionLogger

class TestLoggerManagement(unittest.TestCase):
    def setUp(self):
        self.test_log = "TEST_RUN_LOG.md"
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def test_log_prepending_and_limiting(self):
        # Create a logger with a small limit for testing
        logger = ExecutionLogger(log_file=self.test_log, limit=5)
        
        # Run 10 times
        for i in range(10):
            logger.start_run(trigger=f"RUN_{i}")
            logger.finalize_run()
            
        with open(self.test_log, "r") as f:
            content = f.read()
            
        # Verify most recent is at the top (after header)
        self.assertIn("Trigger Source: `RUN_9`", content.split("## Run:")[1])
        
        # Verify limit of 5 runs (plus header)
        run_count = content.count("## Run:")
        self.assertEqual(run_count, 5)
