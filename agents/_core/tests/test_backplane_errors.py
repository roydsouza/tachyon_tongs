import pytest
import json
from unittest.mock import MagicMock, patch
from agents._core.base import BaseAgentPlugin

class MockAgent(BaseAgentPlugin):
    def execute_action(self, action, parameters):
        return {"status": "SUCCESS"}

def test_backplane_callback_error_emission_success():
    """TDAD: This test verifies that callback exceptions now emit a bus event."""
    mock_bus = MagicMock()
    mock_bus.verify_event.return_value = True
    mock_bus.fetch_events.return_value = [{
        'id': 1,
        'topic': 'TEST_TOPIC',
        'payload_json': json.dumps({'data': 'test'})
    }]
    
    agent = MockAgent(agent_id="test-agent", plugin_name="Test", config={})
    agent.bus = mock_bus
    
    # Define a callback that raises an exception
    def crashing_callback(payload):
        raise ValueError("Simulated Callback Crash")
    
    agent.subscribe("TEST_TOPIC", crashing_callback)
    
    # Run the backplane loop once
    agent._stop_event.set()
    agent._backplane_loop(0.1)
    
    # Verify that AGENT_CALLBACK_ERROR was emitted
    error_emissions = [call for call in mock_bus.emit_event.call_args_list if call.kwargs.get('topic') == "AGENT_CALLBACK_ERROR"]
    assert len(error_emissions) == 1
    _, kwargs = error_emissions[0]
    assert kwargs["payload"]["error"] == "Simulated Callback Crash"
    assert kwargs["payload"]["error_type"] == "ValueError"
    assert kwargs["certificate"] == agent.certificate

def test_action_completed_signing_success():
    """TDAD: This test verifies that ACTION_COMPLETED events are now correctly signed with the certificate (GW-13)."""
    mock_bus = MagicMock()
    agent = MockAgent(agent_id="test-agent", plugin_name="Test", config={})
    agent.bus = mock_bus
    
    # Run an action
    agent.run_action("test_action", {})
    
    # Verify ACTION_COMPLETED emission
    completions = [call for call in mock_bus.emit_event.call_args_list if call.kwargs.get('topic') == "ACTION_COMPLETED"]
    assert len(completions) == 1
    _, kwargs = completions[0]
    assert kwargs["certificate"] == agent.certificate
    assert "signature" not in kwargs # The raw signature is now inside the payload
