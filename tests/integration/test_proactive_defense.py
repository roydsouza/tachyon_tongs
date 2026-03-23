import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.run_pathogen import PathogenRunner

class TestProactiveDefense(unittest.TestCase):
    def setUp(self):
        self.runner = PathogenRunner()

    def test_template_loading(self):
        """Verify that templates are correctly discovered."""
        templates = self.runner.load_templates()
        self.assertGreaterEqual(len(templates), 3, "Should load at least 3 baseline templates.")
        self.assertIn("ASI01_GOAL_HIJACK", [t['type'] for t in templates])

    @patch('scripts.run_pathogen.PathogenRunner.synthesize_hybrid_attack')
    def test_sweep_execution(self, mock_synth):
        """Verify the full proactive sweep loop logic."""
        mock_synth.return_value = "mock_mutated_payload"
        
        # Simulate a sweep
        templates = self.runner.load_templates()
        for t in templates[:1]: # Test first only
            guidance = self.runner.get_guidance(t['type'])
            self.assertIsNotNone(guidance, f"Guidance for {t['type']} should exist.")
            
            hybrid = self.runner.synthesize_hybrid_attack(t, guidance)
            self.assertEqual(hybrid, "mock_mutated_payload")

if __name__ == "__main__":
    unittest.main()
