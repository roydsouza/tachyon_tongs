import pytest
import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from tachyon.core.bus import TachyonEventBus
from tachyon.core.signing import IntegrityManager
from tachyon.core.state import StateManager

@pytest.fixture
def clean_bus():
    os.environ["TACHYON_TEST_MODE"] = "1"
    StateManager._instance = None
    db_path = "tests/tmp/test_chain.db"
    bus_path = "tests/tmp/test_bus_chain.db"
    if os.path.exists(db_path): os.remove(db_path)
    if os.path.exists(bus_path): os.remove(bus_path)
    
    im = IntegrityManager(use_hardware=False)
    bus = TachyonEventBus(db_path=bus_path, integrity_manager=im)
    return bus, im

def test_delegation_chain_verification(clean_bus):
    bus, im = clean_bus
    
    # 1. Generate an agent identity (The Ritual)
    agent_id = "sentinel-test"
    role = "sentinel"
    cert = im.load_agent_identity(role)
    assert cert is not None
    
    # 2. Emit a signed event from the agent
    topic = "TEST_ALIVE"
    payload = {"status": "ok"}
    payload_json = json.dumps(payload, sort_keys=True)
    timestamp = "2026-03-27T10:00:00"
    
    # Sign manually using the agent's sub-key (matching Bus.verify_event logic)
    content = f"{topic}:{payload_json}:{timestamp}".encode('utf-8')
    
    # Get the private key for the agent (from memory/keys)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    key_path = os.path.join(root_dir, "memory", "keys", f"agent_{role}.json")
    with open(key_path, "r") as f:
        key_data = json.load(f)
    
    sk_bytes = base64.b64decode(key_data["private_key_b64"])
    agent_sk = ed25519.Ed25519PrivateKey.from_private_bytes(sk_bytes)
    
    from tachyon.core.keys.hybrid import HybridSigner
    agent_signer = HybridSigner(ed25519_sk=agent_sk)
    signature = agent_signer.sign(content)
    
    # 3. Emit to bus
    event_id = bus.emit_event(
        topic=topic,
        agent_id=agent_id,
        payload=payload,
        signature=signature,
        certificate=cert,
        timestamp=timestamp
    )
    
    # 4. Verify Chain (Root -> Cert -> Event)
    assert bus.verify_event(event_id) == True

def test_tampered_certificate_rejection(clean_bus):
    bus, im = clean_bus
    agent_id = "tamper-agent"
    cert = im.load_agent_identity("sentinel")
    
    # Tamper with the certificate (change the expiry)
    cert_tampered = json.loads(json.dumps(cert))
    cert_tampered["payload"]["expires_at"] = "2099-01-01T00:00:00"
    
    event_id = bus.emit_event(
        topic="TAMPER",
        agent_id=agent_id,
        payload={"msg": "hidden"},
        signature="fake-sig",
        certificate=cert_tampered
    )
    
    # Bus should reject because the certificate signature (from Root) is now invalid
    assert bus.verify_event(event_id) == False
