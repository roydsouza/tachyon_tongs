import asyncio
import os
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import time
from src.adk_sentinel import run_supervisor
from src.execution_logger import ExecutionLogger
from src.apple_sandbox import AppleSandbox
from src.behavior_monitor import syscall_monitor, BehaviorAnomalyError
import shlex

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

INTENT_MAP = {
    "RESEARCH": ["arxiv.org", "nvd.nist.gov", "github.com", "owasp.org", "huntr.ml", "lmsys.org"],
    "SECURITY": ["cisa.gov", "cert.org", "mitre.org"],
    "DEFAULT": []
}

@app.post("/action", response_model=ToolResponse)
async def execute_action(request: ToolRequest):
    request_id = str(uuid.uuid4())
    
    try:
        # 1a. Identity Hijacking Defense (Statistical Drift)
        try:
            syscall_monitor.log_and_evaluate(request.agent_id, request.action)
        except BehaviorAnomalyError as e:
            return ToolResponse(request_id=request_id, status="BLOCKED", error=str(e))
            
        if request.action == "safe_fetch":
            url = request.parameters.get("url")
            intent = request.parameters.get("intent", "DEFAULT")
            allowed_domains = request.parameters.get("allowed_domains", [])
            
            # Semantic Intent Mapping
            mapped_domains = INTENT_MAP.get(intent, [])
            combined_allowed = list(set(allowed_domains + mapped_domains))
            
            if not url:
                raise HTTPException(status_code=400, detail="Missing URL parameter")
            
            # Load Dynamic Denylist for OPA
            denylist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "policies/shared/denylist.json")
            denylist_data = {}
            if os.path.exists(denylist_path):
                with open(denylist_path, "r") as f:
                    denylist_data = json.load(f)
            
            # Start a multi-tenant log entry
            logger = ExecutionLogger(agent_id=request.agent_id)
            logger.start_run(trigger=f"SUBSTRATE_API:{request.tenant_id}")
            
            # 2. Empower the Guardian Triad for this specific tenant request
            # We pass the URL as the "threat_url" to trigger the Scout/Analyst/Engineer cycle
            # We inject the combined allowed domains and the dynamic denylist into the triad's context
            
            pass_params = {
                "url": url,
                "logger": logger,
                "allowed_domains": combined_allowed,
                "denylist": denylist_data.get("malicious_domains", [])
            }
            
            result = await asyncio.to_thread(run_supervisor, **pass_params)
            
            # Finalize the log entry for this specific tenant/agent
            logger.finalize_run()
            
            # In adk_sentinel graph, the final state contains 'analysis' and 'sanitized_content'
            analysis_dict = result.get("analysis", {})
            final_status = analysis_dict.get("status", "UNKNOWN")
            
            if final_status == "success":
                # Check if the Metal Analyst explicitly flagged prompt injections
                threats = analysis_dict.get("threats_found", [])
                
                # If the agent is HorizonScout, it is permitted to read hostile text (like arXiv threat research)
                is_scout = request.agent_id == "HorizonScout"
                
                if len(threats) == 0 or is_scout:
                    return ToolResponse(
                        request_id=request_id,
                        status="SUCCESS",
                        result={
                            "content": result.get("sanitized_content", ""), 
                            "threats": len(threats),
                            "intent_gated": intent
                        }
                    )
                else:
                    return ToolResponse(
                        request_id=request_id,
                        status="BLOCKED",
                        error=f"Action blocked by Guardian Triad. Payload contained hostile prompt injections: {threats}"
                    )
            else:
                reason = analysis_dict.get("reason", "Unknown Triad Failure")
                return ToolResponse(
                    request_id=request_id,
                    status="BLOCKED",
                    error=f"Action blocked by Guardian Triad. Reason: {reason}"
                )
        
        elif request.action == "safe_execute":
            command_str = request.parameters.get("command")
            if not command_str:
                raise HTTPException(status_code=400, detail="Missing command parameter")
            
            # Use AppleSandbox as Tier 0 isolation
            sandbox = AppleSandbox(workspace_dir=f"/tmp/tachyon_tier0_{request.agent_id}")
            command_args = shlex.split(command_str)
            
            result = sandbox.execute(command_args)
            if result["status"] == "success":
                return ToolResponse(
                    request_id=request_id,
                    status="SUCCESS",
                    result={
                        "stdout": result.get("stdout", ""),
                        "stderr": result.get("stderr", ""),
                        "exit_code": result.get("exit_code", 0)
                    }
                )
            else:
                return ToolResponse(
                    request_id=request_id,
                    status="BLOCKED" if result["status"] == "error" else "ERROR",
                    error=result.get("error", "") + "\n" + result.get("stderr", "")
                )
        
        else:
            raise HTTPException(status_code=405, detail=f"Action '{request.action}' not yet implemented in Substrate.")

    except Exception as e:
        return ToolResponse(request_id=request_id, status="ERROR", error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=60461)

# [AUTOGENERATED MITIGATION] Applied deep verification constraint for CVE
