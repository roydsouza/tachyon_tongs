from typing import Dict, Any
from tachyon.agents.base import BaseTachyonAgent

class GuardianRole(BaseTachyonAgent):
    """
    The Guardian Role (The Substrate Sentry).
    Ensures Merkle integrity and syscall compliance.
    """
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "Guardian")

    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        if action == "verify_substrate":
            return self._verify_substrate()
        raise ValueError(f"Unknown action for Guardian: {action}")

    def _verify_substrate(self):
        from tachyon.agents.guardian_ids import GuardianIDS
        guardian = GuardianIDS()
        return guardian.verify_substrate()
