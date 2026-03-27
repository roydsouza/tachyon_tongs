import os
import time
import sqlite3
import pytest
from agents.chronicle.agent import ChroniclePlugin
from tachyon.core.state import StateManager

def reset_state_manager():
    """Forces the StateManager singleton to re-initialize."""
    StateManager._instance = None
    if hasattr(StateManager, "__setattr__"):
        try:
            del StateManager.__setattr__
        except AttributeError:
            pass

def test_chronicle_velocity_anomaly():
    """
    Verifies that Chronicle detects an agent performing too many actions too quickly.
    """
    reset_state_manager()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_db = os.path.join(root_dir, "tests", "tmp", "test_chronicle_velocity.db")
    if os.path.exists(test_db): os.remove(test_db)
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    alert_path = os.path.join(root_dir, "ALERT.md")
    
    # Backup ALERT.md
    original_alert = ""
    if os.path.exists(alert_path):
        with open(alert_path, "r") as f:
            original_alert = f.read()

    try:
        # 1. Setup StateManager and Chronicle
        os.environ["TACHYON_TEST_MODE"] = "1"
        sm = StateManager(db_path=test_db)
        
        chronicle = ChroniclePlugin(
            agent_id="chronicle-monitor",
            config={}
        )
        
        # 2. Simulate high velocity (21 events in a burst)
        # Each call to _on_agent_activity logs and analyzes
        for i in range(21):
            chronicle._on_agent_activity({
                "agent_id": "busy-agent",
                "topic": "COMMAND_EXECUTION",
                "details": {"cmd": f"echo {i}"}
            })
            
        # 3. Verify ALERT.md
        with open(alert_path, "r") as f:
            content = f.read()
            assert "[TEMPORAL_ANOMALY]" in content
            assert "busy-agent" in content
            assert "VELOCITY_VIOLATION" in content
            
    finally:
        if os.path.exists(test_db): os.remove(test_db)
        with open(alert_path, "w") as f:
            f.write(original_alert)

def test_chronicle_role_drift():
    """
    Verifies that Chronicle detects a non-engineer agent proposing patches.
    """
    reset_state_manager()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_db = os.path.join(root_dir, "tests", "tmp", "test_chronicle_drift.db")
    if os.path.exists(test_db): os.remove(test_db)
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    alert_path = os.path.join(root_dir, "ALERT.md")
    
    try:
        sm = StateManager(db_path=test_db)
        chronicle = ChroniclePlugin(agent_id="chronicle-monitor", config={})
        
        # 1. Simulate actor 'scout' proposing a patch
        chronicle._on_agent_activity({
            "agent_id": "scout",
            "topic": "PATCH_PROPOSED",
            "details": {"patch_id": "CVE-2024-9999"}
        })
        
        # 2. Verify ALERT.md
        with open(alert_path, "r") as f:
            content = f.read()
            assert "ROLE_DRIFT" in content
            assert "scout" in content
            
    finally:
        if os.path.exists(test_db): os.remove(test_db)
