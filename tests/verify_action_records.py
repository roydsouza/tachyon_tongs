import os
import sys
import json
import time

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents._core.base import BaseAgentPlugin
from tachyon.core.bus import TachyonEventBus

class TestAgent(BaseAgentPlugin):
    """Simple agent for Phase 33 verification."""
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "sum":
            a = parameters.get("a", 0)
            b = parameters.get("b", 0)
            return {"status": "SUCCESS", "result": a + b}
        return {"status": "ERROR", "message": "Unknown action"}

def verify_action_records():
    print("--- [Phase 33] Verifying ActionRecord Generation ---")
    
    # 1. Setup
    agent = TestAgent(agent_id="test-agent-001", plugin_name="VerificationAgent", config={})
    
    # 2. Run Action
    print("[Test] Running 'sum' action via run_action()...")
    result = agent.run_action("sum", {"a": 10, "b": 20})
    print(f"[Result] {result}")
    
    # 3. Verify Event Bus
    bus = TachyonEventBus()
    
    # Check ACTION_START
    start_events = bus.fetch_events(topic="ACTION_START")
    print(f"[Verify] Found {len(start_events)} ACTION_START events.")
    
    # Check ACTION_COMPLETED
    completed_events = bus.fetch_events(topic="ACTION_COMPLETED")
    print(f"[Verify] Found {len(completed_events)} ACTION_COMPLETED events.")
    
    if len(completed_events) > 0:
        event = completed_events[-1]
        payload = json.loads(event['payload_json'])
        print(f"[Verify] ActionRecord ID: {payload['action_id']}")
        print(f"[Verify] Status: {payload['status']}")
        
        signature = event['signature']
        if signature:
            print(f"[SUCCESS] ActionRecord is SIGNED! (Sig: {signature[:16]}...)")
        else:
            print("[FAILURE] ActionRecord is NOT signed.")
            sys.exit(1)
            
        if payload['result']['result'] == 30:
            print("[SUCCESS] Action result is correct in the record.")
        else:
            print(f"[FAILURE] Action result mismatch: {payload['result']}")
            sys.exit(1)
    else:
        print("[FAILURE] No completed events found on the bus.")
        sys.exit(1)

if __name__ == "__main__":
    verify_action_records()
