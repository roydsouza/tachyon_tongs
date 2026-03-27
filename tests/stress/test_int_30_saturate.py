import time
import uuid
import random
from tachyon.core.telemetry import TelemetryBus
from tachyon.core.forensics import ForensicStore

def stress_test(duration_seconds=5, events_per_second=1000):
    bus = TelemetryBus()
    store = ForensicStore()
    start_time = time.time()
    count = 0
    
    print(f"Starting stress test: {events_per_second} EPS for {duration_seconds}s...")
    
    while time.time() - start_time < duration_seconds:
        for _ in range(events_per_second):
            bus.emit_event(
                event_type="STRESS_TEST",
                agent_id=f"agent_{random.randint(1, 10)}",
                details={"nonce": count, "blob": "X" * 100},
                source=random.choice(["internal", "transit"])
            )
            count += 1
        time.sleep(1)
        
    end_time = time.time()
    actual_duration = end_time - start_time
    print(f"Emitted {count} events in {actual_duration:.2f}s ({count/actual_duration:.1f} EPS)")
    
    # Verify we can still query
    latest = store.query_latest(limit=10)
    print(f"Query check: {len(latest)} events retrieved.")
    assert len(latest) == 10

if __name__ == "__main__":
    stress_test()
