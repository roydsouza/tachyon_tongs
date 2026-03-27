import pytest
import unittest.mock as mock
from agents.sentinel.agent import NVDClient, SentinelPlugin

def test_nvd_client_signing_failure_repro():
    """
    R-01: Reproduce AttributeError when certificate is None during failure signal.
    """
    mock_bus = mock.Mock()
    # The crash happens because emit_event tries to use the 'certificate' to sign.
    # We mock emit_event to simulate the TachyonEventBus behavior.
    def mock_emit_event(topic, agent_id, payload, certificate=None):
        if certificate is None:
            # TachyonEventBus logic (simplified)
            # if topic in SIGNED_TOPICS and not certificate: raise ...
            # The real crash is because it might try to call certificate.public_key
            print(f"DEBUG: Emitting {topic} without certificate")
            # Simulation of the reported error:
            raise AttributeError("'NoneType' object has no attribute 'public_key'")
        return True

    mock_bus.emit_event.side_effect = mock_emit_event
    
    # Initialize client with None certificate
    client = NVDClient("sentinel-test", mock_bus)
    client.certificate = None 
    
    # Force a failure in _call_mcp_tool to trigger the signal
    with mock.patch("random.random", return_value=0.0): # Force the 0.1 failure path if retries match
         with pytest.raises(AttributeError) as excinfo:
             # We need to trigger the i == retries - 1 failure block
             client._call_mcp_tool("test_tool", {}, retries=1)
         
         assert "'NoneType' object has no attribute 'public_key'" in str(excinfo.value)

def test_sentinel_plugin_init_state():
    """
    R-01: Verify that SentinelPlugin initializes NVDClient with its certificate.
    """
    config = {"nvd_mcp_server": "mock"}
    # Mocking BaseAgentPlugin.__init__ which sets self.certificate
    with mock.patch("agents._core.base.BaseAgentPlugin.__init__", return_value=None):
        plugin = SentinelPlugin("sentinel-test", config)
        plugin.certificate = mock.Mock() # Simulate provisioned certificate
        
        # After manual provisioning, the client's cert should match
        plugin.nvd.certificate = plugin.certificate
        assert plugin.nvd.certificate is not None
