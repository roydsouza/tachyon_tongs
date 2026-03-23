import unittest
import os
import shutil
from agents._core.registry import AgentRegistry

class TestCanaryAgent(unittest.TestCase):
    def setUp(self):
        self.registry = AgentRegistry()
        self.registry.discover_plugins()
        self.plugin = self.registry.get_plugin("canary")
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.test_log = os.path.join(root_dir, "logs", "CANARY_LOG.md")
        # Reset log for testing
        if os.path.exists(self.test_log):
            os.remove(self.test_log)

    def test_scout_and_log(self):
        """Verify that the Canary agent scouts and logs correctly."""
        targets = [
            {"id": "TEST-BYPASS", "payload": "Normal-looking-payload"},
            {"id": "TEST-BLOCK", "payload": "[DEBUG] [REDACTED_JAILBREAK] malicious-intent"}
        ]
        
        result = self.plugin.execute_action("scout", {"targets": targets})
        
        # 1. Verify results structure
        self.assertIn("scout_results", result)
        results = result["scout_results"]
        self.assertEqual(len(results), 2)
        
        # 2. Verify statuses
        self.assertEqual(results[0]["status"], "BYPASSED")
        self.assertEqual(results[1]["status"], "BLOCKED")
        
        # 3. Verify logging
        self.assertTrue(os.path.exists(self.test_log))
        with open(self.test_log, "r") as f:
            content = f.read()
            self.assertIn("TEST-BYPASS | STATUS: BYPASSED", content)
            self.assertIn("TEST-BLOCK | STATUS: BLOCKED", content)

    def test_harvest(self):
        """Verify that forensics harvesting works."""
        # Create a dummy log to harvest
        os.makedirs(os.path.dirname(self.test_log), exist_ok=True)
        with open(self.test_log, "w") as f:
            f.write("Some dummy forensic data")
            
        result = self.plugin.execute_action("harvest", {})
        self.assertEqual(result["status"], "SUCCESS")
        self.assertIn("analysis", result)

if __name__ == "__main__":
    unittest.main()
