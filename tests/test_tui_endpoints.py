import os
import sqlite3
import pytest
from tachyon.core.state import StateManager

def reset_state_manager():
    StateManager._instance = None

# Set environment before any imports that might trigger StateManager
os.environ["TACHYON_TEST_MODE"] = "1"

def test_forensics_endpoint():
    """
    Verifies that GET /api/v1/forensics returns the correct forensic events.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_db = os.path.join(root_dir, "tests", "tmp", "test_tui_api.db")
    if os.path.exists(test_db): os.remove(test_db)
    
    os.environ["TACHYON_DB_PATH"] = test_db
    reset_state_manager()
    from tachyon.api.server import app
    from fastapi.testclient import TestClient
    
    try:
        # 1. Setup StateManager and log a fake event
        sm = StateManager(db_path=test_db)
        sm.log_forensic_event("tester", "TEST_ALERT", "Details of the test alert")
        
        # 2. Query the API (Force new client to ensure new Bridge)
        client = TestClient(app)
        response = client.get("/api/v1/forensics")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        alert = data[0]
        assert alert["agent_id"] == "tester"
        assert alert["topic"] == "TEST_ALERT"
        
    finally:
        if os.path.exists(test_db): os.remove(test_db)

def test_substrate_health_with_forensics():
    """
    Verifies that the status endpoint still works and returns basic health.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_db = os.path.join(root_dir, "tests", "tmp", "test_tui_health.db")
    if os.path.exists(test_db): os.remove(test_db)
    
    reset_state_manager()
    from tachyon.api.server import app
    from fastapi.testclient import TestClient
    
    try:
        sm = StateManager(db_path=test_db)
        client = TestClient(app)
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "integrity_verified" in data
        
    finally:
        if os.path.exists(test_db): os.remove(test_db)
