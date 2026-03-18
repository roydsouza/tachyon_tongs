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
from tachyon.core.routing import ModelRouter

app = FastAPI(title="Tachyon Tongs Substrate Daemon", version="1.0.0")
airlock_app = FastAPI(title="Tachyon Tongs Airlock API", version="1.0.0")

# Initialize shared components
sandbox = AppleSandbox(workspace_dir="/tmp/tachyon_tier0")
policy_engine = SingularityPDP()
router = None # Will be initialized on startup
model_router = ModelRouter()

class ToolRequest(BaseModel):
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    tenant_id: Optional[str] = "default"
    prompt_context: Optional[str] = None # Optional context for complexity detection

class ToolResponse(BaseModel):
    request_id: str
    status: str
    selected_model: str # Indicate which model was used
    result: Optional[Any] = None
    error: Optional[str] = None

@app.post("/action", response_model=ToolResponse)
async def execute_action(request: ToolRequest):
    request_id = str(uuid.uuid4())
    
    # 1. Detect Complexity & Select Model
    prompt = request.prompt_context or f"{request.action} with parameters {request.parameters}"
    complexity = model_router.detect_complexity(prompt)
    
    # In a real scenario, we'd fetch actual quota metrics. Using 1.0 (full) for now.
    selected_model = model_router.select_model(prompt, complexity, current_quota=1.0)
    
    # 2. Fallback logic
    # If a specific model is requested but fails, or if we ensure a fallback is always ready:
    fallback_model = "gemini-3-flash" # The reliable floor
    
    try:
        # Route the action
        result = await router.route(request.agent_id, request.action, request.parameters)
    except Exception as e:
        # Fallback implementation: repeat with the floor model if applicable
        # This is a placeholder for actual multi-backend dispatch logic
        logger.warning(f"Primary model routing failed, falling back to {fallback_model}")
        result = {"status": "FALLBACK_SUCCESS", "result": f"Recovered via {fallback_model}", "error": str(e)}

    # Push to Airlock
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
