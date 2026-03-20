from typing import Dict, Any
from tachyon.agents.base import BaseTachyonAgent

class SentinelRole(BaseTachyonAgent):
    """
    The Sentinel Role (The Immune System).
    Autonomously aggregates, analyzes, and mitigates agentic exploits.
    """
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "Sentinel")

    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        if action == "run_sweep":
            return self._run_sweep(parameters)
        raise ValueError(f"Unknown action for Sentinel: {action}")

    def _run_sweep(self, params: Dict[str, Any]):
        from scripts.sentinel import reactive_remediation_sweep
        from tachyon.pipeline.orchestrator import run_supervisor
        
        harvest_mode = params.get("harvest_mode", True)
        reactive_remediation_sweep()
        run_supervisor(target_url="https://github.com/advisories", harvest_mode=harvest_mode)
        return "Sweep complete"
