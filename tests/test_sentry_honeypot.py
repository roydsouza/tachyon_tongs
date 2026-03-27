import os
import time
import json
import pytest
import importlib.util
import sys

# Ensure project root is in path for relative imports
sys.path.insert(0, os.getcwd())

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Dynamic import for hyphenated module path
def import_agent_class(module_path, class_name):
    spec = importlib.util.spec_from_file_location(class_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

# Import Guardian via importlib since 'code-only' is gone
guardian_path = os.path.join(root_dir, "agents", "guardian", "agent.py")
GuardianPlugin = import_agent_class(guardian_path, "GuardianPlugin")

sentry_path = os.path.join(root_dir, "agents", "sentry", "agent.py")
SentryPlugin = import_agent_class(sentry_path, "SentryPlugin")

healer_path = os.path.join(os.getcwd(), "agents", "healer", "agent.py")
HealerPlugin = import_agent_class(healer_path, "HealerPlugin")

from tachyon.core.bus import TachyonEventBus
from tachyon.core.signing import IntegrityManager
from tachyon.core.state import StateManager

def test_sentry_honeypot_trigger():
    """Verify that accessing the bait file triggers a security alert."""
    bus = TachyonEventBus()
    config = {}
    sentry = SentryPlugin("sentry_test", config)
    
    # Ensure bait is deployed
    bait_path = sentry.engine.bait_path
    assert os.path.exists(bait_path)
    
    # Capture initial bus state
    initial_events = bus.fetch_events(topic="SECURITY_ALERT")
    
    # 🚨 TRIGGER: Access the bait file
    # We use touch to update the access time (atime)
    os.utime(bait_path, (time.time() + 10, time.time() + 10))
    
    # Run the background loop to detect the change
    sentry.check_signals()
    
    # Verify alert emission
    new_events = bus.fetch_events(topic="SECURITY_ALERT")
    assert len(new_events) > len(initial_events)
    
    last_event = new_events[-1]
    payload = json.loads(last_event["payload_json"])
    assert last_event["agent_id"] == "sentry_test"
    assert payload["reason"] == "Honeypot Triggered"
    assert payload["type"] == "INTRUSION"
    print("\n✅ Sentry Honeypot Trigger Verified.")

if __name__ == "__main__":
    test_sentry_honeypot_trigger()
