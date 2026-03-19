from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from tachyon.core.state import StateManager
from tachyon.core.signing import IntegrityManager
from tachyon.core.sanitizer import InputSanitizer

class BaseTachyonAgent(ABC):
    """
    Unified Base Substrate for all Tachyon Tongs Agents.
    Provides forensic signing, input sanitization, and state management.
    """
    def __init__(self, agent_id: str, role_name: str):
        self.agent_id = agent_id
        self.role_name = role_name
        self.state = StateManager()
        self.integrity = IntegrityManager()
        self.sanitizer = InputSanitizer()

    def handle_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Unified entry point for all agent actions."""
        # 1. Sanitize Inputs
        sanitized_params = {k: self.sanitizer.sanitize(str(v)) if isinstance(v, str) else v 
                           for k, v in parameters.items()}
        
        # 2. Forensic Audit (Pre-Execution)
        self.state.log_evolution("Agent Action", f"Agent {self.agent_id} ({self.role_name}) initiating {action}")

        # 3. Execute Role Logic
        try:
            result = self.execute_role_logic(action, sanitized_params)
            status = "SUCCESS"
        except Exception as e:
            result = {"error": str(e)}
            status = "ERROR"

        # 4. Forensic Sign-off
        # (This is where we'd sign the specific action footprint if needed)
        
        return {"status": status, "agent": self.agent_id, "role": self.role_name, "result": result}

    @abstractmethod
    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Execute role-specific implementation."""
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        """Returns standard agent metadata."""
        return {
            "agent_id": self.agent_id,
            "type": self.__class__.__name__,
            "capabilities": self.config.get("capabilities", [])
        }
