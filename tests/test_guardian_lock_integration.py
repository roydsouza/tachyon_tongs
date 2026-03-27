import pytest
import os
import importlib
guardian_mod = importlib.import_module("agents.guardian.agent")
GuardianPlugin = guardian_mod.GuardianPlugin
from tachyon.core.state import StateManager

@pytest.fixture
def state():
    db_path = "test_integration.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ["TACHYON_DB_PATH"] = db_path
    manager = StateManager(db_path)
    yield manager
    if os.path.exists(db_path):
        os.remove(db_path)

def test_guardian_suppression_logic(state):
    """Verify that Guardian respects the Mutant Lock."""
    config = {"quarantine_mode": False}
    guardian = GuardianPlugin("test-guardian", config)
    
    # 1. Simulate a failed file (we use an existing file but assume it will fail if tampered)
    # For this unit test, we'll mock verify_integrity to return False
    guardian.integrity_manager.verify_integrity = lambda p: False
    
    # 2. No lock - should return FAILURE
    res_no_lock = guardian.execute_action("verify_file", {"filepath": "TASKS.md"})
    assert res_no_lock["status"] == "FAILURE"
    
    # 3. Acquire lock
    state.acquire_mutant_lock("test-agent", "Security patch")
    
    # 4. With lock - should return WARNING (Suppressed)
    res_with_lock = guardian.execute_action("verify_file", {"filepath": "TASKS.md"})
    assert res_with_lock["status"] == "WARNING"
    assert res_with_lock["authorized_mutation"] is True
