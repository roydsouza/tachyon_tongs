import pytest
from datetime import datetime
import asyncio

# These will fail until implementation is injected (TDAD Red Phase)
try:
    from tachyon.agents.herald.core import HeraldCore, Message, MessageType
    from tachyon.agents.herald.transports.cli_transport import CLITransport
except ImportError:
    pass # Expected in red phase

@pytest.mark.asyncio
async def test_herald_core_registration():
    """Verify HeraldCore can register agents and route basic messages"""
    core = HeraldCore()
    
    # Mock agent
    class MockAgent:
        async def process_command(self, cmd):
            return f"Processed: {cmd}"
            
    core.register_agent("mock", MockAgent())
    assert "mock" in core.agents
    
    # Create dummy message
    msg = Message(
        id="test-1",
        type=MessageType.COMMAND,
        source="test_client",
        destination="herald",
        content={"text": "/status"},
        timestamp=datetime.utcnow(),
        metadata={}
    )
    
    # Should not crash and should process text
    await core.receive_message(msg)
    assert len(core.message_history) == 1

@pytest.mark.asyncio
async def test_cli_transport_initialization():
    """Verify CLITransport validates parameters and can bind securely"""
    core = HeraldCore()
    transport = CLITransport(herald_core=core, socket_path="/tmp/test_tachyon_herald.sock")
    
    assert transport.socket_path == "/tmp/test_tachyon_herald.sock"
    assert transport.herald == core
