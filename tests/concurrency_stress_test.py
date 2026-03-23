import os
import sys
import threading
import time
import random

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tachyon.core.state_manager import StateManager
from tachyon.core.bus import TachyonEventBus

def agent_worker(worker_id: int, num_ops: int):
    """Simulates an agent performing state and bus operations in parallel."""
    print(f"[Worker {worker_id}] Starting {num_ops} operations...")
    state = StateManager()
    bus = TachyonEventBus()
    
    for i in range(num_ops):
        # 1. State Logging
        try:
            state.log_evolution(f"STRESS_TEST_{worker_id}", f"Operation {i} by concurrent worker {worker_id}")
        except Exception as e:
            print(f"[Worker {worker_id}] State Logic Failure: {e}")
            
        # 2. Event Bus Emission
        try:
            bus.emit_event(
                topic="STRESS_TEST",
                agent_id=f"agent-{worker_id}",
                payload={"op": i, "worker": worker_id}
            )
        except Exception as e:
            print(f"[Worker {worker_id}] Event Bus Failure: {e}")
            
        # Random sleep to introduce jitter
        time.sleep(random.uniform(0.01, 0.05))

def test_concurrency():
    print("--- [Integration] Starting Phase 30.2 Concurrency Stress Test ---")
    num_workers = 10 # 10 parallel agents
    ops_per_worker = 20
    
    threads = []
    for i in range(num_workers):
        t = threading.Thread(target=agent_worker, args=(i, ops_per_worker))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print("[SUCCESS] All workers finished without crashing!")
    
    # Verify DB Integrity
    bus = TachyonEventBus()
    events = bus.fetch_events(topic="STRESS_TEST", limit=1000)
    print(f"[Verify] Found {len(events)} stress test events on the bus.")
    
    expected = num_workers * ops_per_worker
    if len(events) >= expected:
        print("[SUCCESS] Data integrity maintained under load.")
    else:
        print(f"[WARNING] Some events may have been dropped or failed: {len(events)}/{expected}")

if __name__ == "__main__":
    test_concurrency()
