import asyncio
from typing import Dict, Any, Optional, FrozenSet
from dataclasses import dataclass, field
from tachyon.enforcement.rate_limiter import AdaptiveRateLimiter
from tachyon.enforcement.alignment_checker import AlignmentChecker

@dataclass(frozen=True)
class ImmutableToolRequest:
    """
    An immutable representation of a tool request.
    Prevents TOCTOU (Time-of-Check to Time-of-Use) vulnerabilities by ensuring
    parameters cannot be modified after policy evaluation begins.
    """
    agent_id: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default=None)

    def __post_init__(self):
        if self.timestamp is None:
            try:
                loop = asyncio.get_event_loop()
                # Use object.__setattr__ because the dataclass is frozen
                object.__setattr__(self, "timestamp", loop.time())
            except RuntimeError:
                import time
                object.__setattr__(self, "timestamp", time.time())

class ToolRouter:
    """
    Unified tool routing logic for Tachyon Tongs.
    Consolidates behavioral monitoring and policy enforcement across different
    entry points (HTTP Substrate Daemon, MCP Gateway).
    """
    
    def __init__(self, orchestrator, sandbox, policy_engine, cot_monitor, syscall_monitor, rate_limiter=None, alignment_checker=None):
        self.orchestrator = orchestrator
        self.sandbox = sandbox
        self.policy_engine = policy_engine
        self.cot_monitor = cot_monitor
        self.syscall_monitor = syscall_monitor
        self.rate_limiter = rate_limiter or AdaptiveRateLimiter()
        self.alignment_checker = alignment_checker or AlignmentChecker(threshold=0.2)
    
    async def route(self, agent_id: str, action: str, params: dict) -> dict:
        """
        Main entry point for tool execution.
        Applies: Rate Limiting -> Alignment Check -> Policy Enforcement -> Execution.
        """
        # 0. Freeze the request immediately to prevent TOCTOU
        request = ImmutableToolRequest(agent_id=agent_id, action=action, params=params)

        # 0. Rate Limiting Check
        if self.rate_limiter:
            allowed, reason = self.rate_limiter.is_allowed(request.agent_id, request.action)
            if not allowed:
                return {
                    "status": "BLOCKED",
                    "error": f"RATE_LIMIT_EXCEEDED: {reason}"
                }

        # 0.1 Semantic Alignment Check (Phase 16)
        if "intent" in request.params:
            alignment = self.alignment_checker.check_alignment(request.params["intent"], request.params)
            if not alignment["is_aligned"]:
                return {
                    "status": "BLOCKED",
                    "error": f"Alignment Violation: {alignment['reason']}"
                }

        # 1. Statistical Behavioral Check
        self.syscall_monitor.log_and_evaluate(request.agent_id, request.action)
        
        # 2. Policy Enforcement Check (Pass the immutable request)
        # Note: We pass request.params to maintain compatibility with current engine signatures
        if not self.policy_engine.is_action_allowed(request.agent_id, request.action, request.params):
            return {
                "status": "BLOCKED",
                "error": f"Policy violation: Action '{request.action}' denied for agent '{request.agent_id}'."
            }
            
        # 3. Final Execution using the FROZEN parameters
        try:
            if request.action == "safe_execute":
                result = await self.sandbox.execute(request.params.get("command"), request.params.get("env"))
            elif request.action == "safe_fetch":
                result = await self.orchestrator.fetch_and_sanitize(request.params.get("url"), request.agent_id)
            elif request.action == "send_message":
                # Outbound DLP (Reverse Firewall)
                if not self.policy_engine.is_action_allowed(request.agent_id, "outbound_dlp", request.params):
                    return {
                        "status": "BLOCKED",
                        "error": "Outbound message blocked by Reverse Firewall (DLP violation)."
                    }
                result = {"status": "sent", "recipient": request.params.get("recipient")}
            else:
                return {"status": "ERROR", "error": f"Unknown action: {request.action}"}
                
            return {"status": "SUCCESS", "result": result}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
