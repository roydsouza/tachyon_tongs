import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock
from agents.herald.herald_agent import HeraldAgent

ALERT_PATH = "ALERT.md"

@pytest.mark.asyncio
async def test_herald_misconfig_logging_success():
    """TDAD: Verifies that Herald now records misconfigurations in ALERT.md."""
    if os.path.exists(ALERT_PATH):
        os.remove(ALERT_PATH)
        
    with patch.dict(os.environ, {}, clear=True):
        agent = HeraldAgent(agent_id="herald-test")
        agent.endpoint = None 
        await agent._broadcast_alert("CRITICAL", "Test Alert")
        
    assert os.path.exists(ALERT_PATH)
    with open(ALERT_PATH, "r") as f:
        content = f.read()
        assert "[HERALD_MISCONFIGURATION]" in content
        assert "TACHYON_HERALD_ENDPOINT is not set" in content

@pytest.mark.asyncio
async def test_herald_misconfig_telemetry_signed():
    """TDAD: Verifies that Herald misconfigurations emit signed events."""
    agent = HeraldAgent(agent_id="herald-test")
    agent.endpoint = None
    agent.certificate = "HERALD-CERT"
    mock_bus = MagicMock()
    mock_bus.certificate = "HERALD-CERT"
    agent.bus = mock_bus
    
    await agent._broadcast_alert("CRITICAL", "Test Alert")
    
    # Verify emission on bus
    emissions = mock_bus.emit_event.call_args_list
    assert len(emissions) == 1
    assert emissions[0].kwargs['topic'] == "HERALD_MISCONFIGURATION"
    assert emissions[0].kwargs['certificate'] == "HERALD-CERT"
