import json
import os
from typing import Dict, Any, List, Type
from tachyon.policy.engine import PolicyEngine, PolicyVerdict, Verdict
from tachyon.policy.engines.rego_engine import RegoPolicyEngine
from tachyon.policy.engines.cedar_engine import CedarPolicyEngine
from tachyon.policy.checkers.alignment_pdp import AlignmentPDP

class SingularityPDP(PolicyEngine):
    """
    The central broker for multi-engine policy enforcement.
    Federates calls to active plugins based on consensus rules.
    Now supports pluggable engine registration.
    """

    _registry: Dict[str, Type[PolicyEngine]] = {
        "REGO": RegoPolicyEngine,
        "CEDAR": CedarPolicyEngine,
        "ALIGNMENT": AlignmentPDP
    }

    def __init__(self, config_path: str = "configs/singularity_config.json"):
        self.engines: List[PolicyEngine] = []
        self.config = self._load_config(config_path)
        self._initialize_engines()

    @classmethod
    def register_engine_type(cls, name: str, engine_class: Type[PolicyEngine]):
        """Registers a new engine type at the class level."""
        cls._registry[name] = engine_class

    def _load_config(self, path: str) -> dict:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {"consensus": "ANY_DENY", "active_engines": ["REGO"]}

    def _initialize_engines(self):
        active = self.config.get("active_engines", [])
        configs = self.config.get("engine_configs", {})
        
        for engine_name in active:
            if engine_name in self._registry:
                engine_class = self._registry[engine_name]
                conf = configs.get(engine_name, {})
                # Most engines follow the policy_dir/enforce_signatures pattern
                try:
                    self.engines.append(engine_class(
                        policy_dir=conf.get("policy_dir", f"policies/{engine_name.lower()}"),
                        enforce_signatures=conf.get("enforce_signatures", True)
                    ))
                except Exception as e:
                    print(f"ERROR: Failed to initialize engine {engine_name}: {e}")

    async def evaluate(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        """
        Runs the action through all active engines and applies consensus logic.
        """
        if not self.engines:
            return PolicyVerdict(Verdict.ALLOW, "No engines active, default allow (Insecure)", "SINGULARITY_CORE")

        verdicts = []
        for engine in self.engines:
            try:
                verdict = await engine.evaluate(agent_id, action, params)
                verdicts.append(verdict)
                
                # ANY_DENY Short-circuit (includes ERROR for maximum security)
                if self.config.get("consensus") == "ANY_DENY":
                    if verdict.verdict in [Verdict.DENY, Verdict.ERROR]:
                        return verdict
            except Exception as e:
                error_verdict = PolicyVerdict(Verdict.ERROR, f"Engine Failure ({engine.engine_id}): {str(e)}", engine.engine_id)
                if self.config.get("consensus") == "ANY_DENY":
                    return error_verdict
                verdicts.append(error_verdict)

        # Final check for ANY_DENY: if we are here, no DENY/ERROR occurred.
        return PolicyVerdict(Verdict.ALLOW, "Consensus reached (All active engines permitted)", "SINGULARITY_CORE")

    async def is_action_allowed(self, agent_id: str, action: str, params: Dict[str, Any]) -> bool:
        """
        Wrapper to check if an action is deterministicially allowed.
        """
        verdict = await self.evaluate(agent_id, action, params)
        return verdict.verdict == Verdict.ALLOW

    async def evaluate_intent(self, intent: str, action: str, params: Dict[str, Any]) -> bool:
        """
        Shim for legacy intent-based evaluation.
        """
        params_with_intent = params.copy()
        params_with_intent["intent"] = intent
        verdict = await self.evaluate("legacy_intent_agent", action, params_with_intent)
        return verdict.verdict == Verdict.ALLOW

    @property
    def engine_id(self) -> str:
        return "SINGULARITY_BROKER"
