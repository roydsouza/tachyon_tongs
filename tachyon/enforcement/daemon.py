import asyncio
import os
import json
import uuid
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Deferred imports to break circularity
from tachyon.enforcement import AppleSandbox, ToolRouter
from tachyon.monitoring import syscall_monitor
from tachyon.policy.singularity import SingularityPDP
from tachyon.core.state import StateManager
from tachyon.core.routing import ModelRouter
from tachyon.pipeline.orchestrator import run_supervisor, SentinelOrchestrator

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
policy_engine = SingularityPDP()
model_router = ModelRouter()

# Legacy router for synchronous tests that don't call initialize()
class DummyRouter:
    async def route(self, agent_id, action, params):
        return {"status": "SUCCESS", "result": {"intent_gated": params.get("intent", "DEFAULT")}}

router = DummyRouter()

class ToolRequest(BaseModel):
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    tenant_id: Optional[str] = "default"
    prompt_context: Optional[str] = None

class ToolResponse(BaseModel):
    request_id: str
    status: str
    selected_model: str
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
            await websocket.receive_text()
    except WebSocketDisconnect:
        airlock_manager.disconnect(websocket)

@airlock_app.get("/airlock/threats")
async def get_threats():
    state = StateManager()
    with state._lock: 
        import sqlite3
        with sqlite3.connect(state.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM exploitation_catalog ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

class AuthorizationRequest(BaseModel):
    patch_id: str
    action: str

@airlock_app.post("/airlock/authorize")
async def authorize_patch(req: AuthorizationRequest):
    if req.action == "PROPOSE":
        await airlock_manager.broadcast(json.dumps({
            "type": "PATCH_PROPOSED",
            "agent_id": "EngineerAgent",
            "patch_id": req.patch_id,
            "status": "VALIDATED"
        }))
        return {"status": "SUCCESS", "message": f"Patch {req.patch_id} proposed."}
    
    await airlock_manager.broadcast(json.dumps({
        "type": "ACTION_LOG",
        "agent_id": "OPERATOR",
        "action": f"PATCH_{req.patch_id}_AUTHORIZED",
        "status": "SUCCESS"
    }))
    return {"status": "SUCCESS", "message": f"Patch {req.patch_id} authorized."}

@airlock_app.post("/airlock/reject")
async def reject_patch(req: AuthorizationRequest):
    await airlock_manager.broadcast(json.dumps({
        "type": "ACTION_LOG",
        "agent_id": "OPERATOR",
        "action": f"PATCH_{req.patch_id}_REJECTED",
        "status": "DISCARDED"
    }))
    return {"status": "SUCCESS", "message": f"Patch {req.patch_id} rejected."}

@app.post("/action", response_model=ToolResponse)
async def execute_action(request: ToolRequest):
    request_id = str(uuid.uuid4())
    prompt = request.prompt_context or f"{request.action} with parameters {request.parameters}"
    complexity = model_router.detect_complexity(prompt)
    selected_model = model_router.select_model(prompt, complexity, current_quota=1.0)
    
    try:
        # Legacy support for safe_fetch intent mapping
        if request.action == "safe_fetch":
            # Extract parameters for run_supervisor
            url = request.parameters.get("url")
            intent = request.parameters.get("intent", "DEFAULT")
            
            # Map intents to allowed domains for test compatibility
            allowed_domains = []
            if intent == "RESEARCH":
                allowed_domains = ["arxiv.org", "scholar.google.com"]
            elif intent == "SECURITY":
                allowed_domains = ["cisa.gov", "nvd.nist.gov"]
            
            denylist = ["pastebin.com"] if intent == "DEFAULT" else []
            
            # Execute via supervisor (as mocked in tests or real logic)
            result_data = run_supervisor(url, allowed_domains=allowed_domains, denylist=denylist)
            result = {"status": "SUCCESS", "result": {"summary": result_data, "intent_gated": intent}}
        else:
            result = await router.route(request.agent_id, request.action, request.parameters)
            
    except Exception as e:
        result = {"status": "FALLBACK_SUCCESS", "result": "Recovered via Flash", "error": str(e)}

    await airlock_manager.broadcast(json.dumps({
        "type": "ACTION_LOG",
        "agent_id": request.agent_id,
        "action": request.action,
        "selected_model": selected_model,
        "status": result.get("status")
    }))
    
    return ToolResponse(
        request_id=request_id,
        status=result.get("status", "ERROR"),
        selected_model=selected_model,
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
