import pytest
from unittest.mock import MagicMock, patch
from agents.sentinel.agent import SentinelPlugin, NVDClient

def test_sentinel_signing_success():
    """TDAD: This test verifies that Sentinel now emits signed events."""
    mock_bus = MagicMock()
    # Mock certificate
    mock_bus.certificate = "MOCK-CERT"
    config = {}
    sentinel = SentinelPlugin(agent_id="sentinel-test", config=config)
    sentinel.bus = mock_bus
    sentinel.nvd.bus = mock_bus
    
    # Trigger a hunt
    with patch.object(sentinel.nvd, '_call_mcp_tool', return_value={"status": "SUCCESS", "cves": []}):
        sentinel.execute_action("hunt", {"mode": "test"})
    
    # Verify events
    emissions = mock_bus.emit_event.call_args_list
    assert len(emissions) >= 2 # SCAN_STARTED and SCAN_COMPLETED
    
    # Every event must have a certificate
    for call in emissions:
        _, kwargs = call
        assert kwargs.get("certificate") is not None, f"Event {kwargs.get('topic')} is missing a certificate!"

def test_sentinel_keyword_failure_emission():
    """TDAD: This test verifies that Sentinel now emits per-keyword failures."""
    mock_bus = MagicMock()
    sentinel = SentinelPlugin(agent_id="sentinel-test", config={})
    sentinel.bus = mock_bus
    sentinel.nvd.bus = mock_bus
    
    def mock_call(tool, args):
        if args.get("keyword") == "LLM":
            raise ValueError("Simulated NVD failure")
        return {"status": "SUCCESS", "cves": []}
        
    with patch.object(sentinel.nvd, '_call_mcp_tool', side_effect=mock_call):
        sentinel.nvd.hunt_new_threats(certificate="TEST-CERT")
    
    # Verify keyword failure emission
    keyword_failures = [call for call in mock_bus.emit_event.call_args_list if call.kwargs.get('topic') == "SENTINEL_KEYWORD_FAILURE"]
    assert len(keyword_failures) == 1
    assert keyword_failures[0].kwargs['payload']['keyword'] == "LLM"
    assert keyword_failures[0].kwargs['certificate'] == "TEST-CERT"
