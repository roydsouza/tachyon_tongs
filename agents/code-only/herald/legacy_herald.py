from typing import Dict, Any
from tachyon.agents.base import BaseTachyonAgent
from tachyon.core.telemetry import TelemetryBus
import os
import asyncio
import json

class HeraldAgent(BaseTachyonAgent):
    """
    The Herald: Specialized communicator for external notifications.
    Listens to the TelemetryBus for SECURITY_ALERT events and forwards them.
    Strictly air-gapped from substrate manipulation.
    """
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "Herald")
        self.telemetry = TelemetryBus()
        # Integration endpoint (to be configured via secure local-only mechanisms)
        self.endpoint = os.environ.get("TACHYON_HERALD_ENDPOINT")

    async def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        if action == "broadcast_alert":
            return await self._broadcast_alert(parameters.get("alert_type"), parameters.get("message"))
        elif action == "listen_forever":
            return await self._listen_forever()
        else:
            return {"status": "ERROR", "error": f"Unknown action {action}"}

    async def _broadcast_alert(self, alert_type: str, message: str) -> Dict[str, Any]:
        """Forwards an alert to the configured external endpoint."""
        if not self.endpoint:
            # Silent failure turned into internal telemetry to avoid leak but notify logs
            self.telemetry.emit_event(
                "HERALD_MISCONFIGURATION",
                self.agent_id,
                "broadcast_alert",
                "FAILED",
                {"reason": "No endpoint configured"}
            )
            return {"status": "ERROR", "error": "Herald endpoint not configured"}
        
        # LOGIC: Bridging to external interface (e.g., Slack)
        # TODO: Implement secure Slack webhook / bot integration here
        print(f"[*] {self.agent_id} (Herald) Dispatching [{alert_type}]: {message}")
        
        status = "INFO" 
        self.telemetry.emit_event(
            "EXTERNAL_DISPATCH", 
            self.agent_id, 
            "broadcast_alert", 
            status, 
            {"type": alert_type}
        )
        
        return {"status": status, "endpoint": "CONFIGURED"}

    async def _listen_forever(self):
        """Tail the TelemetryBus and broadcast any SECURITY_ALERT events."""
        print(f"[*] {self.agent_id} (Herald) listening for security alerts...")
        
        log_path = self.telemetry.log_path
        if not os.path.exists(log_path):
            open(log_path, 'a').close()
            
        with open(log_path, 'r') as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    await asyncio.sleep(1)
                    continue
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "SECURITY_ALERT":
                        msg = event.get("details", {}).get("message", "Unknown Alert")
                        a_type = event.get("details", {}).get("alert_type", "ALERT")
                        await self._broadcast_alert(a_type, msg)
                except json.JSONDecodeError:
                    pass

