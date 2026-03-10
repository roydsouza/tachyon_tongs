import unittest
from src.behavior_monitor import PromptBehaviorMonitor, BehaviorAnomalyError

class TestBehaviorMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = PromptBehaviorMonitor(max_reasoning_steps=5)

    def test_valid_chain_of_thought_allowed(self):
        valid_cot = [
            "I need to check the process list.",
            "Analyzing process behavior.",
            "Found nothing suspicious."
        ]
        result = self.monitor.check_chain_of_thought(valid_cot)
        self.assertTrue(result)

    def test_exceeds_max_reasoning_steps_exhaustion(self):
        exhausting_cot = [
            f"Step {i} checking..." for i in range(6)
        ]
        with self.assertRaises(BehaviorAnomalyError) as context:
            self.monitor.check_chain_of_thought(exhausting_cot)
        self.assertIn("Exceeded maximum 5 reasoning steps", str(context.exception))
        
    def test_cyclic_hallucinations_detected(self):
        cyclic_cot = [
            "Attempting to read file config.json",
            "Reading file config.json",
            "Attempting to read file config.json"
        ]
        with self.assertRaises(BehaviorAnomalyError) as context:
            self.monitor.check_chain_of_thought(cyclic_cot)
        self.assertIn("Cyclic hallucination detected", str(context.exception))

if __name__ == '__main__':
    unittest.main()
