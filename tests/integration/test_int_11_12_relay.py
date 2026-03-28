import unittest
import json
import base64
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from cryptography.hazmat.primitives.asymmetric import ed25519
from tachyon.api.server import app
from tachyon.core.state import StateManager

class TestSignedRelay(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.state = StateManager()
        
        # Create a test sensor key pair
        self.priv = ed25519.Ed25519PrivateKey.generate()
        self.pub = self.priv.public_key()
        self.pub_bytes = self.pub.public_bytes_raw()
        self.pub_b64 = f"ed25519:{base64.b64encode(self.pub_bytes).decode()}"
        self.sensor_id = "test_sensor_01"

    def test_relay_flow(self):
        # 1. Register Sensor
        resp = self.client.post("/api/v1/auth/exchange", json={
            "sensor_id": self.sensor_id,
            "public_key_b64": self.pub_b64
        })
        self.assertEqual(resp.status_code, 200)
        
        # 2. Prepare Tool Request
        body_dict = {
            "agent_id": "sentinel",
            "action": "safe_fetch",
            "parameters": {"url": "https://cisa.gov", "intent": "SECURITY"}
        }
        body_str = json.dumps(body_dict)
        
        # 3. Sign it (Hybrid simulated - we only have Ed25519 in test environment usually)
        # HybridSigner format: "ed25519:xxxx"
        sig = f"ed25519:{self.priv.sign(body_str.encode()).hex()}"
        
        # 4. Submit Valid Command
        relay_payload = {
            "command_body": body_str,
            "signature": sig,
            "signer_id": self.sensor_id,
            "nonce": 100,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        resp = self.client.post("/api/v1/relay", json=relay_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "SUCCESS")
        
        # 5. Replay Attack
        resp = self.client.post("/api/v1/relay", json=relay_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "DENIED")
        self.assertIn("Replay Attack", data["error"])

        # 6. Invalid Signature
        relay_payload["nonce"] = 101
        relay_payload["signature"] = "ed25519:deadbeef"
        resp = self.client.post("/api/v1/relay", json=relay_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "DENIED")
        self.assertIn("Signature Mismatch", data["error"])

if __name__ == "__main__":
    unittest.main()
