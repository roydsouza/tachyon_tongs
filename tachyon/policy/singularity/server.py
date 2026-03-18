import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from tachyon.policy.singularity.ledger import AuthorizationLedger
from tachyon.policy.singularity import SingularityPDP
from tachyon.policy.engine import Verdict

app = FastAPI(title="Singularity Meta-PDP Server")
ledger = AuthorizationLedger()
pdp = SingularityPDP()

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
        
        return {
            "verdict": verdict_obj.verdict.name,
            "reason": verdict_obj.reason,
            "engine": verdict_obj.engine_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ALIVE", "engines": [e.engine_id for e in pdp.engines]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
