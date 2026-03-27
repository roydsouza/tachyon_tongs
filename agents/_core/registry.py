import os
import yaml
import importlib.util
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
    def discover_plugins(cls, agents_dir: Optional[str] = None):
        """Walks the agents directory subdirectories to find and load plugins."""
        if agents_dir is None:
            # Default to the 'agents' directory in the project root
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            agents_dir = os.path.join(root_dir, "agents")
            
        for root, dirs, files in os.walk(agents_dir):
            if "config.yaml" in files:
                agent_name = os.path.basename(root)
                # Determine the module path relative to agents/ root
                # e.g., agents/sentinel/agent.py -> agents.sentinel.agent
                rel_path = os.path.relpath(root, os.path.dirname(agents_dir))
                module_parts = rel_path.replace(os.sep, ".").split(".")
                plugin_module_name = ".".join(module_parts) + ".agent"
                
                try:
                    # Use importlib.util to support hyphenated paths
                    module_path = os.path.join(root, "agent.py")
                    if os.path.exists(module_path):
                        spec = importlib.util.spec_from_file_location(plugin_module_name, module_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                except Exception as e:
                    print(f"[AgentRegistry] Failed to load plugin {agent_name} from {root}: {e}")
                    _write_load_failure_alert(agent_name, str(e))

    @classmethod
    def get_plugin(cls, name: str) -> Optional[Type[BaseAgentPlugin]]:
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls) -> list:
        return list(cls._plugins.keys())

def _write_load_failure_alert(agent_name: str, error: str):
    """Helper to record critical agent load failures when the EventBus is unavailable."""
    import os
    from datetime import datetime
    alert_path = os.path.abspath("ALERT.md")
    entry = f"\n---\n## [AGENT_LOAD_FAILURE] {datetime.now().isoformat()}\n- **Agent**: {agent_name}\n- **Error**: {error}\n"
    with open(alert_path, "a") as f:
        f.write(entry)
