import asyncio
from typing import Dict, Any, Optional

class ToolRouter:
    """
    Unified tool routing logic for Tachyon Tongs.
    Consolidates behavioral monitoring and policy enforcement across different
    entry points (HTTP Substrate Daemon, MCP Gateway).
    """
    
    def __init__(self, orchestrator, sandbox, policy_engine, cot_monitor, syscall_monitor, rate_limiter=None):
        self.orchestrator = orchestrator
        self.sandbox = sandbox
        self.policy_engine = policy_engine
        self.cot_monitor = cot_monitor
        self.syscall_monitor = syscall_monitor
        self.rate_limiter = rate_limiter
    
    async def route(self, agent_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes a tool call through the safety funnel.
        0. Rate Limiting (Adaptive throttle)
        1. Behavioral check (Statistical drift)
        2. Policy check (Deterministic OPA/Cedar)
        3. Execution via Sandbox or Prophylactic Pipeline
        """
        # 0. Rate Limiting
        if self.rate_limiter:
            allowed, reason = self.rate_limiter.is_allowed(agent_id, action)
            if not allowed:
                return {
                    "status": "BLOCKED",
                    "error": f"RATE_LIMIT_EXCEEDED: {reason}"
                }

        # 1. Statistical Behavioral Check
        self.syscall_monitor.log_and_evaluate(agent_id, action)
        
        # 2. Policy Enforcement Check
        if not self.policy_engine.is_action_allowed(agent_id, action, params):
            return {
                "status": "BLOCKED",
                "error": f"Policy violation: Action '{action}' denied for agent '{agent_id}'."
            }
            
        # 3. Final Execution
        try:
            if action == "safe_execute":
                result = await self.sandbox.execute(params.get("command"), params.get("env"))
            elif action == "safe_fetch":
                result = await self.orchestrator.fetch_and_sanitize(params.get("url"), agent_id)
            elif action == "send_message":
                # Outbound DLP (Reverse Firewall)
                # We reuse the policy engine to check if the message content is allowed
                if not self.policy_engine.is_action_allowed(agent_id, "outbound_dlp", params):
                    return {
                        "status": "BLOCKED",
                        "error": "Outbound message blocked by Reverse Firewall (DLP violation)."
                    }
                # If we had a real messaging client, we'd send it here.
                result = {"status": "sent", "recipient": params.get("recipient")}
            else:
                return {"status": "ERROR", "error": f"Unknown action: {action}"}
                
            return {"status": "SUCCESS", "result": result}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
