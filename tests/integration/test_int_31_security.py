import unittest
import json
import base64
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric import ed25519
from tachyon.api.server import app
from tachyon.core.state_manager import StateManager

class TestSecurityHardening(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.state = StateManager()
        
        # Create a test sensor key pair
        self.priv = ed25519.Ed25519PrivateKey.generate()
        self.pub = self.priv.public_key()
        self.pub_bytes = self.pub.public_bytes_raw()
        self.pub_b64 = f"ed25519:{base64.b64encode(self.pub_bytes).decode()}"

    def test_revoked_sensor(self):
        sensor_id = "revoked_sensor_01"
        self.state.register_sensor(sensor_id, self.pub_b64, status="REVOKED")
        
        body_str = json.dumps({"agent_id": "sentinel", "action": "test", "parameters": {}})
        sig = f"ed25519:{self.priv.sign(body_str.encode()).hex()}"
        
        payload = {
            "command_body": body_str,
            "signature": sig,
            "signer_id": sensor_id,
            "nonce": 1,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        resp = self.client.post("/api/v1/relay", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "DENIED")
        self.assertIn("REVOKED", resp.json()["error"])

    def test_expired_sensor(self):
        sensor_id = "expired_sensor_01"
        # Set expiry in the past
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        self.state.register_sensor(sensor_id, self.pub_b64, expires_at=past)
        
        body_str = json.dumps({"agent_id": "sentinel", "action": "test", "parameters": {}})
        sig = f"ed25519:{self.priv.sign(body_str.encode()).hex()}"
        
        payload = {
            "command_body": body_str,
            "signature": sig,
            "signer_id": sensor_id,
            "nonce": 1,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        resp = self.client.post("/api/v1/relay", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "DENIED")
        self.assertIn("EXPIRED", resp.json()["error"])

if __name__ == "__main__":
    unittest.main()
