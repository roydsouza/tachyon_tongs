import pytest
import time
from unittest.mock import MagicMock, patch
from tachyon.core.wasm_benchmark import WasmToolRunner, FuelExhaustedError, EpochTimeoutError
from tachyon.core.bus import TachyonEventBus

# --- S-03: WASM Isolation Tests ---

def test_wasm_fuel_exhaustion():
    """Verify that an infinite logic loop is killed by fuel depletion."""
    runner = WasmToolRunner(fuel_limit=1000)
    
    # Simulate a binary that triggers an infinite loop
    result = runner.execute_tool(b"binary_with_infinite_loop", "input")
    
    assert result["status"] == "error"
    assert "Fuel limit exceeded" in result["error"]
    assert result["fuel_consumed"] > 1000

def test_epoch_interruption():
    """Verify that a long-running execution is killed by the wall-clock watchdog."""
    # Set a very short timeout for the test
    runner = WasmToolRunner(timeout=0.1)
    
    # Simulate a binary that triggers a sleep/hang
    result = runner.execute_tool(b"binary_with_sleep_attack", "input")
    
    assert result["status"] == "error"
    assert "Execution exceeded timeout" in result["error"]

def test_wasm_sandbox_violation():
    """Verify blocked capability access."""
    runner = WasmToolRunner()
    result = runner.execute_tool(b"binary_with_malicious_sys_call", "input")
    assert result["status"] == "error"
    assert "denied" in result["error"]

# --- S-04: EventBus Loop Guard Tests ---

def test_loop_breaker_identical_events():
    """Verify that identical event floods are suppressed (Consensus Ceiling)."""
    # Use a temporary DB for the bus
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_bus.db")
        bus = TachyonEventBus(db_path=db_path)
        
        topic = "HEARTBEAT"
        payload = {"status": "OK"}
        
        # 1. First 3 events should pass
        for i in range(3):
            event_id = bus.emit_event(topic, "agent-001", payload)
            assert event_id > 0
            
        # 2. 4th event should be suppressed by Loop Guard
        from tachyon.core.state import StateManager
        with patch.object(StateManager, 'emit_alert') as mock_alert:
            event_id = bus.emit_event(topic, "agent-001", payload)
            assert event_id == -1
            assert mock_alert.called
            args, _ = mock_alert.call_args
            assert args[0] == "SECURITY_ALERT_LOOP"
            assert "LOOP DETECTED" in args[1]

def test_loop_guard_window_reset():
    """Verify that the loop guard allows events after the window expires."""
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_bus_reset.db")
        bus = TachyonEventBus(db_path=db_path)
        bus.LOOP_WINDOW_SEC = 0.5 # Very short window
        
        topic = "HEARTBEAT"
        payload = {"status": "OK"}
        
        # Fill the threshold
        for _ in range(3):
            bus.emit_event(topic, "agent-001", payload)
            
        # Verify suppression
        assert bus.emit_event(topic, "agent-001", payload) == -1
        
        # Wait for window to expire
        time.sleep(0.6)
        
        # Next event should pass
        assert bus.emit_event(topic, "agent-001", payload) > 0
