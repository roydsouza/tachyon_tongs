import unittest
from src.intent_scoring import ContextualIntentGate, IntentContext

class TestContextualIntentGate(unittest.TestCase):
    def setUp(self):
        self.gate = ContextualIntentGate()
        
    def test_low_risk_context_allow(self):
        # 12 PM (no time anomaly), low sensitivity, active 1 day ago
        context = IntentContext(
            hour_of_day=12,
            data_sensitivity='low',
            days_since_active=1
        )
        result = self.gate.score_intent("read", context)
        self.assertEqual(result["action"], "ALLOW")
        self.assertLess(result["score"], 0.4)
        
    def test_medium_risk_context_challenge(self):
        # 3 AM (time anomaly: 0.3), medium sensitivity (0.4) = 0.7 
        context = IntentContext(
            hour_of_day=3,
            data_sensitivity='medium',
            days_since_active=1
        )
        result = self.gate.score_intent("read", context)
        # Score is 0.7, which is < 0.75, so CHALLENGE
        self.assertEqual(result["action"], "CHALLENGE")
        self.assertGreaterEqual(result["score"], 0.4)
        self.assertLess(result["score"], 0.75)
        
    def test_high_risk_context_block(self):
        # 3 AM (time anomaly: 0.3), high sensitivity (0.8), dormant (0.3)
        context = IntentContext(
            hour_of_day=3,
            data_sensitivity='high',
            days_since_active=45
        )
        result = self.gate.score_intent("delete", context)
        self.assertEqual(result["action"], "BLOCK")
        # Hard cap at 1.0
        self.assertGreaterEqual(result["score"], 0.75)

    def test_dormancy_alone_is_allow(self):
        # Dormant (0.3), but otherwise normal time (12 PM) and low sensitivity (0.0).
        # Score = 0.3 (< 0.4)
        context = IntentContext(
            hour_of_day=12,
            data_sensitivity='low',
            days_since_active=35
        )
        result = self.gate.score_intent("read", context)
        self.assertEqual(result["action"], "ALLOW")
        
if __name__ == '__main__':
    unittest.main()
