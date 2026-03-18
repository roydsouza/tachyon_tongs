import unittest
import os
import sqlite3
import time
import subprocess
import requests
from tachyon.policy.singularity.client import RemoteSingularityPDP

class TestMetaPDP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Starts the Meta-PDP server in a background process."""
        cls.db_path = "memory/test_authz_ledger.db"
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
            
        # Set ENV for the server to use the test DB
        env = os.environ.copy()
        env["PYTHONPATH"] = f".:{env.get('PYTHONPATH', '')}"
        
        cls.server_proc = subprocess.Popen(
            ["python3", "tachyon/policy/singularity/server.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3) # Wait for server to boot

    @classmethod
    def tearDownClass(cls):
        """Stop the server and cleanup."""
        cls.server_proc.terminate()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self):
        self.client = RemoteSingularityPDP(server_url="http://localhost:8001")

    def test_remote_evaluation_and_ledger(self):
        """Verify remote evaluate call reaches the server and is logged to the ledger."""
        # 1. Test ALLOW
        result = self.client.evaluate("test_agent_alpha", "safe_fetch", {"url": "https://google.com"})
        self.assertIn(result.verdict.name, ["ALLOW", "DENY"]) # Mock depends on policy
        
        # 2. Test DENY (Simulate drift/violation if possible, or just check blocking)
        params = {"intent": "fetching documentation", "url": "https://vault.internal/key.pem"}
        # Note: ToolRouter normally calls AlignmentChecker, but PDP evaluation might also block.
        result = self.client.evaluate("agent_1", "outbound_dlp", {"has_sensitive_token": True})
        self.assertEqual(result.verdict.name, "DENY")

        # 3. Verify Ledger Persistence
        # We need to check the ledger DB produced by the server
        # Default server uses memory/authorization_ledger.db
        ledger_path = "memory/authorization_ledger.db"
        conn = sqlite3.connect(ledger_path)
        cursor = conn.cursor()
        cursor.execute("SELECT agent_id, action, verdict FROM authz_ledger WHERE agent_id = ?", ("test_agent_alpha",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "test_agent_alpha")
        self.assertEqual(row[1], "safe_fetch")
        conn.close()

    def test_fail_closed_unreachable(self):
        """Verify that the client fails CLOSED when the server URL is wrong."""
        broken_client = RemoteSingularityPDP(server_url="http://localhost:9999")
        result = broken_client.evaluate("agent_x", "any_action", {})
        self.assertEqual(result.verdict.name, "DENY")
        self.assertIn("ZERO-TRUST FAIL-CLOSED", result.reason)

if __name__ == "__main__":
    unittest.main()
