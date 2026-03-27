import os
import time
import pytest
from typing import Dict, Any
from agents._core.base import BaseAgentPlugin
from tachyon.core.state import StateManager

class MockFailAgent(BaseAgentPlugin):
    """A mock agent that specifically fails actions for testing."""
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "fail_soft":
            return {"status": "ERROR", "message": "Simulated soft failure"}
        elif action == "crash":
            raise RuntimeError("Simulated hard crash")
        return {"status": "SUCCESS"}

def test_agent_action_fail_loud():
    """
    Verifies that an agent failing an action writes to ALERT.md.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    alert_path = os.path.join(root_dir, "ALERT.md")
    
    # Backup ALERT.md if it exists
    original_content = ""
    if os.path.exists(alert_path):
        with open(alert_path, "r") as f:
            original_content = f.read()

    try:
        # 1. Setup Agent
        agent = MockFailAgent(
            agent_id="test-fail-agent",
            plugin_name="FailPlugin",
            config={"quarantine_mode": True}
        )
        
        # 2. Trigger Soft Failure
        agent.run_action("fail_soft", {})
        
        # 3. Verify ALERT.md
        with open(alert_path, "r") as f:
            content = f.read()
            assert "[AGENT_ACTION_ERROR]" in content
            assert "test-fail-agent" in content
            assert "Simulated soft failure" in content
            
        # 4. Trigger Hard Crash
        agent.run_action("crash", {})
        
        # 5. Verify ALERT.md again
        with open(alert_path, "r") as f:
            content = f.read()
            assert "Simulated hard crash" in content
            
    finally:
        # Restore ALERT.md
        with open(alert_path, "w") as f:
            f.write(original_content)

def test_agent_backplane_crash_fail_loud():
    """
    Verifies that a background loop crash triggers an alert.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    alert_path = os.path.join(root_dir, "ALERT.md")
    
    # 1. Setup Agent
    agent = MockFailAgent(
        agent_id="test-backplane-agent",
        plugin_name="BackplanePlugin",
        config={}
    )
    
    # 2. Manually trigger the _backplane_loop exception path
    # We mock _subscriptions to cause an error during iteration
    # 2. Manually trigger the _backplane_loop exception path
    # We mock _subscriptions to cause an error during iteration
    agent._subscriptions = None # Will cause AttributeError
    
    # We want to run ONLY ONE iteration. 
    # But _backplane_loop is a while loop.
    # To test the error path, we can't easily run it once if it crashes immediately.
    # Actually, if it crashes, it hits the 'except' and THEN continues to the end of the loop body.
    # We need to set the stop_event INSIDE the loop or just mock the while.
    
    # Better: Patch the while loop or just rely on the crash to exit the process? No, it's a test.
    # Let's just call the loop once in a thread and then set the event.
    
    import threading
    t = threading.Thread(target=agent._backplane_loop, args=(0.01,))
    t.start()
    time.sleep(0.05) # Wait for crash and alert emission
    agent._stop_event.set()
    t.join()
        
    # Verify ALERT.md
    with open(alert_path, "r") as f:
        content = f.read()
        assert "[AGENT_BACKPLANE_CRASH]" in content
        assert "test-backplane-agent" in content
