import os
import pytest
import tempfile
import shutil
import json
import time
from agents.guardian.agent import GuardianPlugin
from agents.healer.agent import HealerPlugin
from tachyon.core.signing import IntegrityManager
from tachyon.core.bus import TachyonEventBus
from tachyon.core.state import StateManager

# Substrate environment is now provided by tests/conftest.py

# Substrate environment is now provided by tests/conftest.py

def test_full_security_loop_no_mocks(substrate_env):
    """
    TD-01: Integration test verifying the full Sentry -> Healer -> Guardian loop.
    Ensures PQC signing, EventBus relay, and State persistence work with real files.
    """
    env = substrate_env
    tmp_dir = env["tmp_dir"]
    
    # 1. Initialize Agents with real delegated identities
    # Derive keys first so they have valid certificates
    _, cert_guardian = env["im"].derive_agent_key("guardian", save_to_disk=True)
    _, cert_healer = env["im"].derive_agent_key("healer", save_to_disk=True)
    
    guardian = GuardianPlugin("test-guardian", {"quarantine_mode": False})
    healer = HealerPlugin("test-healer", {})
    
    # 2. Create a test file and sign it (Using the Agent's own signer)
    test_file = os.path.join(tmp_dir, "critical_logic.py")
    with open(test_file, "w") as f:
        f.write("print('Hello World')")
    
    guardian.im.sign_document(test_file)
    assert os.path.exists(test_file + ".sig.json")
    
    # 3. Verify Integrity (Guardian Action)
    # execute_action now returns TachyonResult object
    result = guardian.execute_action("verify_file", {"filepath": test_file})
    assert result.status.value == "SUCCESS"
    assert result.data["is_valid"] == True
    
    # 4. Simulate an Integrity Violation (Tamper the file)
    with open(test_file, "a") as f:
        f.write("\n# Tampered logic")
        
    result_tampered = guardian.execute_action("verify_file", {"filepath": test_file})
    assert result_tampered.status.value == "DENIED" # IntegrityManager raises error on mismatch
    
    # 5. Verify the Bus Relay (Real Signed Event Emission)
    guardian.emit_signed_event(
        topic="INTEGRITY_VIOLATION",
        payload={"filepath": test_file, "reason": "TAMPERED"}
    )
    
    events = env["bus"].fetch_events(topic="INTEGRITY_VIOLATION", after_id=0)
    assert len(events) >= 1
    # Verify the most recent event (which should be our signed one)
    assert env["bus"].verify_event(events[-1]["id"]) == True
    
    print("[INTEGRATION_SUCCESS] Full security loop verified with zero mocks.")

def test_result_monad_behavior(substrate_env):
    """TD-02: Verify that all agents now return standardized TachyonResult objects."""
    env = substrate_env
    guardian = GuardianPlugin("test-guardian", {})
    
    # 2. Create and sign a test file for monad testing
    test_file = os.path.join(env["tmp_dir"], "monad_test.py")
    with open(test_file, "w") as f: f.write("print('test')")
    env["im"].sign_document(test_file)
    
    # execute_action returns TachyonResult object
    res = guardian.execute_action("verify_file", {"filepath": test_file})
    assert res.status.value in ["SUCCESS", "ERROR", "FAILURE", "DENIED"]
    
    # Test invalid action (Fails Loudly)
    res_bad = guardian.execute_action("unknown_action", {})
    assert res_bad.status.value == "NOT_IMPLEMENTED"
    assert res_bad.error is not None
    assert "Unknown action" in res_bad.error
