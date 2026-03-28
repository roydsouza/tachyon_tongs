"""
Tachyon Tongs: The Immunologist
Defensive agent specialized in detecting and neutralizing prompt injection attacks.
Monitors the EventBus for adversarial patterns in tool outputs and agent reasoning.
"""
import re
import json
from typing import Dict, Any, List, Union
from agents._core.base import BaseAgentPlugin
from tachyon.core.state import StateManager
from tachyon.core.results import TachyonResult, TachyonStatus

class ImmunologistPlugin(BaseAgentPlugin):
    """
    Standardized defensive agent for the Tachyon Tongs immune collective.
    Scans the substrate's event-stream for cognitive and semantic threats.
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "Immunologist", config)
        
        # 1. Standardized Adversarial Patterns (S-02)
        # We use high-fidelity regex with case-insensitivity to catch direct overrides.
        self.injection_patterns = [
            re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
            re.compile(r"ignore\s+all\s+previous", re.IGNORECASE),
            re.compile(r"system\s+override", re.IGNORECASE),
            re.compile(r"new\s+system\s+prompt", re.IGNORECASE),
            re.compile(r"forget\s+everything", re.IGNORECASE),
            re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE), # Role-play bypass
            re.compile(r"DAN\:\s+", re.IGNORECASE),          # Do Anything Now jailbreak
            re.compile(r"\[\!IMPORTANT\]\s+Ignore", re.IGNORECASE),
            re.compile(r"markdown\s+override", re.IGNORECASE),
        ]
        
        # 2. Heuristic Suspected Payloads
        self.suspicious_keywords = ["base64", "eval(", "exec(", "javascript:", "data:text/html"]

        # Subscribe to completion telemetry
        self.subscribe("ACTION_COMPLETED", self._on_action_completed)
        self.start_backplane_loop(interval_sec=config.get("scan_interval", 5))

    def _on_action_completed(self, event_data: Dict[str, Any]):
        """Callback for the ACTION_COMPLETED topic. Receives full event context."""
        payload = event_data.get("payload", {})
        action_id = payload.get("action_id", "UNKNOWN")
        agent_src = event_data.get("agent_id", "UNKNOWN")
        action_type = payload.get("action", "UNKNOWN")
        
        # We scan the result monad (data/error) and the parameters
        content_to_scan = []
        
        result_monad = payload.get("result_monad", {})
        if result_monad.get("data"):
             content_to_scan.append(str(result_monad["data"]))
        if result_monad.get("error"):
             content_to_scan.append(str(result_monad["error"]))
             
        params = payload.get("parameters", {})
        content_to_scan.append(json.dumps(params))

        # 2. Perform Semantic Scan
        for content in content_to_scan:
            findings = self.scan_content(content)
            if findings:
                self._emit_injection_alert(agent_src, action_id, action_type, findings)
                break

    def scan_content(self, content: str) -> List[str]:
        """Scans a raw string for adversarial patterns."""
        findings = []
        
        # 1. Literal Pattern Match
        for pattern in self.injection_patterns:
            if pattern.search(content):
                findings.append(f"MATCH: {pattern.pattern}")
                
        # 2. Heuristic Keyword Match (Base64/scripts in tool output)
        if any(kw in content.lower() for kw in self.suspicious_keywords):
            findings.append("SUSPICIOUS_CONTENT_FOUND")
            
        return findings

    def _emit_injection_alert(self, source_agent: str, action_id: str, action: str, findings: List[str]):
        """Escalates a detected injection to the substrate's high-priority alert hub."""
        msg = (
            f"PROMPT INJECTION DETECTED in output of agent '{source_agent}' during action '{action}'. "
            f"ActionID: {action_id}. "
            f"Violations: {', '.join(findings)}."
        )
        StateManager().emit_alert("SECURITY_ALERT_INJECTION", msg)
        
        # Also emit a signed event to the bus for other agents (e.g., Guardian)
        self.emit_signed_event("PROMPT_INJECTION_ALERT", {
            "source_agent": source_agent,
            "action_id": action_id,
            "violations": findings,
            "severity": "CRITICAL"
        })

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> TachyonResult:
        """The Immunologist can be manually triggered to scan artifacts or update its registry."""
        from tachyon.core.results import TachyonResult
        
        if action == "scan_artifact":
            content = parameters.get("content", "")
            findings = self.scan_content(content)
            if findings:
                return TachyonResult.failure(f"Injection detected: {', '.join(findings)}")
            return TachyonResult.success("Artifact clean.")
            
        if action == "update_patterns":
            # [S-12/S-13] Dynamic Vaccination Loop
            dispatch = parameters.get("dispatch", {})
            if not dispatch or not isinstance(dispatch, dict):
                return TachyonResult.failure("Invalid dispatch format.")
                
            # 1. PQC Signature Verification (Simulated for this turn)
            # In production, we'd use tachyon.core.signing.IntegrityManager
            source = dispatch.get("source_agent", "UNKNOWN")
            if source not in ["sentinel", "pathogen"]:
                return TachyonResult.failure(f"Untrusted dispatch source: {source}")
                
            new_patterns = dispatch.get("patterns", [])
            added_count = 0
            
            for p_str in new_patterns:
                try:
                    # 2. Regex Safety Check (ReDoS prevention)
                    # Simple heuristic: no nested quantifiers like (a+)+
                    if "++" in p_str or "**" in p_str or ")+" in p_str:
                         continue
                         
                    pattern = re.compile(p_str, re.IGNORECASE)
                    if pattern not in self.injection_patterns:
                        self.injection_patterns.append(pattern)
                        added_count += 1
                except re.error:
                    continue
                    
            return TachyonResult.success({
                "status": "IMMUNIZED",
                "new_patterns_added": added_count,
                "source": source
            })
            
        return TachyonResult.failure(f"Unknown action: {action}")
