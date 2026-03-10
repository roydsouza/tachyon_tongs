import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import time
from src.adk_sentinel import run_supervisor
from src.execution_logger import ExecutionLogger

app = FastAPI(title="Tachyon Tongs Substrate Daemon", version="1.0.0")

# In-memory session tracking (Will transition to a more permanent store in Phase 3/Cloud)
sessions: Dict[str, Dict[str, Any]] = {}

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
    
    # 1. Action Governance & Routing
    # In Phase 1, we route through the existing Supervisor Graph (Guardian Triad)
    # We treat every external request as "UNTRUSTED_CONTENT" to trigger the full pipeline.
    
    try:
        if request.action == "safe_fetch":
            url = request.parameters.get("url")
            allowed_domains = request.parameters.get("allowed_domains")
            if not url:
                raise HTTPException(status_code=400, detail="Missing URL parameter")
            
            # Start a multi-tenant log entry
            logger = ExecutionLogger(agent_id=request.agent_id)
            logger.start_run(trigger=f"SUBSTRATE_API:{request.tenant_id}")
            
            # 2. Empower the Guardian Triad for this specific tenant request
            # We pass the URL as the "threat_url" to trigger the Scout/Analyst/Engineer cycle
            # Note: In a production 'Substrate', we would have a more optimized 'Fast Path' 
            # for known safe domains, but for v1, we apply the full Triad for safety.
            
            result = await asyncio.to_thread(run_supervisor, url=url, logger=logger, allowed_domains=allowed_domains)
            
            # Finalize the log entry for this specific tenant/agent
            logger.finalize_run()
            final_output = result.get("final_output", {})
            final_status = final_output.get("status", "UNKNOWN")
            
            if final_status == "success":
                return ToolResponse(
                    request_id=request_id,
                    status="SUCCESS",
                    result={
                        "content": result.get("sanitized_content", ""), 
                        "threats": result.get("analysis", {}).get("threats_identified", 0)
                    }
                )
            else:
                reason = final_output.get("reason", "Unknown reason")
                return ToolResponse(
                    request_id=request_id,
                    status="BLOCKED",
                    error=f"Action blocked by Guardian Triad. Reason: {reason}"
                )
        
        else:
            raise HTTPException(status_code=405, detail=f"Action '{request.action}' not yet implemented in Substrate.")

    except Exception as e:
        return ToolResponse(request_id=request_id, status="ERROR", error=str(e))

if __name__ == "__main__":
    import uvicorn
    # Port 60461 is the standard 'Tachyon' port defined in our earlier sessions
    uvicorn.run(app, host="127.0.0.1", port=60461)
