import unittest
from agents._core.base import BaseAgentPlugin
from typing import Dict, Any

class MockQuarantinedPlugin(BaseAgentPlugin):
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if self.quarantine_mode and action not in ["safe_fetch", "read_file"]:
             return {"status": "BLOCKED", "reason": "Quarantine Restriction"}
        return {"status": "SUCCESS"}

class TestQuarantineGating(unittest.TestCase):
    def test_quarantine_blocks_unsafe_action(self):
        config = {"quarantine_mode": True, "graduated": False}
        plugin = MockQuarantinedPlugin("test-1", "mock", config)
        
        result = plugin.execute_action("delete_file", {})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(plugin.quarantine_mode)

    def test_quarantine_allows_safe_action(self):
        config = {"quarantine_mode": True, "graduated": False}
        plugin = MockQuarantinedPlugin("test-1", "mock", config)
        
        result = plugin.execute_action("safe_fetch", {"url": "example.com"})
        self.assertEqual(result["status"], "SUCCESS")

    def test_graduated_agent_allows_all(self):
        config = {"quarantine_mode": False, "graduated": True}
        plugin = MockQuarantinedPlugin("test-1", "mock", config)
        
        result = plugin.execute_action("delete_file", {})
        self.assertEqual(result["status"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()
