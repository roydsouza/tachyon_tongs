import requests
import json
from typing import Dict, Any, List
from tachyon.policy.engine import PolicyEngine, PolicyVerdict, Verdict

class RemoteSingularityPDP(PolicyEngine):
    """
    Substrate Client for the Singularity Meta-PDP Server.
    Enforces a 'FAIL-CLOSED' posture for 100% zero-trust assurance.
    """
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url

    def evaluate(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        """
        Sends an evaluation request to the Meta-PDP server over REST.
        """
        try:
            response = requests.post(
                f"{self.server_url}/evaluate",
                json={"agent_id": agent_id, "action": action, "params": params},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                verdict_enum = Verdict[data["verdict"]]
                return PolicyVerdict(verdict_enum, data["reason"], data["engine"])
            else:
                return PolicyVerdict(
                    Verdict.DENY, 
                    f"META-PDP ERROR: Server returned HTTP {response.status_code}", 
                    self.engine_id
                )
                
        except requests.exceptions.RequestException as e:
            # --- FAIL CLOSED POLICY ---
            return PolicyVerdict(
                Verdict.DENY, 
                f"ZERO-TRUST FAIL-CLOSED: Meta-PDP server unreachable ({str(e)})", 
                self.engine_id
            )

    @property
    def engine_id(self) -> str:
        return "REMOTE_SINGULARITY_CLIENT"

    def is_action_allowed(self, agent_id: str, action: str, params: Dict[str, Any]) -> bool:
        verdict = self.evaluate(agent_id, action, params)
        return verdict.verdict == Verdict.ALLOW
