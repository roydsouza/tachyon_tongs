import pytest
import time
from fastapi.testclient import TestClient
from tachyon.api.server import app
from tachyon.core.telemetry import TelemetryBus

def test_websocket_event_delivery():
    """INT-03: Verify that telemetry events are pushed to WebSocket clients."""
    # TestClient as a context manager ensures 'lifespan' (telemetry_broadcaster) runs
    with TestClient(app) as client:
        with client.websocket_connect("/api/v1/logs/stream") as websocket:
            bus = TelemetryBus()
            
            # Use a unique message to avoid interference from other events
            unique_msg = f"WS-TEST-{time.time()}"
            
            # Emit a test event
            bus.emit_event(
                event_type="TEST_EVENT",
                agent_id="test-agent",
                action="STREAM_TEST",
                details={"message": unique_msg},
                source="internal"
            )
            
            # The broadcaster polls every 0.5s.
            # We'll try to receive with a timeout.
            # TestClient.websocket_connect's receive_json doesn't have a timeout?
            # It uses starlette's WebSocket which blocks.
            
            data = websocket.receive_json()
            # If there were other events in the pipe, we might need to loop.
            # But query_after(last_id) should start from the latest.
            
            # Check if it's our event
            if data["event_type"] == "TEST_EVENT" and data["details"].get("message") == unique_msg:
                assert True
            else:
                # Try one more just in case of a heartbeat or concurrent event
                data = websocket.receive_json()
                assert data["event_type"] == "TEST_EVENT"
                assert data["details"]["message"] == unique_msg
