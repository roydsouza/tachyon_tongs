import json
import os
from typing import Dict, Any, List
from tachyon.policy.engine import PolicyEngine, PolicyVerdict, Verdict
from tachyon.policy.engines.rego_engine import RegoPolicyEngine
from tachyon.policy.engines.cedar_engine import CedarPolicyEngine

class SingularityPDP(PolicyEngine):
    """
    The central broker for multi-engine policy enforcement.
    Federates calls to active plugins based on consensus rules.
    """

    def __init__(self, config_path: str = "configs/singularity_config.json"):
        self.engines: List[PolicyEngine] = []
        self.config = self._load_config(config_path)
        self._initialize_engines()

    def _load_config(self, path: str) -> dict:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {"consensus": "ANY_DENY", "active_engines": ["REGO"]}

    def _initialize_engines(self):
        active = self.config.get("active_engines", [])
        configs = self.config.get("engine_configs", {})
        
        if "REGO" in active:
            rego_conf = configs.get("REGO", {})
            self.engines.append(RegoPolicyEngine(
                policy_dir=rego_conf.get("policy_dir", "policies/rego"),
                enforce_signatures=rego_conf.get("enforce_signatures", True)
            ))

        if "CEDAR" in active:
            cedar_conf = configs.get("CEDAR", {})
            self.engines.append(CedarPolicyEngine(
                policy_dir=cedar_conf.get("policy_dir", "policies/cedar"),
                enforce_signatures=cedar_conf.get("enforce_signatures", True)
            ))

    def evaluate(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        """
        Runs the action through all active engines and applies consensus logic.
        """
        if not self.engines:
            return PolicyVerdict(Verdict.ALLOW, "No engines active, default allow (Insecure)", "SINGULARITY_CORE")

        verdicts = []
        for engine in self.engines:
            try:
                verdict = engine.evaluate(agent_id, action, params)
                verdicts.append(verdict)
                
                # Short-circuit on ANY_DENY (includes DENY and ERROR for maximum security)
                if self.config.get("consensus") == "ANY_DENY":
                    if verdict.verdict in [Verdict.DENY, Verdict.ERROR]:
                        return verdict
            except Exception as e:
                error_verdict = PolicyVerdict(Verdict.ERROR, str(e), engine.engine_id)
                if self.config.get("consensus") == "ANY_DENY":
                    return error_verdict
                verdicts.append(error_verdict)

        # Placeholder: If we reached here without a short-circuited DENY and consensus is ANY_DENY
        # then we are essentially ALLOWed unless an error occurred.
        return PolicyVerdict(Verdict.ALLOW, "Consensus reached", "SINGULARITY_CORE")

    @property
    def engine_id(self) -> str:
        return "SINGULARITY_BROKER"
