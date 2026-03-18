import unittest
import asyncio
import time
from typing import Dict, Any
from tachyon.enforcement.router import ToolRouter
from tachyon.enforcement.rate_limiter import AdaptiveRateLimiter

# Mock Objects for Testing
class MockOrchestrator:
    async def fetch_and_sanitize(self, url: str, agent_id: str):
        return {"status": "SUCCESS"}

class MockPolicyEngine:
    def is_action_allowed(self, agent_id: str, action: str, params: Dict[str, Any]) -> bool:
        return True

class MockMonitor:
    def log_and_evaluate(self, *args): pass

class TestRateLimiting(unittest.TestCase):
    def setUp(self):
        # Initialize Rate Limiter with a low threshold for easy testing (5 RPM)
        self.rate_limiter = AdaptiveRateLimiter(default_rpm=5)
        self.router = ToolRouter(
            orchestrator=MockOrchestrator(),
            sandbox=None,
            policy_engine=MockPolicyEngine(),
            cot_monitor=None,
            syscall_monitor=MockMonitor(),
            rate_limiter=self.rate_limiter
        )

    def test_rate_limiting_enforcement(self):
        """Verify that an agent is blocked after exceeding the RPM threshold."""
        agent_id = "looping_agent"
        action = "safe_fetch"
        params = {"url": "https://example.com"}

        # 1. First 5 requests should be allowed
        for i in range(5):
            result = asyncio.run(self.router.route(agent_id, action, params))
            self.assertEqual(result["status"], "SUCCESS", f"Request {i+1} should be allowed")

        # 2. 6th request should be blocked
        result = asyncio.run(self.router.route(agent_id, action, params))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("RATE_LIMIT_EXCEEDED", result["error"])

    def test_per_tool_isolation(self):
        """Verify that rate limits are tracked independently per tool."""
        agent_id = "multi_tool_agent"
        
        # Exhaust limits for 'safe_fetch'
        for _ in range(5):
            asyncio.run(self.router.route(agent_id, "safe_fetch", {}))
        
        # 'safe_fetch' should be blocked
        res_fetch = asyncio.run(self.router.route(agent_id, "safe_fetch", {}))
        self.assertEqual(res_fetch["status"], "BLOCKED")
        
        # 'safe_execute' should still be allowed
        res_exec = asyncio.run(self.router.route(agent_id, "safe_execute", {"command": "ls"}))
        self.assertNotEqual(res_exec["status"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
