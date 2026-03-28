import pytest
import os
import importlib
from tachyon.core.state import StateManager

herald_mod = importlib.import_module("agents.herald.agent")
HeraldPlugin = herald_mod.HeraldPlugin

@pytest.fixture
def state():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_herald.db")
        os.environ["TACHYON_DB_PATH"] = db_path
        from tachyon.core.state import StateManager
        StateManager._instance = None
        manager = StateManager(db_path)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS patches (id TEXT, summary TEXT, status TEXT, cve_id TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS relayed_events (dispatcher_id TEXT, event_id TEXT, relayed_at TEXT, PRIMARY KEY (dispatcher_id, event_id))")
            conn.execute("CREATE TABLE IF NOT EXISTS forensic_events (id INTEGER PRIMARY KEY, agent_id TEXT, action TEXT, status TEXT, details TEXT, timestamp TEXT, event_type TEXT)")
            conn.commit()
        yield manager
        # Purge singleton again to prevent pollution
        StateManager._instance = None

def test_herald_aggregation_logic(state):
    """Verify Herald collects events from multiple sources."""
    herald = HeraldPlugin("test-herald", {})
    
    # 1. Mock an alert in ALERT.md
    with open("ALERT.md", "w") as f:
        f.write("# 🚨 Alerts\n\n## [TEST_ALERT] 2026-03-22 20:00:00\n> [!CAUTION]\n> Test message\n\n---\n\n")
    
    # 2. Mock a task in tasks/TASKS_CLEANUP.md
    os.makedirs("tasks", exist_ok=True)
    with open("tasks/TASKS_CLEANUP.md", "w") as f:
        f.write("- [ ] **HITL**: Review this patch\n")
        
    # 3. Simulate Airlock patch
    with state._lock:
        import sqlite3
        with sqlite3.connect(state.db_path) as conn:
            conn.execute("INSERT INTO patches (id, summary, status) VALUES ('p1', 'Fix bug', 'PENDING')")
            conn.commit()

    # 4. Aggregation check
    res = herald.execute_action("aggregate_summary", {})
    events = res.data["summary"]
    
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
    assert res1.data["relayed_count"] >= 1
    
    # 3. Relay second time - should be 0 new events
    res2 = herald.execute_action("relay_new_events", {})
    assert res2.data["relayed_count"] == 0
