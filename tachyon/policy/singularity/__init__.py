import json
import os
import logging
from typing import Dict, Any, List, Type
from tachyon.policy.engine import PolicyEngine, PolicyVerdict, Verdict
from tachyon.policy.engines.rego_engine import RegoPolicyEngine
from tachyon.policy.engines.cedar_engine import CedarPolicyEngine
from tachyon.policy.checkers.alignment_pdp import AlignmentPDP

logger = logging.getLogger(__name__)


class EmergencyPolicyEngine(PolicyEngine):
    """
    Ultra-conservative fallback policy engine.
    
    Activated when ALL configured policy engines fail to initialize.
    Only permits read-only, non-destructive operations (health checks, status queries).
    Everything else is DENIED.
    
    This allows remote operators to examine the system state and diagnose why
    engines failed, without allowing any destructive or data-exfiltrating actions.
    
    TT-2026-002: Implements fail-closed with graceful degradation.
    """

    SAFE_READ_ONLY_ACTIONS = frozenset({
        "health_check",
        "get_status",
        "list_agents",
        "get_agent_health",
        "verify_file",
        "verify_substrate",
    })

    @property
    def engine_id(self) -> str:
        return "EMERGENCY_FALLBACK"

    def __init__(self, **kwargs):
        """EmergencyPolicyEngine ignores all config — it is self-contained."""
        pass

    async def evaluate(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        if action in self.SAFE_READ_ONLY_ACTIONS:
            return PolicyVerdict(
                Verdict.ALLOW,
                f"Emergency fallback: '{action}' is a safe read-only operation.",
                self.engine_id,
                {"emergency_mode": True}
            )
        return PolicyVerdict(
            Verdict.DENY,
            f"EMERGENCY FAIL-CLOSED: Action '{action}' blocked. "
            f"All policy engines are offline. Only read-only operations are permitted. "
            f"Check engine initialization logs and singularity_config.json.",
            self.engine_id,
            {"emergency_mode": True, "blocked_action": action}
        )


class SingularityPDP(PolicyEngine):
    """
    The central broker for multi-engine policy enforcement.
    Federates calls to active plugins based on consensus rules.
    Supports pluggable engine registration.
    
    TT-2026-002 FIX: Fail-closed with EmergencyPolicyEngine fallback.
    """

    _registry: Dict[str, Type[PolicyEngine]] = {
        "REGO": RegoPolicyEngine,
        "CEDAR": CedarPolicyEngine,
        "ALIGNMENT": AlignmentPDP
    }

    def __init__(self, config_path: str = "configs/singularity_config.json"):
        self.engines: List[PolicyEngine] = []
        self.config = self._load_config(config_path)
        self._emergency_mode = False
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
        
        failed_engines = []
        
        for engine_name in active:
            if engine_name in self._registry:
                engine_class = self._registry[engine_name]
                conf = configs.get(engine_name, {})
                try:
                    self.engines.append(engine_class(
                        policy_dir=conf.get("policy_dir", f"policies/{engine_name.lower()}"),
                        enforce_signatures=conf.get("enforce_signatures", True)
                    ))
                except Exception as e:
                    # TT-2026-002 FIX: Log at ERROR level, never silently print
                    failed_engines.append((engine_name, str(e)))
                    logger.error(f"Failed to initialize policy engine {engine_name}: {e}")
            else:
                failed_engines.append((engine_name, f"Unknown engine type: {engine_name}"))
                logger.error(f"Unknown policy engine type: {engine_name}")
        
        # TT-2026-002 FIX: If ALL configured engines failed, activate emergency mode
        if not self.engines and active:
            error_details = "\n".join(f"  - {name}: {err}" for name, err in failed_engines)
            logger.critical(
                f"FATAL: All {len(active)} configured policy engines failed to initialize.\n"
                f"Activating EmergencyPolicyEngine (fail-closed, read-only only).\n"
                f"Failures:\n{error_details}"
            )
            self._emergency_mode = True
            self.engines.append(EmergencyPolicyEngine())

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Aggregates snapshots from all active member engines."""
        return {
            "engines": {e.engine_id: e.get_state_snapshot() for e in self.engines},
            "consensus": self.config.get("consensus", "ANY_DENY"),
            "emergency_mode": self._emergency_mode
        }

    async def evaluate(self, agent_id: str, action: str, params: Dict[str, Any], snapshot: Optional[Dict[str, Any]] = None) -> PolicyVerdict:
        """
        Runs the action through all active engines and applies consensus logic.
        If a snapshot is provided, it is decomposed and passed to member engines.
        """
        if not self.engines:
            # This should never happen after _initialize_engines, but belt-and-suspenders
            return PolicyVerdict(
                Verdict.DENY,
                "FAIL-CLOSED: No policy engines available. Cannot authorize actions.",
                "SINGULARITY_CORE"
            )

        # If in emergency mode, delegate directly to the emergency engine
        if self._emergency_mode:
            emergency_snapshot = snapshot.get("engines", {}).get("EMERGENCY_FALLBACK") if snapshot else None
            return await self.engines[0].evaluate(agent_id, action, params, snapshot=emergency_snapshot)

        verdicts = []
        engine_snapshots = snapshot.get("engines", {}) if snapshot else {}
        
        for engine in self.engines:
            try:
                engine_snap = engine_snapshots.get(engine.engine_id)
                verdict = await engine.evaluate(agent_id, action, params, snapshot=engine_snap)
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
        """Wrapper to check if an action is deterministically allowed."""
        verdict = await self.evaluate(agent_id, action, params)
        return verdict.verdict == Verdict.ALLOW

    async def evaluate_intent(self, intent: str, action: str, params: Dict[str, Any]) -> bool:
        """Shim for legacy intent-based evaluation."""
        params_with_intent = params.copy()
        params_with_intent["intent"] = intent
        verdict = await self.evaluate("legacy_intent_agent", action, params_with_intent)
        return verdict.verdict == Verdict.ALLOW

    @property
    def engine_id(self) -> str:
        return "SINGULARITY_BROKER"
