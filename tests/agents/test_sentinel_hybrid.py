import unittest
import os
import json
from tachyon.agents.sentinel.runner import SentinelRunner

class TestSentinelHybridMigration(unittest.TestCase):
    def setUp(self):
        self.skill_path = "agents/sentinel/SKILL.md"
        self.runner = SentinelRunner(skill_path=self.skill_path)

    def test_skill_loading(self):
        """Verify that the runner correctly loads declarative config from the skill manifest."""
        config = self.runner.config
        self.assertIn("harvest_mode", config)
        self.assertIn("keywords", config)
        self.assertTrue(isinstance(config["keywords"], list))
        self.assertEqual(config["harvest_mode"], True)

    def test_node_registration(self):
        """Verify that the Sentinel is correctly registered in the substrate node registry."""
        registry_path = "/tmp/tachyon/nodes.json"
        self.assertTrue(os.path.exists(registry_path), "Registry file missing")
        
        with open(registry_path, "r") as f:
            nodes = json.load(f)
            
        sentinel_node = next((n for n in nodes if n["agent_id"] == "sentinel-v1"), None)
        self.assertIsNotNone(sentinel_node)
        self.assertEqual(sentinel_node["type"], "sentinel")
        self.assertEqual(sentinel_node["skill_path"], "agents/sentinel/SKILL.md")

    def test_runner_initialization(self):
        """Verify the runner can be initialized without errors."""
        self.assertIsNotNone(self.runner)
        self.assertTrue(hasattr(self.runner, "run_sweep"))

if __name__ == "__main__":
    unittest.main()
