import time
import json
import pytest
import importlib.util
import sys
import os

# Ensure project root is in path for relative imports
sys.path.insert(0, os.getcwd())

# Dynamic import for hyphenated module path
def import_agent_class(module_path, class_name):
    spec = importlib.util.spec_from_file_location(class_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

healer_path = os.path.join(os.getcwd(), "agents", "healer", "agent.py")
HealerPlugin = import_agent_class(healer_path, "HealerPlugin")
from tachyon.core.bus import TachyonEventBus

def test_healer_somatic_coordination():
    """Verify that the Healer reacts to patch proposals."""
    bus = TachyonEventBus()
    config = {}
    healer = HealerPlugin("healer_test", config)
    
    # Capture telemetry
    initial_telemetry = bus.fetch_events(topic="TELEMETRY")
    
    # 📢 SIMULATE: Engineer proposing a patch
    bus.emit_event(
        topic="PATCH_PROPOSED",
        agent_id="engineer_mock",
        payload={"cve_id": "CVE-2026-TEST", "patch": "diff --git ..."},
        signature="INFO"
    )
    
    # Process subscriptions manually for the test
    # This simulates the logic inside _backplane_loop
    for topic in healer._subscriptions.keys():
        events = healer.bus.fetch_events(topic=topic, after_id=healer._last_event_id)
        for event in events:
            healer._last_event_id = max(healer._last_event_id, event['id'])
            payload = json.loads(event['payload_json'])
            for callback in healer._subscriptions.get(topic, []):
                callback(topic, event['agent_id'], payload, event['timestamp'], event['certificate_json'])
    
    # Verify Healer ACK
    new_telemetry = bus.fetch_events(topic="TELEMETRY")
    acks = []
    for e in new_telemetry:
        payload = json.loads(e["payload_json"])
        if payload.get("type") == "SOMATIC_ACK":
            acks.append((e, payload))
    
    assert len(acks) > 0
    event, payload = acks[-1]
    assert event["agent_id"] == "healer_test"
    assert payload["cve_id"] == "CVE-2026-TEST"
    assert payload["status"] == "READY_FOR_OVERSIGHT"
    print("\n✅ Healer Somatic Coordination Verified.")

if __name__ == "__main__":
    test_healer_somatic_coordination()
