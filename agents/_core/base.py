from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgentPlugin(ABC):
    """
    Standardized interface for all Tachyon Tongs agent plugins.
    Ensures consistent lifecycle management and registration.
    """
    def __init__(self, agent_id: str, plugin_name: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.plugin_name = plugin_name
        self.config = config
        self.quarantine_mode = config.get("quarantine_mode", False)
        self.graduated = config.get("graduated", not self.quarantine_mode)

    @abstractmethod
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Core execution logic for the plugin."""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Returns standard metadata for registration."""
        return {
            "agent_id": self.agent_id,
            "plugin_name": self.plugin_name,
            "config": self.config
        }
