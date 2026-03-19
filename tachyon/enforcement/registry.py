from typing import Dict, Any, Callable, Coroutine
import asyncio

class ToolRegistry:
    """
    Registry for tool handlers across the Tachyon Tongs substrate.
    Encapsulates action-specific logic and simplifies the ToolRouter.
    """
    def __init__(self):
        self._handlers: Dict[str, Callable[..., Coroutine[Any, Any, Dict[str, Any]]]] = {}

    def register(self, action: str, handler: Callable[..., Coroutine[Any, Any, Dict[str, Any]]]):
        """Registers a new tool handler."""
        self._handlers[action] = handler

    async def execute(self, action: str, agent_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches the action to the registered handler."""
        if action not in self._handlers:
            return {"status": "ERROR", "error": f"Unknown action: {action}"}
        
        handler = self._handlers[action]
        return await handler(agent_id, params)

# Global registry instance
registry = ToolRegistry()
