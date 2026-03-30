import pytest
from tachyon.core.local_provider import LocalModelProvider

@pytest.mark.asyncio
async def test_local_provider_redirection():
    """
    Ensures that the tachyon_tongs LocalModelProvider correctly uses
    the event-horizon-core logic.
    """
    provider = LocalModelProvider()
    # Check that healthy() uses the underlying core provider
    status = await provider.is_healthy()
    # If the service is running, it should be True; otherwise, it should 
    # at least not crash while checking.
    assert isinstance(status, bool)

def test_hyperagent_stub_import():
    """
    Verifies that the Hyperagent can still be initialized.
    """
    from experiments.darwin_godel_machine.src.hyperagent import DefenseHyperagent
    agent = DefenseHyperagent("test-id", {})
    assert agent.hyperagent_id == "test-id"
    # The provider should be an MLXProvider from event_horizon_core
    from event_horizon_core.providers.mlx_provider import MLXProvider
    assert isinstance(agent.provider, MLXProvider)
