import asyncio
import os
import json
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Deferred import to break circularity
# from tachyon.pipeline import SentinelOrchestrator
from tachyon.enforcement import AppleSandbox, ToolRouter
from tachyon.monitoring import syscall_monitor
from tachyon.policy.singularity import SingularityPDP

app = FastAPI(title="Tachyon Tongs Substrate Daemon", version="1.0.0")

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

@app.post("/action", response_model=ToolResponse)
async def execute_action(request: ToolRequest):
    request_id = str(uuid.uuid4())
    result = await router.route(request.agent_id, request.action, request.parameters)
    
    return ToolResponse(
        request_id=request_id,
        status=result.get("status", "ERROR"),
        result=result.get("result"),
        error=result.get("error")
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=60461)
