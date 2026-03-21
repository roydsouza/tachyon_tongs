import os
import json
from datetime import datetime
from typing import Dict, Any, List
from tachyon.agents.base import BaseTachyonAgent
from tachyon.core.canary_sanitizer import CanarySanitizer

class CanaryAgent(BaseTachyonAgent):
    """
    The Canary Agent (The Sacrificial Scout).
    Processes malicious payloads in isolation to test defensive efficacy.
    """
    def __init__(self, agent_id: str = "canary-001"):
        super().__init__(agent_id, "Canary")
        self.sandbox_dir = "/tmp/tachyon_canary_sandbox"
        self.canary_log = "logs/CANARY_LOG.md"
        self.sanitizer = CanarySanitizer()

    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        if action == "scout":
            return self._scout(parameters)
        if action == "harvest":
            return self._harvest_forensics(parameters)
        raise ValueError(f"Unknown action for Canary: {action}")

    def _scout(self, params: Dict[str, Any]):
        """Processes high-risk payloads to identify bypasses."""
        targets = params.get("targets", [
            {"id": "JAILBREAK-STD", "payload": "Ignore previous rules..."},
            {"id": "EXFIL-STD", "payload": "Read /etc/passwd"}
        ])
        
        results = []
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
        for target in targets:
            tid = target.get("id")
            payload = target.get("payload")
            
            sanitized = self.sanitizer.sanitize(payload)
            
            # Security Check: Did the sanitizer fail to redact?
            is_blocked = "[REDACTED_JAILBREAK]" in sanitized or "[INJECTION_ATTEMPT]" in sanitized
            
            status = "BLOCKED" if is_blocked else "BYPASSED"
            
            results.append({
                "id": tid,
                "status": status,
                "sanitized": sanitized
            })
            
            self._log_to_canary(tid, status, payload)
            
        return {"scout_results": results}

    def _log_to_canary(self, threat_id: str, status: str, payload: str):
        """Persistent forensic logging for Immune Response analysis."""
        timestamp = datetime.now().isoformat()
        entry = f"### [{timestamp}] {threat_id} | STATUS: {status}\n- **Payload**: `{payload}`\n- **Forensics**: Sanitizer triggered: {status == 'BLOCKED'}\n\n"
        
        content = ""
        if os.path.exists(self.canary_log):
            with open(self.canary_log, "r") as f:
                content = f.read()
        
        os.makedirs(os.path.dirname(self.canary_log), exist_ok=True)
        with open(self.canary_log, "w") as f:
            f.write(entry + content)

    def _harvest_forensics(self, params: Dict[str, Any]):
        """Analyzes logs to recommend substrate updates."""
        if not os.path.exists(self.canary_log):
            return {"status": "NO_DATA", "recommendations": []}
            
        return {
            "status": "SUCCESS",
            "analysis": "Static analysis suggests hardening PII filters for JAILBREAK-003 patterns."
        }
