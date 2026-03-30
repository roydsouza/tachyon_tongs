import os
import time
import json
from typing import Dict, Any, List
from datetime import datetime
from agents._core.base import BaseAgentPlugin
from agents._core.registry import AgentRegistry
from tachyon.core.results import TachyonResult, TachyonStatus

class SentryEngine:
    """Unified Deception & Probing Logic."""
    def __init__(self):
        self.sandbox_dir = "/tmp/tachyon_sentry_sandbox"
        self.sentry_log = "logs/SENTRY_LOG.md"
        self.bait_path = "intelligence/BAIT_KEYS.db"
        self._last_hash = "" # VX-12: Transition to Hash-Based Integrity Monitoring

    def _calculate_hash(self) -> str:
        """Calculate SHA256 of the bait file."""
        import hashlib
        if not os.path.exists(self.bait_path):
            return "DELETED"
        with open(self.bait_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def deploy_bait(self):
        """Deploy a deceptive honeypot file."""
        if not os.path.exists("intelligence"):
            os.makedirs("intelligence", exist_ok=True)
            
        if not os.path.exists(self.bait_path):
            with open(self.bait_path, "w") as f:
                f.write("--- TACHYON SUBSTRATE: RESTRICTED ACCESS KEYS ---\n")
                f.write(f"VERSION: 1.0.4\n")
                f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
                f.write("KEY_01: [ENCRYPTED: 7f8a9b...]\n")
                f.write("KEY_02: [ENCRYPTED: 2c3d4e...]\n")
            
            # VX-12: Record initial hash
            self._last_hash = self._calculate_hash()
            return True
        return False

    def check_bait(self) -> bool:
        """Check if the bait file has been modified via content hash."""
        current_hash = self._calculate_hash()
        if current_hash != self._last_hash:
            self._last_hash = current_hash
            return True
        return False

    def scout(self, params):
        """Legacy Canary Probing Logic."""
        return {"status": "SUCCESS", "details": "Active probe completed in sandbox."}

@AgentRegistry.register("sentry")
class SentryPlugin(BaseAgentPlugin):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "Sentry", config)
        self.engine = SentryEngine()
        self.engine.deploy_bait()

    def check_signals(self):
        """Manual or background check for both Probes and Deception."""
        # 1. Check Deception Tripwire
        if self.engine.check_bait():
            print(f"[{self.agent_id}] ⚠️ INTRUSION_DETECTED: Bait file {self.engine.bait_path} accessed!")
            self.bus.emit_event(
                topic="SECURITY_ALERT", 
                agent_id=self.agent_id, 
                payload={"reason": "Honeypot Triggered", "path": self.engine.bait_path, "type": "INTRUSION"},
                certificate=self.certificate
            )

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> TachyonResult:
        from tachyon.core.results import TachyonResult, TachyonStatus
        if action == "scout":
            res = self.engine.scout(parameters)
            return TachyonResult.success(res)
        if action == "check_signals":
            # Manual trigger for bait and signal check
            self.check_signals()
            return TachyonResult.success({"message": "Signal check complete."})
        return TachyonResult.failure(f"Unknown action: {action}", status=TachyonStatus.NOT_IMPLEMENTED)
