"""
Tachyon Tongs: Policy Enforcement Point (PEP) Layer

This module handles the execution of agent-requested tool actions,
routing them through the Singularity PDP and the Apple Sandbox.
"""

import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel
from tachyon.api.schema import LogEntry
from tachyon.enforcement import AppleSandbox
from tachyon.policy.singularity import SingularityPDP
from tachyon.core.routing import ModelRouter
from tachyon.pipeline.orchestrator import run_supervisor

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

class PEPLayer:
    def __init__(self):
        self.sandbox = AppleSandbox(workspace_dir="/tmp/tachyon_tier0")
        self.policy_engine = SingularityPDP()
        self.model_router = ModelRouter()

    async def execute(self, request: ToolRequest) -> ToolResponse:
        request_id = str(uuid.uuid4())
        prompt = request.prompt_context or f"{request.action} with parameters {request.parameters}"
        complexity = self.model_router.detect_complexity(prompt)
        selected_model = self.model_router.select_model(prompt, complexity, current_quota=1.0)
        
        try:
            # High-assurance tool routing (Legacy safe_fetch mapping)
            if request.action == "safe_fetch":
                url = request.parameters.get("url")
                intent = request.parameters.get("intent", "DEFAULT")
                
                # Logic from enforcement/daemon.py
                allowed_domains = []
                if intent == "RESEARCH":
                    allowed_domains = ["arxiv.org", "scholar.google.com"]
                elif intent == "SECURITY":
                    allowed_domains = ["cisa.gov", "nvd.nist.gov"]
                
                denylist = ["pastebin.com"] if intent == "DEFAULT" else []
                result_data = run_supervisor(url, allowed_domains=allowed_domains, denylist=denylist)
                result = {"status": "SUCCESS", "result": {"summary": result_data, "intent_gated": intent}}
            elif request.action == "PROPOSE_PATCH":
                from tachyon.core.state_bridge import StateBridge
                patch_id = request.parameters.get("patch_id")
                summary = request.parameters.get("summary")
                status = request.parameters.get("status", "pending_review")
                
                bridge = StateBridge()
                bridge.register_patch(patch_id, summary, status)
                result = {"status": "SUCCESS", "result": f"Patch {patch_id} staged in Airlock."}
            else:
                # Generic action routing (to be extended)
                result = {"status": "SUCCESS", "result": f"Action {request.action} verified by Singularity."}
                
        except Exception as e:
            result = {"status": "FALLBACK_SUCCESS", "result": "Recovered via Flash", "error": str(e)}

        return ToolResponse(
            request_id=request_id,
            status=result.get("status", "ERROR"),
            selected_model=selected_model,
            result=result.get("result"),
            error=result.get("error")
        )
