import os
import sys
import json
import time
import threading
from datetime import datetime

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents._core.base import BaseAgentPlugin
from tachyon.core.bus import TachyonEventBus
from tachyon.core.signing import IntegrityManager
from tachyon.core.keys.certificates import DelegationCertificateAuthority
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

class PingerAgent(BaseAgentPlugin):
    def execute_action(self, action: str, parameters: dict):
        return {"status": "SUCCESS"}

class PongerAgent(BaseAgentPlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pings_received = 0
        self.subscribe("IMMUNE_SIGNAL_PING", self.handle_ping)
    
    def handle_ping(self, payload):
        print(f"[{self.agent_id}] PING RECEIVED! Content: {payload.get('msg')}")
        self.pings_received += 1
        
    def execute_action(self, action: str, parameters: dict):
        return {"status": "SUCCESS"}

def verify_coordination():
    print("--- [Phase 33] Verifying Inter-Agent Coordination Loop ---")
    
    # 0. Setup Root CA and Certificates
    im = IntegrityManager(use_hardware=False)
    # Generate mock root
    root_sk = ed25519.Ed25519PrivateKey.generate()
    root_pk = root_sk.public_key()
    im._private_key = root_sk # Mock override
    im._public_key = root_pk
    
    ca = DelegationCertificateAuthority(im)
    
    # 1. Initialize Agents
    pinger = PingerAgent(agent_id="pinger", plugin_name="Pinger", config={})
    pinger_sk, pinger_cert = ca.derive_and_issue("PINGER")
    pinger.im._private_key = pinger_sk
    pinger.im._public_key = pinger_sk.public_key()
    pinger.certificate = pinger_cert
    
    ponger = PongerAgent(agent_id="ponger", plugin_name="Ponger", config={})
    ponger_sk, ponger_cert = ca.derive_and_issue("PONGER")
    ponger.im._private_key = ponger_sk
    ponger.im._public_key = ponger_sk.public_key()
    ponger.certificate = ponger_cert

    # 2. Start Ponger Backplane
    ponger.start_backplane_loop(interval_sec=1)
    
    # 3. Pinger Emits Signal
    topic = "IMMUNE_SIGNAL_PING"
    payload = {"msg": "Coordination Test"}
    payload_json = json.dumps(payload, sort_keys=True)
    ts = datetime.now().isoformat()
    content = f"{topic}:{payload_json}:{ts}".encode('utf-8')
    sig = pinger.im.signer.sign(content)
    
    pinger.bus.emit_event(
        topic=topic,
        agent_id="pinger",
        payload=payload,
        signature=sig,
        certificate=pinger.certificate,
        timestamp=ts
    )
    
    # 4. Wait and Verify
    print("[Test] Waiting for Ponger to process event...")
    time.sleep(3)
    
    if ponger.pings_received > 0:
        print(f"[SUCCESS] Ponger received {ponger.pings_received} pings via the backplane!")
    else:
        print("[FAILURE] Ponger did not receive any pings.")
        
    ponger.stop_backplane_loop()

if __name__ == "__main__":
    verify_coordination()
