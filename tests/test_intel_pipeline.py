import unittest
import asyncio
import os
import json
import shutil
from scripts.intel_ingest import IntelIngestor, IntelSource
from src.execution_logger import ExecutionLogger

class TestIntelPipeline(unittest.TestCase):
    def setUp(self):
        self.test_log = "test_run_log.md"
        self.test_gt = "test_verified_traffic.json"
        self.logger = ExecutionLogger(agent_id="TestAgent", log_file=self.test_log)
        
    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)
        if os.path.exists(self.test_gt):
            os.remove(self.test_gt)

    def test_logger_site_results(self):
        """Verify that ExecutionLogger correctly stores and formats site results."""
        self.logger.start_run(trigger="TEST")
        self.logger.add_site_result("http://onesignal.com", status="SUCCESS", signals=5)
        self.logger.add_site_result("http://fail.com", status="FAIL", signals=0, error="404 Not Found")
        
        self.logger.finalize_run()
        
        with open(self.test_log, "r") as f:
            entry = f.read()

        self.assertIn("✅ `http://onesignal.com` (5 signals)", entry)
        self.assertIn("❌ `http://fail.com` (0 signals) - *Error: 404 Not Found*", entry)
        self.assertIn("Sites Audited:", entry)

    def test_ingestor_run_all(self):
        """Verify that IntelIngestor correctly orchestrates sources and logs results."""
        class MockSource(IntelSource):
            def name(self): return "Good-Source"
            async def fetch_threats(self): return [{"id": "THREAT-1"}]

        class BadSource(IntelSource):
            def name(self): return "Bad-Source"
            async def fetch_threats(self): raise ValueError("Source exploded")

        ingestor = IntelIngestor(logger_instance=self.logger)
        ingestor.register_source(MockSource())
        ingestor.register_source(BadSource())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        threats = loop.run_until_complete(ingestor.run_all())

        self.assertEqual(len(threats), 1)
        self.assertEqual(threats[0]["id"], "THREAT-1")
        
        # Verify logger state
        self.assertEqual(self.logger.run_data["site_results"]["intel://Good-Source"]["status"], "SUCCESS")
        self.assertEqual(self.logger.run_data["site_results"]["intel://Bad-Source"]["status"], "FAIL")
        self.assertEqual(self.logger.run_data["site_results"]["intel://Bad-Source"]["error"], "Source exploded")

    def test_logger_finalization_with_prepending(self):
        """Verify that RUN_LOG.md prepending and limiting works as expected."""
        # Start a run and finalize it
        self.logger.start_run(trigger="RUN_1")
        self.logger.finalize_run()
        
        with open(self.test_log, "r") as f:
            content = f.read()
            self.assertIn("Trigger Source: `RUN_1`", content)

        # Start a second run
        self.logger.start_run(trigger="RUN_2")
        self.logger.finalize_run()
        
        with open(self.test_log, "r") as f:
            content = f.read()
            # RUN_2 should be before RUN_1
            pos2 = content.find("RUN_2")
            pos1 = content.find("RUN_1")
            self.assertTrue(pos2 < pos1)

if __name__ == "__main__":
    unittest.main()
