import os
from typing import Dict, Any
from agents._core.base import BaseAgentPlugin
from agents._core.registry import AgentRegistry
from tachyon.core.signing import IntegrityManager

@AgentRegistry.register("guardian")
class GuardianPlugin(BaseAgentPlugin):
    """
    Guardian Plugin: Specialized in substrate integrity.
    """
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "Guardian", config)
        self.integrity_manager = IntegrityManager()

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "verify_file":
            filepath = parameters.get("filepath")
            if not filepath:
                return {"status": "ERROR", "message": "filepath required"}
            
            # Ensure absolute path for deterministic verification
            abs_path = os.path.abspath(filepath)
            is_valid = self.integrity_manager.verify_integrity(abs_path)
            
            # Mutant Lock Bypass: Check if mutation is authorized
            from tachyon.core.state import StateManager
            state = StateManager()
            is_authorized = state.is_mutant_lock_active()
            
            if not is_valid and is_authorized:
                # Downgrade to informational warning instead of failure
                return {
                    "status": "WARNING",
                    "is_valid": False,
                    "authorized_mutation": True,
                    "filepath": abs_path,
                    "message": "Integrity mismatch detected, but authorized Mutant Lock is active. Suppression engaged."
                }

            return {
                "status": "SUCCESS" if is_valid else "FAILURE",
                "is_valid": is_valid,
                "filepath": abs_path
            }
        
        return {"status": "ERROR", "message": f"Unknown action: {action}"}
