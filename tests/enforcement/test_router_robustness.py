import pytest
import asyncio
from tachyon.enforcement.router import ToolRouter, ImmutableToolRequest

class MockSandbox:
    async def execute(self, command, env):
        return {"stdout": f"executed: {command}"}

class MockOrchestrator:
    async def fetch_and_sanitize(self, url, agent_id):
        return {"content": "sanitized content"}

class MockPolicyEngine:
    def is_action_allowed(self, agent_id, action, params):
        return True

class MockMonitor:
    def log_and_evaluate(self, agent_id, action):
        pass

@pytest.mark.asyncio
async def test_router_toctou_resistance():
    """Verify that parameters are frozen and cannot be mutated after the request is created."""
    router = ToolRouter(
        MockOrchestrator(), 
        MockSandbox(), 
        MockPolicyEngine(), 
        MockMonitor(), 
        MockMonitor()
    )
    
    params = {"command": "ls"}
    # The route method will create an ImmutableToolRequest
    # We want to ensure that even if the original params dict is modified,
    # the request execution uses the frozen state.
    
    # Actually, the current implementation takes the dict and puts it in the frozen dataclass.
    # In Python, the dict itself is still mutable unless we deep-copy it.
    # Let's ensure the router uses the values from the request.
    
    request = ImmutableToolRequest(agent_id="test", action="safe_execute", params=params)
    
    # Attempt mutation of the original dictionary
    params["command"] = "rm -rf /"
    
    # Verify the request remains original because it was frozen on initialization
    assert request.params["command"] == "ls"
    
    # Verify direct mutation raises TypeError (MappingProxyType)
    with pytest.raises(TypeError):
        request.params["command"] = "rm -rf /"
    
@pytest.mark.asyncio
async def test_router_parameter_validation():
    """Verify that router handles unknown actions gracefully."""
    router = ToolRouter(
        MockOrchestrator(), 
        MockSandbox(), 
        MockPolicyEngine(), 
        MockMonitor(), 
        MockMonitor()
    )
    
    result = await router.route("agent", "unknown_tool", {})
    assert result["status"] == "ERROR"
    assert "Unknown action" in result["error"]
