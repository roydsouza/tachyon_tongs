import pytest
import os
import shutil
from tachyon.core.immune_manager import ImmuneManager
from tachyon.core.state import StateManager

@pytest.fixture
def clean_state():
    """Ensure a fresh state for testing."""
    if os.path.exists("test_tachyon.db"):
        os.remove("test_tachyon.db")
    os.environ["TACHYON_DB_PATH"] = "test_tachyon.db"
    state = StateManager("test_tachyon.db")
    yield state
    if os.path.exists("test_tachyon.db"):
        os.remove("test_tachyon.db")

def test_immune_loop_idempotency(clean_state):
    """Verify that ImmuneManager only processes bypasses once."""
    log_path = "test_canary.md"
    with open(log_path, "w") as f:
        f.write("### [2026-03-20T10:00:00] BYPASS-001 | STATUS: BYPASSED\n")
        f.write("- **Payload**: `malicious-command`\n")
    
    manager = ImmuneManager()
    manager.canary_log = log_path
    
    # 1. First run should trigger evolution
    # Note: We mock the actual engineer call if needed, but here we want to see the state tracking
    # Since EngineerRole attempts to call hitpx, we might get an error if daemon is off, 
    # but the Manager should still attempt and we should see it marked if it "finishes"
    
    # Mocking _evolve_fix to bypass network calls for this unit test
    original_evolve = manager._evolve_fix
    manager._evolve_fix = lambda b: {"threat_id": b["id"], "engineer_status": "staged"}
    
    results = manager.scan_and_evolve()
    assert results["evolutions_triggered"] == 1
    assert clean_state.is_event_processed("BYPASS-001-2026-03-20T10:00:00")
    
    # 2. Second run should trigger 0 evolutions
    results_2 = manager.scan_and_evolve()
    assert results_2["evolutions_triggered"] == 0
    
    os.remove(log_path)

def test_immune_parsing():
    """Verify Canary Log parsing regex."""
    log_content = """
### [2026-03-20T12:00:00] TEST-ID | STATUS: BYPASSED
- **Payload**: `CMD: /bin/sh`
- **Forensics**: Sanitizer triggered: False
"""
    import re
    pattern = r"### \[(.*?)\] (.*?) \| STATUS: BYPASSED\n- \*\*Payload\*\*: `(.*?)`"
    match = re.search(pattern, log_content)
    assert match is not None
    assert match.group(1) == "2026-03-20T12:00:00"
    assert match.group(2) == "TEST-ID"
    assert match.group(3) == "CMD: /bin/sh"
