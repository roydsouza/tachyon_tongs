from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseTachyonAgent(ABC):
    """
    Abstract Base Class for all Tachyon Tongs agents.
    Provides a standardized interface for execution, logging, and metadata.
    """
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.config = config or {}
        
    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for agent execution.
        Must be implemented by subclasses.
        """
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        """Returns standard agent metadata."""
        return {
            "agent_id": self.agent_id,
            "type": self.__class__.__name__,
            "capabilities": self.config.get("capabilities", [])
        }
