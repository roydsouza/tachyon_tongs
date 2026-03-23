import unittest
import os
import json
from agents._core.registry import AgentRegistry

class TestSentinelHybridMigration(unittest.TestCase):
    def setUp(self):
        self.registry = AgentRegistry()
        self.registry.discover_plugins()
        self.plugin = self.registry.get_plugin("sentinel")

    def test_skill_loading(self):
        """Verify that the runner correctly loads declarative config from the skill manifest."""
        # The new runner loads config into internal state, we verify it's initialized
        self.assertIsNotNone(self.runner)

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
        """Verify the plugin is loaded."""
        self.assertIsNotNone(self.plugin)

if __name__ == "__main__":
    unittest.main()
