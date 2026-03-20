from tachyon.agents.base import BaseTachyonAgent
import os
import subprocess
import httpx
import sys
import json
from datetime import datetime

class SentinelRole(BaseTachyonAgent):
    def __init__(self, agent_id: str):
        from .sentinel.sentinel_role import SentinelRole as RealSentinel
        self._delegate = RealSentinel(agent_id)
        super().__init__(agent_id, "Sentinel")

    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        return self._delegate.execute_role_logic(action, parameters)

class EngineerRole(BaseTachyonAgent):
    def __init__(self, agent_id: str):
        from .engineer.engineer_role import EngineerRole as RealEngineer
        self._delegate = RealEngineer(agent_id)
        super().__init__(agent_id, "Engineer")

    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        return self._delegate.execute_role_logic(action, parameters)

class CanaryRole(BaseTachyonAgent):
    def __init__(self, agent_id: str):
        from .canary import CanaryAgent
        self._delegate = CanaryAgent(agent_id)
        super().__init__(agent_id, "Canary")

    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        return self._delegate.execute_role_logic(action, parameters)

class GuardianRole(BaseTachyonAgent):
    def __init__(self, agent_id: str):
        from .guardian.guardian_role import GuardianRole as RealGuardian
        self._delegate = RealGuardian(agent_id)
        super().__init__(agent_id, "Guardian")

    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        return self._delegate.execute_role_logic(action, parameters)


