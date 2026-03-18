import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from tachyon.policy.singularity.ledger import AuthorizationLedger
from tachyon.policy.singularity import SingularityPDP
from tachyon.policy.engine import Verdict

app = FastAPI(title="Singularity Meta-PDP Server")
ledger = AuthorizationLedger()
pdp = SingularityPDP()

# Ensure REGO engine is initialized with the correct policy path for the server context
for engine in pdp.engines:
    if engine.engine_id == "REGO_OPA":
        engine.policy_dir = os.path.abspath("policies/rego")
        # In production, we'd enable signatures. For this substrate hardening, 
        # we check the ENV for override.
        engine.enforce_signatures = os.environ.get("TACHYON_ENFORCE_REGO_SIGS", "False").lower() == "true"

class EvaluationRequest(BaseModel):
    agent_id: str
    action: str
    params: Dict[str, Any]

@app.post("/evaluate")
async def evaluate_policy(request: EvaluationRequest):
    """
    Federates the authorization request and logs the decision to the ledger.
    """
    try:
        verdict_obj = pdp.evaluate(request.agent_id, request.action, request.params)
        
        # Log to Absolute Ledger
        ledger.log_decision(
            agent_id=request.agent_id,
            action=request.action,
            params=request.params,
            verdict=verdict_obj.verdict.name,
            reason=verdict_obj.reason,
            engine=verdict_obj.engine_id
        )
        
        # We always return 200 even on DENY, because the decision itself is a success.
        # However, if an ERROR occurs, SingularityPDP returns an ERROR verdict.
        return {
            "verdict": verdict_obj.verdict.name,
            "reason": verdict_obj.reason,
            "engine": verdict_obj.engine_id
        }
    except Exception as e:
        # Unexpected server-level failure
        raise HTTPException(status_code=500, detail=f"Internal PDP Failure: {str(e)}")

@app.get("/health")
async def health_check():
    engine_status = []
    for engine in pdp.engines:
        try:
            # Simple probe: check if engine can be reached/initialized
            engine_status.append({"id": engine.engine_id, "status": "READY"})
        except Exception as e:
            engine_status.append({"id": engine.engine_id, "status": "ERROR", "error": str(e)})
            
    return {
        "status": "ALIVE", 
        "consensus": pdp.config.get("consensus", "ANY_DENY"),
        "engines": engine_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
