import unittest
import os
import sqlite3
import json
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tachyon.core.threat_updater import ThreatModelUpdater
from tachyon.core.forensics import ForensicStore

class TestThreatPropagation(unittest.TestCase):
    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.mock_db = os.path.join(self.root, "tests", "core", "mock_forensics.db")
        self.mock_tm = os.path.join(self.root, "tests", "core", "MOCK_THREAT_MODEL.md")
        
        # Setup Mock DB
        if os.path.exists(self.mock_db): os.remove(self.mock_db)
        self.store = ForensicStore(db_path=self.mock_db)
        
        # Setup Mock Threat Model
        with open(self.mock_tm, "w") as f:
            f.write("# Mock Threat Model\n\n## Adversarial Evidence\n")
            f.write("### [ASI-07] Semantic Drift\n- Baseline evidence.\n")

    def tearDown(self):
        if os.path.exists(self.mock_db): os.remove(self.mock_db)
        if os.path.exists(self.mock_tm): os.remove(self.mock_tm)
        sig_path = self.mock_tm + ".sig"
        if os.path.exists(sig_path): os.remove(sig_path)

    def test_propagation_logic(self):
        # 1. Seed Forensic Breach
        self.store.log_event(
            "pathogen_agent",
            "PATHOGEN_BREACH",
            action="exploit_vector",
            status="SUCCESS",
            details={
                "asi_id": "ASI-07",
                "summary": "Bypassed intent-gating via nested reasoning tokens."
            }
        )
        
        # 2. Run Updater
        updater = ThreatModelUpdater(db_path=self.mock_db, threat_model_path=self.mock_tm)
        count = updater.propagate_findings()
        
        self.assertEqual(count, 1)
        
        # 3. Verify Markdown Injection
        with open(self.mock_tm, "r") as f:
            content = f.read()
            
        self.assertIn("Bypassed intent-gating", content)
        self.assertIn("forensic:1", content)
        
        # 4. Verify PQC Signing (Should have a .sig file)
        self.assertTrue(os.path.exists(self.mock_tm + ".sig"))

if __name__ == "__main__":
    unittest.main()
