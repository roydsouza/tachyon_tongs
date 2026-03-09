import unittest
import time
from src.capability_token import CapabilityToken
from src.intent_scoring import ContextualIntentGate, IntentContext
from src.adk_sentinel import run_supervisor

class TestAdvancedProtections(unittest.TestCase):

    # --- Capability Token (Decay) Tests ---
    def test_token_decay_initial_state(self):
        token = CapabilityToken("t_123", ["admin", "write", "read"], t_decay_seconds=900)
        # At T=0, should have all rights
        self.assertTrue(token.authorize("admin", current_time=token.created_at))
        self.assertTrue(token.authorize("read", current_time=token.created_at))

    def test_token_decay_after_one_interval(self):
        token = CapabilityToken("t_123", ["admin", "write", "read"], t_decay_seconds=900)
        # Advance clock by 901 seconds (1 interval passed)
        future_time = token.created_at + 901
        
        # 'admin' (highest risk, index 0) should be revoked
        self.assertFalse(token.authorize("admin", current_time=future_time))
        # 'write' and 'read' should remain
        self.assertTrue(token.authorize("write", current_time=future_time))

    def test_token_decay_after_max_intervals(self):
        token = CapabilityToken("t_123", ["admin", "write", "read"], t_decay_seconds=900)
        # Advance clock by 3 intervals (2700+ seconds)
        future_time = token.created_at + 2800
        
        # Token is functionally dead
        self.assertFalse(token.authorize("read", current_time=future_time))

    # --- Contextual Intent Scoring Tests ---
    def test_intent_scoring_benign(self):
        gate = ContextualIntentGate()
        # Midday, low sensitivity, active daily
        ctx = IntentContext(hour_of_day=14, data_sensitivity="low", days_since_active=1)
        result = gate.score_intent("read_file", ctx)
        self.assertEqual(result["action"], "ALLOW")

    def test_intent_scoring_requires_challenge(self):
        gate = ContextualIntentGate()
        # 3 AM check, medium sensitivity
        ctx = IntentContext(hour_of_day=3, data_sensitivity="medium", days_since_active=1)
        result = gate.score_intent("modify_config", ctx)
        self.assertEqual(result["action"], "CHALLENGE")
        self.assertIn("score", result)

    def test_intent_scoring_blocks_critical_anomaly(self):
        gate = ContextualIntentGate()
        # 3 AM, HIGH sensitivity, dormant account
        ctx = IntentContext(hour_of_day=3, data_sensitivity="high", days_since_active=45)
        result = gate.score_intent("export_keys", ctx)
        self.assertEqual(result["action"], "BLOCK")

    # --- ADK Sentinel Integration Tests ---
    def test_adk_sentinel_graph_execution(self):
        # Proves the mocked ADK StateGraph successfully passes state through the 3 nodes
        from src.adk_sentinel import run_supervisor
        final_state = run_supervisor("https://github.com/advisories")
        
        # Ensure all steps populated the state dictionary
        self.assertIn("target_url", final_state)
        self.assertNotEqual(final_state["raw_html"], "")
        self.assertIn("status", final_state["analysis"])

if __name__ == '__main__':
    unittest.main()
