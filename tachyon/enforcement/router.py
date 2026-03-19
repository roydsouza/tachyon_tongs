import asyncio
from typing import Dict, Any, Optional, FrozenSet
from dataclasses import dataclass, field
from tachyon.enforcement.rate_limiter import AdaptiveRateLimiter
from tachyon.enforcement.alignment_checker import AlignmentChecker

from types import MappingProxyType

def recursive_freeze(d: Any) -> Any:
    """Recursively convert dictionaries to MappingProxyType and lists to tuple."""
    if isinstance(d, MappingProxyType):
        return d
    elif isinstance(d, dict):
        return MappingProxyType({k: recursive_freeze(v) for k, v in d.items()})
    elif isinstance(d, list) or isinstance(d, set):
        return tuple(recursive_freeze(i) for i in d)
    elif isinstance(d, tuple):
        return tuple(recursive_freeze(i) for i in d)
    return d

@dataclass(frozen=True)
class ImmutableToolRequest:
    """
    An immutable representation of a tool request.
    Prevents TOCTOU (Time-of-Check to Time-of-Use) vulnerabilities by ensuring
    parameters cannot be modified after policy evaluation begins.
    """
    agent_id: str
    action: str
    params: Any = field(default_factory=dict)
    timestamp: float = field(default=None)

    def __post_init__(self):
        # Freeze params recursively
        object.__setattr__(self, "params", recursive_freeze(self.params))
        
        if self.timestamp is None:
            try:
                loop = asyncio.get_event_loop()
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
        
        # Initialize Tool Registry with standard handlers
        from .registry import registry as tool_registry
        self.registry = tool_registry
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Registers the core substrate tool handlers."""
        self.registry.register("safe_execute", self._handle_safe_execute)
        self.registry.register("safe_fetch", self._handle_safe_fetch)
        self.registry.register("send_message", self._handle_send_message)

    async def _handle_safe_execute(self, agent_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.sandbox.execute(params.get("command"), params.get("env"))

    async def _handle_safe_fetch(self, agent_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.orchestrator.fetch_and_sanitize(params.get("url"), agent_id)

    async def _handle_send_message(self, agent_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Core handler for sending messages. Security checks are handled in the route() pass."""
        return {"status": "sent", "recipient": params.get("recipient")}
    
    async def route(self, agent_id: str, action: str, params: dict) -> dict:
        """
        Main entry point for tool execution.
        Applies: Rate Limiting -> Alignment Check -> Policy Enforcement -> Execution via Registry.
        """
        # 0. Freeze the request immediately to prevent TOCTOU
        request = ImmutableToolRequest(agent_id=agent_id, action=action, params=params)

        # 1. Rate Limiting Check
        if self.rate_limiter:
            allowed, reason = self.rate_limiter.is_allowed(request.agent_id, request.action)
            if not allowed:
                return {
                    "status": "BLOCKED",
                    "error": f"RATE_LIMIT_EXCEEDED: {reason}"
                }

        # 2. Semantic Alignment Check (Phase 16)
        if "intent" in request.params:
            alignment = self.alignment_checker.check_alignment(request.params["intent"], request.params)
            if not alignment["is_aligned"]:
                return {
                    "status": "BLOCKED",
                    "error": f"Alignment Violation: {alignment['reason']}"
                }

        # 3. Statistical Behavioral Check
        self.syscall_monitor.log_and_evaluate(request.agent_id, request.action)
        
        # 4. Policy Enforcement Check (Pass the immutable request)
        if not self.policy_engine.is_action_allowed(request.agent_id, request.action, request.params):
            return {
                "status": "BLOCKED",
                "error": f"Policy violation: Action '{request.action}' denied for agent '{request.agent_id}'."
            }
            
        # 5. Final Execution using the Registry and FROZEN parameters
        try:
            result = await self.registry.execute(request.action, request.agent_id, request.params)
            if isinstance(result, dict) and result.get("status") == "BLOCKED":
                 return result
            if isinstance(result, dict) and result.get("status") == "ERROR":
                 return result
                 
            return {"status": "SUCCESS", "result": result}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
