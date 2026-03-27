import pytest
import os
from tachyon.core.state_bridge import StateBridge

def test_statebridge_dynamic_agents():
    """INT-01: Verify that StateBridge returns all discovered agents."""
    bridge = StateBridge()
    agents = bridge.get_agents()
    
    # The current implementation (before fix) hardcodes 4 agents:
    # sentinel, engineer, guardian, canary
    
    agent_names = [a.name for a in agents]
    print(f"Discovered agents: {agent_names}")
    
    # We expect the full set of agents from the 'agents/' directory:
    # administrator, auditor, chronicle, engineer, guardian, healer, herald, 
    # pathogen, scout, sentinel, sentry, synthesizer.
    
    # Requirement from TASKS_INTERFACES.md: ≥10 agents.
    assert len(agents) >= 10, f"Expected at least 10 agents, found {len(agents)}: {agent_names}"
    
    # Verify specific roles exist that weren't in the hardcoded list
    assert "auditor" in agent_names
    assert "sentry" in agent_names
    assert "pathogen" in agent_names

def test_schema_import_integrity():
    """INT-01: Verify that ToolRequest can be instantiated (checking for import errors)."""
    # This test will fail if schema.py has the missing 'Any' import
    from tachyon.api.schema import ToolRequest
    from typing import Dict, Any
    
    req = ToolRequest(
        agent_id="test-agent",
        action="test-tool",
        parameters={"key": "value"}
    )
    assert req.agent_id == "test-agent"

def test_statebridge_new_agent_visibility():
    """INT-01: Verify that a new agent plugin directory is dynamically discovered."""
    import shutil
    bridge = StateBridge()
    original_count = len(bridge.get_agents())
    
    # Create a dummy agent directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dummy_agent_dir = os.path.join(root_dir, "agents", "mock_agent_int01")
    os.makedirs(dummy_agent_dir, exist_ok=True)
    with open(os.path.join(dummy_agent_dir, "SKILL.md"), "w") as f:
        f.write("# Mock Agent\nDescription: For INT-01 verification.")
    
    try:
        # Re-fetch agents. AgentRegistry is expected to re-scan.
        new_agents = bridge.get_agents()
        new_count = len(new_agents)
        agent_names = [a.name for a in new_agents]
        
        assert new_count == original_count + 1
        assert "mock_agent_int01" in agent_names
    finally:
        # Cleanup
        shutil.rmtree(dummy_agent_dir)
