import os
import yaml
import importlib
from typing import Dict, Type, Optional
from agents._core.base import BaseAgentPlugin

class AgentRegistry:
    """
    Central registry for Tachyon Tongs agent plugins.
    Handles autonomous discovery and instantiation.
    """
    _plugins: Dict[str, Type[BaseAgentPlugin]] = {}

    @classmethod
    def register(cls, name: str):
        def wrapper(plugin_class: Type[BaseAgentPlugin]):
            cls._plugins[name] = plugin_class
            return plugin_class
        return wrapper

    @classmethod
    def discover_plugins(cls, agents_dir: str):
        """Walks the agents directory subdirectories to find and load plugins."""
        for root, dirs, files in os.walk(agents_dir):
            if "config.yaml" in files:
                agent_name = os.path.basename(root)
                # Determine the module path relative to agents/ root
                # e.g., if root is agents/code-only/canary, module should be agents.code_only.canary.agent
                rel_path = os.path.relpath(root, os.path.dirname(agents_dir))
                module_parts = rel_path.replace(os.sep, ".").split(".")
                plugin_module_name = ".".join(module_parts) + ".agent"
                
                try:
                    importlib.import_module(plugin_module_name)
                except ImportError as e:
                    print(f"[AgentRegistry] Failed to load plugin {agent_name} from {plugin_module_name}: {e}")

    @classmethod
    def get_plugin(cls, name: str) -> Optional[Type[BaseAgentPlugin]]:
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls) -> list:
        return list(cls._plugins.keys())
