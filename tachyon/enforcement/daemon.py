import asyncio
import os
import json
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Deferred import to break circularity
# from tachyon.pipeline import SentinelOrchestrator
from tachyon.enforcement import AppleSandbox, ToolRouter
from tachyon.monitoring import syscall_monitor
from tachyon.policy.singularity import SingularityPDP

app = FastAPI(title="Tachyon Tongs Substrate Daemon", version="1.0.0")
airlock_app = FastAPI(title="Tachyon Tongs Airlock API", version="1.0.0")

# Enable CORS for the Airlock Dashboard (Port 3030)
airlock_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3030", "http://localhost:3030"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize shared components
sandbox = AppleSandbox(workspace_dir="/tmp/tachyon_tier0")
# orchestrator = SentinelOrchestrator()
policy_engine = SingularityPDP()
# router = ToolRouter(orchestrator, sandbox, policy_engine, None, syscall_monitor)
router = None # Will be initialized on startup

class ToolRequest(BaseModel):
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    tenant_id: Optional[str] = "default"

class ToolResponse(BaseModel):
    request_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "ok", "engine": "Metal 4 / Apple Silicon", "substrate": "active"}

class AirlockManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

airlock_manager = AirlockManager()

@airlock_app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await airlock_manager.connect(websocket)
    try:
        while True:
            # Dummy pulse data for now
            await websocket.receive_text()
            # real implementation will stream from StateManager/Scout
    except WebSocketDisconnect:
        airlock_manager.disconnect(websocket)

@app.post("/action", response_model=ToolResponse)
async def execute_action(request: ToolRequest):
    request_id = str(uuid.uuid4())
    result = await router.route(request.agent_id, request.action, request.parameters)
    
    # Push to Airlock
    await airlock_manager.broadcast(json.dumps({
        "type": "ACTION_LOG",
        "agent_id": request.agent_id,
        "action": request.action,
        "status": result.get("status")
    }))
    
    return ToolResponse(
        request_id=request_id,
        status=result.get("status", "ERROR"),
        result=result.get("result"),
        error=result.get("error")
    )

if __name__ == "__main__":
    import uvicorn
    # Start Substrate Daemon (PEP)
    substrate_config = uvicorn.Config(app, host="127.0.0.1", port=60461, log_level="info")
    substrate_server = uvicorn.Server(substrate_config)
    
    # Start Airlock API (Telemetry)
    airlock_config = uvicorn.Config(airlock_app, host="127.0.0.1", port=60462, log_level="info")
    airlock_server = uvicorn.Server(airlock_config)

    async def run_servers():
        await asyncio.gather(substrate_server.serve(), airlock_server.serve())

    asyncio.run(run_servers())
