import pytest
import asyncio
from tachyon.api.pep import PEPLayer, ToolRequest

@pytest.mark.asyncio
async def test_pep_wasm_routing():
    """
    Verify that SAFE_MATH is routed to Tier 1 (WASM).
    """
    pep = PEPLayer()
    request = ToolRequest(
        agent_id="test-agent",
        action="SAFE_MATH",
        parameters={"val1": 15, "val2": 25}
    )
    
    response = await pep.execute(request)
    assert response.status == "SUCCESS"
    assert response.result["value"] == 40
    assert response.result["tier"] == 1

@pytest.mark.asyncio
async def test_pep_vm_routing_mock():
    """
    Verify that AUTONOMIC_RECOVERY is routed to Tier 0 (MicroVM).
    Note: We mock the actual VM execution to avoid long test times in CI.
    """
    pep = PEPLayer()
    
    # Mock the VM runner to avoid actual limactl calls in unit tests
    from unittest.mock import MagicMock
    pep.vm_runner.provision_vm = MagicMock()
    pep.vm_runner.execute_command = MagicMock(return_value="Substrate Recovered in VM")
    
    request = ToolRequest(
        agent_id="test-agent",
        action="AUTONOMIC_RECOVERY",
        parameters={"command": "reboot --confirm"}
    )
    
    response = await pep.execute(request)
    assert response.status == "SUCCESS"
    assert response.result["output"] == "Substrate Recovered in VM"
    assert response.result["tier"] == 0

@pytest.mark.asyncio
async def test_pep_native_fallback():
    """
    Verify that unknown actions use the legacy native sandbox.
    """
    pep = PEPLayer()
    request = ToolRequest(
        agent_id="test-agent",
        action="GENERIC_ACTION",
        parameters={"key": "value"}
    )
    
    response = await pep.execute(request)
    assert response.status == "SUCCESS"
    assert "verified by Singularity" in response.result
