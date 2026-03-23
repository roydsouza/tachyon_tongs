import pytest
import os
import time
from tachyon.core.state import StateManager

@pytest.fixture
def state():
    db_path = "test_lock.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    os.environ["TACHYON_DB_PATH"] = db_path
    manager = StateManager(db_path)
    yield manager
    if os.path.exists(db_path):
        os.remove(db_path)

def test_mutant_lock_lifecycle(state):
    """Verify lock acquisition, check, and release."""
    agent_id = "test-engineer"
    
    # 1. Acquire lock
    lock_id = state.acquire_mutant_lock(agent_id, "Applying critical patch")
    assert lock_id is not None
    
    # 2. Verify active
    assert state.is_mutant_lock_active() is True
    
    # 3. Release lock
    state.release_mutant_lock(lock_id)
    assert state.is_mutant_lock_active() is False

def test_mutant_lock_expiry(state):
    """Verify that locks expire (mocked clock)."""
    # Initialize the table by ensuring the state object has run _init_db
    # (The state fixture already does this)
    import sqlite3
    from datetime import datetime, timedelta
    
    expired_time = (datetime.now() - timedelta(minutes=10)).isoformat()
    
    with sqlite3.connect(state.db_path) as conn:
        conn.execute('''
            INSERT INTO mutant_locks (lock_id, agent_id, reason, acquired_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ("expired-lock", "stale-agent", "forgot to release", expired_time, expired_time))
        conn.commit()
    
    # Should be False because it's expired
    assert state.is_mutant_lock_active() is False
