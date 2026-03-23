from typing import Dict, Any, List
from agents._core.base import BaseAgentPlugin

class BaseTachyonRole:
    """Standard role abstraction for plugin wrappers."""
    def __init__(self, agent_id: str, role_name: str):
        self.agent_id = agent_id
        self.role_name = role_name

    def handle_action(self, action: str, parameters: dict) -> dict:
        """Delegates the action to the registered plugin for this role."""
        from agents._core.registry import AgentRegistry
        import os

        # Discover plugins (Phase 32: ensure everything is loaded)
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        agents_dir = os.path.join(root_dir, "agents")
        AgentRegistry.discover_plugins(agents_dir)
        
        # Mapping role name to registry ID
        registry_id = self.role_name.lower()
        plugin_class = AgentRegistry.get_plugin(registry_id)
        
        if not plugin_class:
            return {"status": "ERROR", "message": f"No plugin registered for role: {self.role_name}"}
            
        # Instantiate and run (Phase 33 pattern)
        plugin = plugin_class(self.agent_id, {})
        return plugin.run_action(action, parameters)
