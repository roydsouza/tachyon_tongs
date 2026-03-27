import pytest
import os
from unittest.mock import MagicMock, patch
from agents.sentry.agent import SentryPlugin

def test_sentry_alert_signature_success():
    """TDAD: This test verifies that the Sentry agent now emits a signed alert."""
    mock_bus = MagicMock()
    sentry = SentryPlugin(agent_id="sentry-test", config={})
    sentry.bus = mock_bus
    
    with patch.object(sentry.engine, 'check_bait', return_value=True):
        sentry.check_signals()
    
    mock_bus.emit_event.assert_called_once()
    args, kwargs = mock_bus.emit_event.call_args
    
    assert kwargs.get("certificate") == sentry.certificate
    assert "signature" not in kwargs
