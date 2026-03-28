import os
import yaml
import importlib.util
from typing import Dict, Type, Optional
from agents._core.base import BaseAgentPlugin

class RegistrationError(Exception):
    """Raised when an agent plugin fails to register correctly (SF-04)."""
    pass

class AgentRegistry:
    """
    Central registry for Tachyon Tongs agent plugins.
    Handles autonomous discovery and instantiation.
    """
    _plugins: Dict[str, Type[BaseAgentPlugin]] = {}

    @classmethod
    def register(cls, name: str):
        def wrapper(plugin_class: Type[BaseAgentPlugin]):
            if name in cls._plugins:
                raise RegistrationError(f"Duplicate agent ID registered: {name}")
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
                        # [S-10] Agent Provenance Verification
                        _verify_agent_hash(agents_dir, module_path)
                        
                        spec = importlib.util.spec_from_file_location(plugin_module_name, module_path)
                        module = importlib.util.module_from_spec(spec)
                        if spec and spec.loader:
                            spec.loader.exec_module(module)
                        else:
                            raise RegistrationError(f"Module spec loader missing for {plugin_module_name}")
                except Exception as e:
                    # Always write forensic alert
                    _write_load_failure_alert(agent_name, str(e))
                    # In production/strict mode, fail-loud
                    if os.environ.get("TACHYON_STRICT_MODE") == "1":
                         raise RegistrationError(f"Critical agent load failure: {agent_name} -> {e}")
                    else:
                         print(f"[AgentRegistry] WARNING: Failed to load plugin {agent_name}: {e}")

    @classmethod
    def get_plugin(cls, name: str) -> Optional[Type[BaseAgentPlugin]]:
        return cls._plugins.get(name)

    @classmethod
    def list_plugins(cls) -> list:
        return list(cls._plugins.keys())

def _verify_agent_hash(agents_dir: str, module_path: str):
    """Calculates and verifies the SHA256 hash of an agent implementation [S-10]."""
    import hashlib
    import json
    
    # Calculate current hash
    with open(module_path, "rb") as f:
        content = f.read()
    current_hash = hashlib.sha256(content).hexdigest()
    
    # Load SBOM
    root_dir = os.path.abspath(os.path.join(os.path.dirname(agents_dir), ".."))
    # In some contexts, agents_dir might be just 'agents', resolve to root correctly
    if os.path.basename(agents_dir) == "agents":
        root_dir = os.path.dirname(agents_dir)
        
    hashes_path = os.path.join(root_dir, "metadata", "agent_hashes.json")
    
    # Fallback to absolute workspace path if relative lookup fails
    if not os.path.exists(hashes_path):
        hashes_path = "/Users/rds/antigravity/tachyon_tongs/metadata/agent_hashes.json"

    if not os.path.exists(hashes_path):
        # In strict mode, missing SBOM is a failure
        if os.environ.get("TACHYON_STRICT_MODE") == "1":
            raise RegistrationError(f"SBOM Missing: No agent_hashes.json found at {hashes_path}")
        return

    with open(hashes_path, "r") as f:
        sbom = json.load(f)
        
    # Relative path for SBOM lookup (e.g. agents/sentinel/agent.py)
    rel_module_path = os.path.relpath(module_path, root_dir)
    
    expected_hash = sbom.get(rel_module_path)
    if not expected_hash:
        if os.environ.get("TACHYON_STRICT_MODE") == "1":
            raise RegistrationError(f"Provenance Failure: Agent {rel_module_path} not found in SBOM.")
        return

    if current_hash != expected_hash:
        raise RegistrationError(
            f"PROVENANCE_VIOLATION: Hash mismatch for {rel_module_path}.\n"
            f"Expected: {expected_hash}\n"
            f"Actual:   {current_hash}"
        )

def _write_load_failure_alert(agent_name: str, error: str):
    """Helper to record critical agent load failures when the EventBus is unavailable."""
    import os
    from datetime import datetime
    alert_path = os.path.abspath("ALERT.md")
    entry = f"\n---\n## [AGENT_LOAD_FAILURE] {datetime.now().isoformat()}\n- **Agent**: {agent_name}\n- **Error**: {error}\n"
    with open(alert_path, "a") as f:
        f.write(entry)
