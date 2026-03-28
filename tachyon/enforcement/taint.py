"""
Tachyon Tongs: Semantic Taint Tracking (S-06)
Implements data labeling and exfiltration prevention.
"""
import re
from typing import List, Dict, Any, Optional

class TaintPolicy:
    """
    Registry of sensitive patterns and exfiltration rules.
    """
    
    # 🧪 Tier 1: High-Assurance Secrets
    SECRET_PATTERNS = [
        # AI API Keys
        r"sk-[a-zA-Z0-9]{48}", # OpenAI
        r"AIzaSy[a-zA-Z0-9_-]{33}", # Google Cloud / Gemini
        # Infrastructure
        r"xoxp-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}", # Slack User Token
        r"ghp_[a-zA-Z0-9]{36}", # GitHub PAT
        # Tachyon Specific
        r"TACHYON_SECRET_[a-zA-Z0-9]{32}"
    ]

    def __init__(self):
        self._compiled_patterns = [re.compile(p) for p in self.SECRET_PATTERNS]

    def is_tainted(self, payload: str) -> bool:
        """Checks if a payload contains any 'Deep Secret' patterns."""
        if not payload:
            return False
        
        for p in self._compiled_patterns:
            if p.search(payload):
                return True
        return False

    def redact_taint(self, payload: str) -> str:
        """Redacts all detected secrets from the payload."""
        if not payload:
            return payload
            
        redacted = payload
        for p in self._compiled_patterns:
            redacted = p.sub("[REDACTED_SECRET]", redacted)
        return redacted

    def audit_taint_violation(self, agent_id: str, topic: str, payload_summary: str):
        """Logs a persistent record of the exfiltration attempt."""
        from tachyon.core.state import StateManager
        msg = f"EXFILTRATION ATTEMPT: Agent '{agent_id}' attempted to relay tainted content on topic '{topic}'."
        StateManager().emit_alert("SECURITY_ALERT_TAINT", msg)
        StateManager().log_forensic_event(agent_id, "TAINT_VIOLATION", msg)
