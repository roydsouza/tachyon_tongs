import pytest
from unittest.mock import MagicMock, patch
from agents.engineer.agent import EngineerPlugin, AutoPatcher

def test_engineer_test_failure_emission():
    """TDAD: This test verifies that Engineer emits ENGINEER_TEST_FAILURE on test failure."""
    mock_bus = MagicMock()
    mock_bus.certificate = "ENGINEER-CERT"
    config = {}
    engineer = EngineerPlugin(agent_id="engineer-test", config=config)
    engineer.bus = mock_bus
    
    # Mock AutoPatcher to return FAILURE
    with patch.object(engineer.patcher, 'apply_and_test', return_value={"status": "FAILURE", "error": "Test regression detected"}):
        engineer.execute_action("apply_and_test", {"cve_id": "CVE-TEST-001"})
    
    # Verify emission
    failures = [call for call in mock_bus.emit_event.call_args_list if call.kwargs.get('topic') == "ENGINEER_TEST_FAILURE"]
    assert len(failures) == 1, "ENGINEER_TEST_FAILURE was not emitted on failure!"
    assert failures[0].kwargs['certificate'] == "ENGINEER-CERT"
    assert failures[0].kwargs['payload']['error'] == "Test regression detected"

def test_engineer_event_signing():
    """TDAD: This test verifies that all Engineer events are signed."""
    mock_bus = MagicMock()
    mock_bus.certificate = "ENGINEER-CERT"
    engineer = EngineerPlugin(agent_id="engineer-test", config={})
    engineer.bus = mock_bus
    
    with patch.object(engineer.patcher, 'apply_and_test', return_value={"status": "SUCCESS"}):
        engineer.execute_action("apply_and_test", {"cve_id": "CVE-TEST-002"})
    
    # In current state, ENGINEER_PATCH_APPLIED (or similar) might be missing or unsigned
    # Wait, the current code doesn't emit ANY events in execute_action success path except what's in BaseAgentPlugin.
    # We want it to emit ENGINEER_PATCH_COMPLETED.
    
    completions = [call for call in mock_bus.emit_event.call_args_list if call.kwargs.get('topic') == "ENGINEER_PATCH_COMPLETED"]
    assert len(completions) == 1, "ENGINEER_PATCH_COMPLETED was not emitted!"
    assert completions[0].kwargs['certificate'] == "ENGINEER-CERT"
