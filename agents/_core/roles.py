from typing import Dict, Any, List
from agents._core.base import BaseAgentPlugin

class BaseTachyonRole:
    """Standard role abstraction for plugin wrappers."""
    def __init__(self, agent_id: str, role_name: str):
        self.agent_id = agent_id
        self.role_name = role_name

class GuardianRole(BaseTachyonRole):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "Guardian")

class SentinelRole(BaseTachyonRole):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "Sentinel")
