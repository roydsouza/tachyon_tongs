from fastapi import APIRouter
from typing import List, Dict
from tachyon.api.schema import (
    SubstrateHealth, AgentDetail, PatchProposal, ForensicAlert, 
    AgentHealth, TrafficSummary, SignedCommand, AuthExchangeRequest
)
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

@router.get("/forensics", response_model=List[ForensicAlert])
async def list_forensics():
    """Recent Forensic High-Signal Events"""
    return bridge.get_forensic_alerts()

@router.get("/agents/{name}/health", response_model=AgentHealth)
async def get_agent_health(name: str):
    """Detailed Agent Health & Heartbeat"""
    return bridge.get_agent_health(name)

@router.get("/traffic/summary", response_model=TrafficSummary)
async def get_traffic_summary():
    """Aggregated Traffic Stats (Transit vs Internal)"""
    return bridge.get_traffic_summary()

@router.post("/action", response_model=ToolResponse)
async def execute_action(request: ToolRequest):
    """Execute secured tool actions via PEPLayer"""
    return await pep.execute(request)

@router.post("/relay", response_model=ToolResponse)
async def relay_command(command: SignedCommand):
    """Securely relay signed commands from remote sensors"""
    return await pep.execute_signed(command)

@router.post("/auth/exchange", response_model=Dict[str, str])
async def exchange_keys(request: AuthExchangeRequest):
    """Register remote sensor public keys for trusted relay"""
    from tachyon.core.state_manager import StateManager
    StateManager().register_sensor(request.sensor_id, request.public_key_b64)
    return {"status": "SUCCESS", "sensor_id": request.sensor_id}
