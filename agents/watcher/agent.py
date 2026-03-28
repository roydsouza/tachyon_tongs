"""
Tachyon Tongs: The Watcher (S-07)
Performs runtime behavioral auditing via Capability Verification (ACV).
Ensures agents do not exceed their delegated permissions.
"""
import json
from datetime import datetime
from typing import Dict, Any, List, Union
from agents._core.base import BaseAgentPlugin
from tachyon.core.results import TachyonResult

class WatcherPlugin(BaseAgentPlugin):
    """
    Security Agent: Capability Verification (ACV)
    Monitors the EventBus for ACTION_COMPLETED and verifies permissions.
    """
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "Watcher", config)
        self.subscribe("ACTION_COMPLETED", self._audit_action)
        self.start_backplane_loop()

    def _audit_action(self, event_data: Dict[str, Any]):
        """
        Audits an action against the agent's certificate.
        Expected record format from BaseAgentPlugin._backplane_loop.
        """
        payload = event_data.get("payload", {})
        agent_id = event_data.get("agent_id")
        action = payload.get("action")
        
        # S-07: Extract certificate from the event context
        cert_json = event_data.get("certificate_json")
        cert = json.loads(cert_json) if cert_json else None
        
        print(f"[Watcher] Auditing event from {agent_id} for action '{action}'...")
        
        if not cert:
             print(f"[Watcher] No certificate found for {agent_id} in event. Attempting load...")
             # Fallback to fetching state from StateManager if missing in event
             cert = self.im.load_agent_identity(agent_id.split("-")[0].lower())
             
        if not cert:
            from tachyon.core.state import StateManager
            StateManager().emit_alert("WATCHER_UNAUTHORIZED_AGENT", f"Agent {agent_id} performed action {action} WITHOUT a valid delegation certificate.")
            return

        allowed_actions = cert.get("payload", {}).get("subject", {}).get("allowed_actions", [])
        
        if action not in allowed_actions:
            from tachyon.core.state import StateManager
            StateManager().emit_alert("WATCHER_CAPABILITY_VIOLATION", 
                f"PRIVILEGE ESCALATION: Agent {agent_id} attempted unauthorized action '{action}'. Allowed: {allowed_actions}")

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Union[TachyonResult, Dict[str, Any]]:
        """The Watcher usually operates as a passive auditor."""
        if action == "GET_AUDIT_SUMMARY":
            return TachyonResult.success({"status": "AUDIT_ACTIVE", "agent_id": self.agent_id})
        return TachyonResult.failure(f"Unknown movement: {action}")
