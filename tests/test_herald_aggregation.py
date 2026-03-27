import pytest
import os
import importlib
from tachyon.core.state import StateManager

herald_mod = importlib.import_module("agents.herald.agent")
HeraldPlugin = herald_mod.HeraldPlugin

@pytest.fixture
def state():
    db_path = "test_herald.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ["TACHYON_DB_PATH"] = db_path
    manager = StateManager(db_path)
    yield manager
    if os.path.exists(db_path):
        os.remove(db_path)

def test_herald_aggregation_logic(state):
    """Verify Herald collects events from multiple sources."""
    herald = HeraldPlugin("test-herald", {})
    
    # 1. Mock an alert in ALERT.md
    with open("ALERT.md", "w") as f:
        f.write("# 🚨 Alerts\n\n## [TEST_ALERT] 2026-03-22 20:00:00\n> [!CAUTION]\n> Test message\n\n---\n\n")
    
    # 2. Mock a task in TASKS.md
    with open("TASKS.md", "w") as f:
        f.write("- [ ] **HITL**: Review this patch\n")
        
    # 3. Simulate Airlock patch
    with state._lock:
        import sqlite3
        with sqlite3.connect(state.db_path) as conn:
            conn.execute("INSERT INTO patches (id, summary, status) VALUES ('p1', 'Fix bug', 'PENDING')")
            conn.commit()

    # 4. Aggregation check
    res = herald.execute_action("aggregate_summary", {})
    events = res["summary"]
    
    # Should find at least 3 events: 1 alert, 1 task, 1 patch
    event_types = [e["type"] for e in events]
    assert "TEST_ALERT" in event_types
    assert "HITL_TASK" in event_types
    assert "AIRLOCK_PENDING" in event_types

def test_herald_deduplication(state):
    """Verify Herald doesn't relay the same event twice."""
    herald = HeraldPlugin("test-herald", {})
    
    # 1. Mock alert
    with open("ALERT.md", "w") as f:
        f.write("## [DEDUP_TEST] 2026-03-22 20:00:00\nContent\n\n")
    
    # 2. Relay first time
    res1 = herald.execute_action("relay_new_events", {})
    assert res1["relayed_count"] >= 1
    
    # 3. Relay second time - should be 0 new events
    res2 = herald.execute_action("relay_new_events", {})
    assert res2["relayed_count"] == 0
