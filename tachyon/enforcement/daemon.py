import os
import asyncio
from typing import Dict, Any
from agents._core.registry import AgentRegistry
from tachyon.core.telemetry import TelemetryBus
from tachyon.enforcement.router import ToolRouter

class SubstrateDaemon:
    """
    The High-Assurance Substrate Daemon.
    Orchestrates agent plugins via the AgentRegistry.
    """
    def __init__(self):
        self.registry = AgentRegistry()
        self.registry.discover_plugins()
        self.router = ToolRouter()
        self.bus = TelemetryBus()

    async def start(self):
        self.bus.emit_event("SUBSTRATE_START", "system", status="SUCCESS")
        print("🚀 Tachyon Tongs Substrate Daemon Operational.")
        
    async def dispatch_action(self, agent_id: str, action: str, params: Dict[str, Any]):
        plugin = self.registry.get_plugin(agent_id)
        if not plugin:
            raise ValueError(f"Agent {agent_id} not found in registry.")
        
        return plugin.execute_action(action, params)

if __name__ == "__main__":
    daemon = SubstrateDaemon()
    asyncio.run(daemon.start())
