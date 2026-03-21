import os
import json
import pytest
import tempfile
from unittest.mock import patch, mock_open
from tachyon.core.telemetry import TelemetryBus

@pytest.fixture
def edge_telemetry_file():
    """Creates a temporary file for telemetry edge testing."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)

def test_telemetry_corruption_recovery(edge_telemetry_file):
    """Verify that get_events skips malformed JSON lines without crashing."""
    TelemetryBus._instance = None
    bus = TelemetryBus(log_path=edge_telemetry_file)
    
    # Write one valid, one corrupt, then one valid line
    valid_1 = {"timestamp": "2026-03-20T10:00:00", "event_type": "TEST", "agent_id": "a1", "status": "OK"}
    valid_2 = {"timestamp": "2026-03-20T10:01:00", "event_type": "TEST", "agent_id": "a2", "status": "OK"}
    
    with open(edge_telemetry_file, "a") as f:
        f.write(json.dumps(valid_1) + "\n")
        f.write("{NOT_JSON_AT_ALL}\n")
        f.write(json.dumps(valid_2) + "\n")
        
    events = bus.get_events()
    assert len(events) == 2
    assert events[0]["agent_id"] == "a1"
    assert events[1]["agent_id"] == "a2"

def test_telemetry_large_payload(edge_telemetry_file):
    """Verify that the bus handles large (1MB+) payloads without fcntl/lock failure."""
    TelemetryBus._instance = None
    bus = TelemetryBus(log_path=edge_telemetry_file)
    
    large_data = "X" * (1024 * 1024) # 1MB string
    bus.emit_event(
        event_type="STRESS_TEST",
        agent_id="heavy_agent",
        details={"blob": large_data}
    )
    
    events = bus.get_events()
    assert len(events) == 1
    assert len(events[0]["details"]["blob"]) == (1024 * 1024)

def test_telemetry_io_failure_fallback(edge_telemetry_file):
    """Verify that TelemetryBus falls back to stderr if the disk is full/unwritable."""
    TelemetryBus._instance = None
    bus = TelemetryBus(log_path=edge_telemetry_file)
    
    # Mock 'open' to raise an OSError
    with patch("builtins.open", side_effect=OSError("Permission Denied")):
        with patch("sys.stderr.write") as mock_stderr_write:
            bus.emit_event("FAIL_TEST", "agent_01", status="CRITICAL")
            
            # Check if it tried to write to stderr (print calls write)
            mock_stderr_write.assert_called()
            # Verify the content
            call_args = "".join(str(call.args[0]) for call in mock_stderr_write.call_args_list)
            assert "[TelemetryBus] FAILED TO WRITE EVENT" in call_args

def test_telemetry_get_events_file_not_found():
    """Verify get_events handles a missing log file gracefully."""
    TelemetryBus._instance = None
    bus = TelemetryBus(log_path="/tmp/non_existent_file_9999.jsonl")
    assert bus.get_events() == []
