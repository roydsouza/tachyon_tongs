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

    def test_multi_category_propagation(self):
        # 1. Seed Multiple Forensic Breaches
        self.store.log_event("p1", "PATHOGEN_BREACH", action="act", status="OK", details={"asi_id": "ASI-07", "summary": "Drift 1"})
        self.store.log_event("p2", "SENTINEL_DISCOVERY", action="act", status="OK", details={"asi_id": "ASI-01", "summary": "Discovery 1"})
        
        # 2. Add ASI-01 section to mock model
        with open(self.mock_tm, "a") as f:
            f.write("\n### [ASI-01] Prompt Injection\n- Baseline.\n")
            
        # 3. Run Updater
        updater = ThreatModelUpdater(db_path=self.mock_db, threat_model_path=self.mock_tm)
        count = updater.propagate_findings()
        self.assertEqual(count, 2)
        
        # 4. Verify Multi-Section Injection
        with open(self.mock_tm, "r") as f:
            content = f.read()
        self.assertIn("Discovery 1", content)
        self.assertIn("### [ASI-01]", content)
        
        # 5. Verify PQC-Signed State
        from tachyon.core.signing import IntegrityManager
        im = IntegrityManager()
        self.assertTrue(im.verify_integrity(self.mock_tm))

if __name__ == "__main__":
    unittest.main()
