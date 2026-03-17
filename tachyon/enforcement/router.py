import asyncio
from typing import Dict, Any, Optional

class ToolRouter:
    """
    Unified tool routing logic for Tachyon Tongs.
    Consolidates behavioral monitoring and policy enforcement across different
    entry points (HTTP Substrate Daemon, MCP Gateway).
    """
    
    def __init__(self, orchestrator, sandbox, policy_engine, cot_monitor, syscall_monitor):
        self.orchestrator = orchestrator
        self.sandbox = sandbox
        self.policy_engine = policy_engine
        self.cot_monitor = cot_monitor
        self.syscall_monitor = syscall_monitor
    
    async def route(self, agent_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes a tool call through the safety funnel.
        1. Behavioral check (Statistical drift)
        2. Policy check (Deterministic OPA/Cedar)
        3. Execution via Sandbox or Prophylactic Pipeline
        """
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
            else:
                return {"status": "ERROR", "error": f"Unknown action: {action}"}
                
            return {"status": "SUCCESS", "result": result}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
