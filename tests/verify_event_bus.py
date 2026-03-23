import os
import sys
import json
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tachyon.core.signing import IntegrityManager
from tachyon.core.bus import TachyonEventBus
from tachyon.core.keys.hybrid import HybridSigner

def test_event_bus_pqc_flow():
    print("--- [EventBus] Starting PQC Verification Test ---")
    
    # 1. Setup Infrastructure with Mocked Keys
    print("[Test] Initializing IntegrityManager in software mode...")
    im = IntegrityManager(use_hardware=False)
    
    # Manually Inject a Root Key for the session (since KeychainProvider won't load one)
    root_private = ed25519.Ed25519PrivateKey.generate()
    root_public = root_private.public_key()
    im._private_key = root_private
    im._public_key = root_public
    # Re-initialize the signer with these keys
    im.signer = HybridSigner(ed25519_sk=root_private, ed25519_pk=root_public)
    
    bus = TachyonEventBus(integrity_manager=im)
    
    # 2. Derive Agent Identity (The Sentinel)
    role = "sentinel"
    print(f"[Test] Deriving key and certificate for role: {role}...")
    agent_key, certificate = im.derive_agent_key(role)
    print(f"[Test] Certificate Fingerprint: {certificate['payload']['subject']['fingerprint']}")
    
    # 3. Create and Sign an Event
    topic = "THREAT_DETECTED"
    payload = {
        "cve": "CVE-2026-1234",
        "severity": "CRITICAL",
        "description": "Exploit detected in substrate airlock."
    }
    
    # Content pattern must match EventBus.verify_event: topic + payload_json + timestamp
    timestamp = datetime.now().isoformat()
    payload_json = json.dumps(payload, sort_keys=True)
    content = f"{topic}:{payload_json}:{timestamp}".encode('utf-8')
    
    # Sign with Agent Key
    print("[Test] Signing event with Agent Key...")
    agent_signer = HybridSigner(ed25519_sk=agent_key)
    signature = agent_signer.sign(content)
    
    # 4. Emit to Bus
    print("[Test] Emitting signed event to bus...")
    with bus._get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO event_bus (timestamp, topic, agent_id, payload_json, signature, certificate_json) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, topic, role, payload_json, signature, json.dumps(certificate))
        )
        event_id = cursor.lastrowid
        conn.commit()
    
    print(f"[Test] Event Emitted! ID: {event_id}")
    
    # 5. Verify via Bus
    print("[Test] Verifying event integrity via EventBus.verify_event()...")
    is_valid = bus.verify_event(event_id)
    
    if is_valid:
        print("[SUCCESS] EventBus PQC/Classical Verification PASSED!")
    else:
        print("[FAILURE] EventBus Verification FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    test_event_bus_pqc_flow()
