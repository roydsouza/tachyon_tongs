import unittest
import os
import sys
import json
from datetime import datetime

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tachyon.core.research import ResearchSynthesizer
from tachyon.core.state_manager import StateManager

class TestAutoresearchSynthesis(unittest.TestCase):
    def setUp(self):
        self.synthesizer = ResearchSynthesizer()
        self.db_path = "/tmp/test_tachyon_state.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.state = StateManager(db_path=self.db_path)

    def test_synthesis_classification(self):
        """Verify that threats are correctly mapped to ASI categories."""
        raw_threats = [
            {"id": "CVE-1", "summary": "Tool bypass in exec module"},
            {"id": "CVE-2", "summary": "Goal hijacking via prompt drift"}
        ]
        synthesis = self.synthesizer.synthesize(raw_threats)
        
        # CVE-1 should map to ASI02 (Tool) or ASI05 (Code)
        # Based on my mock heuristic: "tool" -> ASI02, "code"/"exec" -> ASI05
        # "Tool bypass in exec module" has both. If order is tool first:
        self.assertEqual(synthesis['asi_mapping']['ASI02'], ["CVE-1"])
        self.assertEqual(synthesis['asi_mapping']['ASI01'], ["CVE-2"])

    def test_catalog_export_with_synthesis(self):
        """Verify that export_catalog produces the High-Signal format."""
        threats = [{"cve_id": "TEST-CVE", "description": "Critical tool bypass"}]
        self.state.log_exploitation(threats, catalog_file="/tmp/TEST_CATALOG.md")
        
        with open("/tmp/TEST_CATALOG.md", "r") as f:
            content = f.read()
            self.assertIn("# 📘 EXPLOITATION CATALOG (High-Signal)", content)
            self.assertIn("## 💎 Crown Jewels: Synthesized Intelligence", content)
            self.assertIn("ASI02", content) # Classified as tool

if __name__ == "__main__":
    unittest.main()
