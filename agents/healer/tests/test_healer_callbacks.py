import pytest
from unittest.mock import MagicMock, patch
from agents.healer.agent import HealerPlugin

def test_healer_callback_success():
    """TDAD: This test should now PASS after GW-01 fix."""
    mock_bus = MagicMock()
    payload = {"cve_id": "GHSA-mcp-v1", "sender": "engineer-001"}
    
    healer = HealerPlugin(agent_id="healer-test", config={})
    healer.bus = mock_bus
    
    # This should NOT raise TypeError
    healer._on_patch_proposed(payload)
    
    # Verify emit_event was called with the certificate
    mock_bus.emit_event.assert_called_once()
    args, kwargs = mock_bus.emit_event.call_args
    assert kwargs["topic"] == "TELEMETRY"
    assert kwargs["certificate"] == healer.certificate

def test_healer_integrity_violation_success():
    """TDAD: This test should now PASS after GW-01 fix."""
    payload = {"reason": "Unauthorized file access", "sender": "guardian-001"}
    healer = HealerPlugin(agent_id="healer-test", config={})
    
    # This should NOT raise TypeError
    healer._on_integrity_violation(payload)
