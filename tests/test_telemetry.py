import os
import json
import pytest
import tempfile
import threading
from tachyon.core.telemetry import TelemetryBus

@pytest.fixture
def temp_telemetry_bus():
    """Provides a fresh TelemetryBus instance pointing to a temp file."""
    # Reset singleton
    TelemetryBus._instance = None
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        path = f.name
    
    bus = TelemetryBus(log_path=path)
    yield bus
    
    # Cleanup
    TelemetryBus._instance = None
    if os.path.exists(path):
        os.unlink(path)

def test_telemetry_singleton():
    """Verify TelemetryBus acts as a singleton."""
    TelemetryBus._instance = None
    b1 = TelemetryBus("/tmp/test1.jsonl")
    b2 = TelemetryBus("/tmp/test2.jsonl")
    assert b1 is b2
    assert b1.log_path == "/tmp/test1.jsonl"
    TelemetryBus._instance = None

def test_telemetry_emit_and_get(temp_telemetry_bus):
    """Verify writing and reading structured events."""
    bus = temp_telemetry_bus
    
    bus.emit_event(
        event_type="TOOL_CALL",
        agent_id="sentinel",
        action="safe_execute",
        status="BLOCKED",
        details={"reason": "PDP_DENY"}
    )
    
    events = bus.get_events()
    assert len(events) == 1
    
    evt = events[0]
    assert evt["event_type"] == "TOOL_CALL"
    assert evt["agent_id"] == "sentinel"
    assert evt["action"] == "safe_execute"
    assert evt["status"] == "BLOCKED"
    assert evt["details"]["reason"] == "PDP_DENY"
    assert "timestamp" in evt

def test_telemetry_concurrent_writes(temp_telemetry_bus):
    """Verify atomic writes handle concurrency via flock without corruption."""
    bus = temp_telemetry_bus
    
    def worker(agent_id, count):
        for i in range(count):
            bus.emit_event(
                event_type="STRESS_TEST",
                agent_id=str(agent_id),
                action="test",
                status="INFO",
                details={"seq": i}
            )

    threads = []
    num_threads = 10
    writes_per_thread = 50
    
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i, writes_per_thread))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    events = bus.get_events(limit=1000) # Should be 500 total
    assert len(events) == (num_threads * writes_per_thread)
    
    # Verify no corruption by checking required keys
    for evt in events:
        assert evt["event_type"] == "STRESS_TEST"
        assert "seq" in evt["details"]
