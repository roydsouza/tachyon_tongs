from fastapi import APIRouter
from typing import List
from tachyon.api.schema import SubstrateHealth, AgentDetail, PatchProposal
from tachyon.api.pep import PEPLayer, ToolRequest, ToolResponse
from tachyon.core.state_bridge import StateBridge

router = APIRouter(prefix="/api/v1")
bridge = StateBridge()
pep = PEPLayer()

@router.get("/status", response_model=SubstrateHealth)
async def get_status():
    """Tachyon Substrate Health Dashboard"""
    return bridge.get_substrate_health()

@router.get("/agents", response_model=List[AgentDetail])
async def list_agents():
    """Active Agent Collective Inventory"""
    return bridge.get_agents()

@router.get("/airlock", response_model=List[PatchProposal])
async def list_patches():
    """Pending Airlock Patches for Review"""
    return bridge.get_patches()

@router.post("/action", response_model=ToolResponse)
async def execute_action(request: ToolRequest):
    """Execute secured tool actions via PEPLayer"""
    return await pep.execute(request)
