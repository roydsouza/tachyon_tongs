import unittest
import os
from src.execution_logger import ExecutionLogger

class TestSentinelTransparency(unittest.TestCase):
    def setUp(self):
        self.test_log = "TEST_RUN_LOG.md"
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def test_granular_site_and_file_logging(self):
        logger = ExecutionLogger(log_file=self.test_log)
        logger.start_run()
        
        # Test site result formatting (Discoverer / Ingester)
        logger.add_site_result("nvd.nist.gov", status="SUCCESS", signals=2)
        logger.add_site_result("evil.com", status="FAIL", error="Connection Timeout")
        
        # Test granular file modification formatting (Engineer)
        logger.add_file_updated("EXPLOITATION_CATALOG.md", details="Appended GHSA-1234")
        logger.add_file_updated("SITES.md", details="Autodiscovered Google Project Zero")
        logger.add_file_updated("SITES.md", details="Autodiscovered DeepMind Blog")
        
        logger.finalize_run()
        
        with open(self.test_log, "r") as f:
            content = f.read()
            
        # Assertions
        self.assertIn("✅ `nvd.nist.gov` (2 signals)", content)
        self.assertIn("❌ `evil.com` (0 signals) - *Error: Connection Timeout*", content)
        self.assertIn("- Files Modified:", content)
        self.assertIn("  - `EXPLOITATION_CATALOG.md`", content)
        self.assertIn("    - Appended GHSA-1234", content)
        self.assertIn("  - `SITES.md`", content)
        self.assertIn("    - Autodiscovered Google Project Zero", content)
        self.assertIn("    - Autodiscovered DeepMind Blog", content)

    def test_legacy_file_logging(self):
        # Ensure it doesn't break if details aren't provided
        logger = ExecutionLogger(log_file=self.test_log)
        logger.start_run()
        logger.add_file_updated("TASKS.md")
        logger.finalize_run()
        
        with open(self.test_log, "r") as f:
            content = f.read()
            
        self.assertIn("  - `TASKS.md`", content)

if __name__ == '__main__':
    unittest.main()
