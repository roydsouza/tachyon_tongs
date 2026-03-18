import unittest
import asyncio
from typing import Dict, Any
from tachyon.enforcement.router import ToolRouter
from tachyon.enforcement.alignment_checker import AlignmentChecker

# Mock Objects for Testing
class MockOrchestrator:
    async def fetch_and_sanitize(self, url: str, agent_id: str):
        return {"status": "SUCCESS"}

class MockPolicyEngine:
    def is_action_allowed(self, agent_id: str, action: str, params: Dict[str, Any]) -> bool:
        return True

class MockMonitor:
    def log_and_evaluate(self, *args): pass

class TestAlignmentDrift(unittest.TestCase):
    def setUp(self):
        self.router = ToolRouter(
            orchestrator=MockOrchestrator(),
            sandbox=None,
            policy_engine=MockPolicyEngine(),
            cot_monitor=None,
            syscall_monitor=MockMonitor()
        )

    def test_aligned_intent(self):
        """Verify that a technical action matching the intent is allowed."""
        params = {
            "intent": "Search for documentation on python asyncio",
            "url": "https://docs.python.org/3/library/asyncio.html"
        }
        result = asyncio.run(self.router.route("agent_1", "safe_fetch", params))
        self.assertEqual(result["status"], "SUCCESS")

    def test_misaligned_intent_drift(self):
        """Verify that technical actions deviating from intent are blocked."""
        params = {
            "intent": "Fetching documentation for the project",
            "url": "https://internal.vault/service_account_keys.json"
        }
        result = asyncio.run(self.router.route("agent_1", "safe_fetch", params))
        if result["status"] == "SUCCESS":
            # Manual check to see why it passed
            alignment = self.router.alignment_checker.check_alignment(params["intent"], params)
            print(f"DEBUG: Misaligned test passed with score: {alignment['score']} (reason: {alignment['reason']})")
        
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("Alignment Violation", result["error"])
        self.assertIn("Semantic Drift Detected", result["error"])

    def test_missing_intent_bypass(self):
        """Verify that actions without an intent field bypass the alignment check (Legacy support)."""
        params = {
            "url": "https://anywhere.com"
        }
        result = asyncio.run(self.router.route("agent_1", "safe_fetch", params))
        self.assertEqual(result["status"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()
