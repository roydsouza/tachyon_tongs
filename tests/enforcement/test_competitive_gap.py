import unittest
import os
import json
from tachyon.enforcement.safe_fetch import SafeFetch, SecurityViolationError
from tachyon.enforcement.apple_sandbox import AppleSandbox

class TestCompetitiveGap(unittest.TestCase):
    def setUp(self):
        self.sandbox = AppleSandbox()
        # TT-2026-003: Test mode via env var, not constructor param
        os.environ["TACHYON_TEST_MODE"] = "1"
        self.fetcher = SafeFetch()
    
    def tearDown(self):
        os.environ.pop("TACHYON_TEST_MODE", None)

    def test_domain_reputation_blocking(self):
        """Verify that high-risk domains are blocked by the reputation engine."""
        # Seed the whitelist for Google but NOT for emailgpt
        import sqlite3
        from tachyon.core.state import StateManager
        db_path = StateManager().db_path
        with sqlite3.connect(db_path) as conn:
             conn.execute("INSERT OR IGNORE INTO exploitation_catalog (cve_id, relevance_class) VALUES (?, ?)", ("google.com", "APPROVED"))
             conn.commit()
             
        # 1. Test Malicious Domain (Score 0.1)
        with self.assertRaises(SecurityViolationError):
             self.fetcher.fetch("https://emailgpt.com/payload")

        # 2. Test Trusted Domain (Score 1.0)
        # Note: In mock mode, this might fail if networking is off, but status should not be BLOCKED by intent gate
        # google.com is seeded in the whitelist above
        result = self.fetcher.fetch("https://google.com")
        self.assertNotEqual(result["status"], "BLOCKED")

    def test_static_analysis_blocking(self):
        """Verify that dangerous Python payloads are blocked before execution."""
        # 1. Create a malicious script
        malicious_script = os.path.join(self.sandbox.workspace_dir, "attack.py")
        with open(malicious_script, "w") as f:
            f.write("import os\nos.system('rm -rf /')")
            
        # 2. Attempt execution
        result = self.sandbox.execute(["python3", malicious_script])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("Static Analysis Violation", result["error"])
        
        # 3. Create a safe script
        safe_script = os.path.join(self.sandbox.workspace_dir, "safe.py")
        with open(safe_script, "w") as f:
            f.write("print('Hello World')")
            
        # 4. Attempt execution
        result = self.sandbox.execute(["python3", safe_script])
        # On macOS, sandbox-exec might fail if python3 path isn't right in the profile,
        # but the key for THIS test is that it's NOT BLOCKED by the gate.
        self.assertNotEqual(result["status"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
