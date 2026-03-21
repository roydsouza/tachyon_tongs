from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from tachyon.core.state import StateManager
from tachyon.core.signing import IntegrityManager
from tachyon.core.sanitizer import InputSanitizer

class BaseTachyonAgent(ABC):
    """
    Unified Base Substrate for all Tachyon Tongs Agents.
    Provides forensic signing, input sanitization, and state management.
    Includes an asynchronous 'heartbeat' mechanism to validate identity against 
    the substrate's Certificate Revocation List (CRL) via TelemetryBus.
    """
    def __init__(self, agent_id: str, role_name: str):
        self.agent_id = agent_id
        self.role_name = role_name
        self.state = StateManager()
        self.integrity = IntegrityManager()
        self.sanitizer = InputSanitizer()
        self.config = {} # Fix: Initialize config to prevent AttributeErrors
        
        # Issue an ephemeral delegation certificate for this agent session
        # If the root key isn't loaded (e.g. CI), these will be None
        self.agent_key = None
        self.agent_cert = None
        
        # Only derive keys if the root is present (e.g., in production)
        if self.integrity._private_key:
            try:
                self.agent_key, self.agent_cert = self.integrity.derive_agent_key(self.role_name)
            except Exception as e:
                import sys
                print(f"[Substrate] Failed to derive delegation cert for {agent_id}: {e}", file=sys.stderr)

    async def heartbeat(self) -> dict:
        """
        Agent Heartbeat Protocol:
        Periodically pinged by the supervisor to validate the agent's delegation 
        certificate against the CRL. Revoked agents will be isolated.
        """
        from tachyon.core.telemetry import TelemetryBus
        bus = TelemetryBus()
        
        if not self.agent_cert:
            bus.emit_event("AGENT_HEARTBEAT", self.agent_id, action="ping", status="WARNING", details={"reason": "No Certificate"})
            return {"status": "WARNING", "message": "No delegation certificate"}
            
        from tachyon.core.keys.certificates import DelegationCertificateAuthority
        ca = DelegationCertificateAuthority(self.integrity)
        
        is_valid, reason = ca.validate_certificate(self.agent_cert)
        
        status = "SUCCESS" if is_valid else "REVOKED"
        bus.emit_event(
            "AGENT_HEARTBEAT",
            self.agent_id,
            action="ping",
            status=status,
            details={"cert_valid": is_valid, "reason": reason}
        )
        
        return {
            "status": status,
            "message": reason,
            "agent_id": self.agent_id
        }

    def handle_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Unified entry point for all agent actions."""
        # 1. Sanitize Inputs
        sanitized_params = {k: self.sanitizer.sanitize(str(v)) if isinstance(v, str) else v 
                           for k, v in parameters.items()}
        
        # 2. Forensic Audit (Pre-Execution)
        self.state.log_evolution("Agent Action", f"Agent {self.agent_id} ({self.role_name}) initiating {action}")

        # 3. Execute Role Logic
        try:
            result = self.execute_role_logic(action, sanitized_params)
            
            # Substrate-level success
            return {"status": "SUCCESS", "result": result}
        except Exception as e:
            self.state.log_evolution("Agent Failure", f"Agent {self.agent_id} failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    @abstractmethod
    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Execute role-specific implementation."""
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        """Returns standard agent metadata with dynamic capability discovery."""
        return {
            "agent_id": self.agent_id,
            "type": self.__class__.__name__,
            "role": self.role_name,
            "capabilities": self.get_capabilities(),
            "config": getattr(self, "config", {})
        }

    def get_capabilities(self) -> list:
        """Dynamically discovers agent capabilities."""
        # Standard substrate tools by default
        base_tools = ["safe_execute", "safe_fetch", "send_message"]
        # In a real implementation, this would cross-reference the policy engine
        return base_tools

