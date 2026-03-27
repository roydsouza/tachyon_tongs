import pytest
import os
import importlib
from tachyon.core.state import StateManager

herald_mod = importlib.import_module("agents.herald.agent")
HeraldPlugin = herald_mod.HeraldPlugin

@pytest.fixture
def state():
    db_path = "test_healer.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ["TACHYON_DB_PATH"] = db_path
    manager = StateManager(db_path)
    # Ensure logs dir doesn't have canary log for testing
    if os.path.exists("logs/TEST_CANARY.md"):
        os.remove("logs/TEST_CANARY.md")
    yield manager
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists("logs/TEST_CANARY.md"):
        os.remove("logs/TEST_CANARY.md")

def test_herald_self_healing(state):
    """Verify Herald fixes missing files automatically."""
    herald = HeraldPlugin("healer-agent", {})
    
    # 1. Mock a failure entry in logs/EVOLUTION.md
    evo_path = "logs/EVOLUTION.md"
    failure_msg = "Agent failed: [Errno 2] No such file or directory: 'logs/TEST_CANARY.md'"
    state.log_evolution("Agent Failure", failure_msg)
    
    # Verify file doesn't exist yet
    assert not os.path.exists("logs/TEST_CANARY.md")
    
    # 2. Trigger relay (which triggers healing)
    res = herald.execute_action("relay_new_events", {})
    
    # 3. Verify heal
    assert os.path.exists("logs/TEST_CANARY.md")
    # Verify the relay count was at least 1
    assert res["relayed_count"] >= 1
    
    # 4. Verify evolution entry for the repair
    with open(evo_path, "r") as f:
        content = f.read()
        assert "SOMATIC_REPAIR" in content
        assert "Successfully recreated missing path: logs/TEST_CANARY.md" in content
