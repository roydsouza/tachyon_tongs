import unittest
import os
import json
import hashlib
from tachyon.agents.guardian_ids import GuardianIDS

class TestGuardianIDS(unittest.TestCase):
    def setUp(self):
        self.ids = GuardianIDS()
        self.manifest_path = "docs/adr/MANIFEST.json"
        with open(self.manifest_path, "r") as f:
            self.original_manifest = json.load(f)

    def tearDown(self):
        # Restore manifest after tests
        with open(self.manifest_path, "w") as f:
            json.dump(self.original_manifest, f, indent=2)

    def test_baseline_secure_state(self):
        """Verify that the current substrate is SECURE."""
        report = self.ids.verify_substrate()
        self.assertEqual(report["status"], "SECURE")
        self.assertEqual(report["merkle_verification"], "PASSED")

    def test_detect_content_tampering(self):
        """Verify that modifying an ADR content triggers a CRITICAL violation."""
        target_adr = "docs/adr/0001-record-architecture-decisions.md"
        with open(target_adr, "r") as f:
            original_content = f.read()
        
        try:
            # Tamper with content
            with open(target_adr, "a") as f:
                f.write("\n# MALICIOUS_INJECTION")
            
            report = self.ids.verify_substrate()
            # It will be CRITICAL due to sidecar mismatch and COMPROMISED due to Merkle mismatch
            self.assertIn(report["status"], ["CRITICAL", "COMPROMISED"])
            self.assertIn("INTEGRITY_VIOLATION", str(report["findings"]))
            self.assertEqual(report["merkle_verification"], "FAILED")
        finally:
            # Restore content
            with open(target_adr, "w") as f:
                f.write(original_content)

    def test_detect_manifest_tampering(self):
        """Verify that tampering with the Merkle Root in MANIFEST.json is detected."""
        tampered_manifest = self.original_manifest.copy()
        tampered_manifest["merkle_root"] = "deadbeef" * 8
        
        with open(self.manifest_path, "w") as f:
            json.dump(tampered_manifest, f, indent=2)
            
        report = self.ids.verify_substrate()
        self.assertEqual(report["status"], "COMPROMISED")
        self.assertEqual(report["merkle_verification"], "FAILED")
        self.assertIn("Merkle Root Mismatch", str(report["findings"]))

    def test_detect_missing_sidecar(self):
        """Verify that a missing .sig sidecar triggers a WARNING."""
        target_sig = "docs/adr/0015-model-routing.md.sig"
        os.rename(target_sig, target_sig + ".bak")
        
        try:
            report = self.ids.verify_substrate()
            self.assertEqual(report["status"], "WARNING")
            self.assertIn("MISSING_SIDECAR", str(report["findings"]))
        finally:
            os.rename(target_sig + ".bak", target_sig)

if __name__ == "__main__":
    unittest.main()
