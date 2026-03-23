import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tachyon.core.reflector import AdversarialReflector
from scripts.run_pathogen import PathogenRunner

class TestMetamorphicReasoning(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.reflector = AdversarialReflector(self.root_dir)
        self.runner = PathogenRunner()

    def test_knowledge_ingestion(self):
        """Verify that the Reflector correctly maps the substrate topology."""
        # Using a mock knowledge base for deterministic testing
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', unittest.mock.mock_open(read_data="ADR-0040: Metamorphic Reasoning")):
            knowledge = self.reflector._ingest_knowledge()
            self.assertIn("ADR-0040", knowledge)

    def test_reflection_cycle(self):
        """Verify the Think-Criticize-Attack mutation logic."""
        template = {"type": "ASI05_CODE_EXECUTION", "payload": "rm -rf /", "vector": "jit_smuggling"}
        guidance = "Use nested quotes to bypass shell filters."
        
        reflection = self.reflector.reflect_and_mutate(template, guidance)
        
        self.assertIn("mutated_payload", reflection)
        self.assertIn("Semantic Drift", reflection['drift_strategy'])
        self.assertIn("REASONING:", reflection['mutated_payload'])

    def test_herald_signaling(self):
        """Verify that metamorphic stages are broadcast to the Telemetry Bus (Herald)."""
        # Set test mode to bypass frozen state
        os.environ["TACHYON_TEST_MODE"] = "1"
        self.runner.state.emit_alert = MagicMock()
        
        # We need to mock load_templates to return a simple list with required keys
        mock_template = {"type": "ASI05", "vector": "test", "payload": "rm -rf /"}
        
        with patch('scripts.run_pathogen.PathogenRunner.load_templates', return_value=[mock_template]):
             self.runner.execute_sweep()
             
             # Check for Herald events
             expected_topics = ["PATHOGEN_REFLECTION_STARTED", "PATHOGEN_GOAL_MUTATED", "PATHOGEN_BREACH"]
             emitted_topics = [call.args[0] for call in self.runner.state.emit_alert.call_args_list]
             
             for topic in expected_topics:
                 self.assertIn(topic, emitted_topics, f"Herald should have received {topic} event.")
        del os.environ["TACHYON_TEST_MODE"]
                 
    def test_goal_aliasing_visibility(self):
        """Verify that the specific goal mutation is visible in the alert metadata."""
        os.environ["TACHYON_TEST_MODE"] = "1"
        self.runner.state.emit_alert = MagicMock()
        mock_template = {"type": "ASI01", "vector": "test", "payload": "hijack"}
        
        with patch('scripts.run_pathogen.PathogenRunner.load_templates', return_value=[mock_template]):
             self.runner.execute_sweep()
             
             # Locate the GOAL_MUTATED event
             mutation_alert = next(call for call in self.runner.state.emit_alert.call_args_list if call.args[0] == "PATHOGEN_GOAL_MUTATED")
             self.assertIn("Strategy: Semantic Drift", mutation_alert.args[1])
        del os.environ["TACHYON_TEST_MODE"]

if __name__ == "__main__":
    unittest.main()
