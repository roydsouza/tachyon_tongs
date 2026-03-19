import os
import yaml
import logging
from typing import Dict, Any

from tachyon.agents.roles import SentinelRole

class SentinelRunner:
    """Consolidated SentinelRunner. Delegates to SentinelRole."""
    def __init__(self, skill_path: str = "agents/sentinel/SKILL.md"):
        self.role = SentinelRole("legacy-sentinel")

    def run_sweep(self):
        return self.role.handle_action("run_sweep", {"harvest_mode": True})

if __name__ == "__main__":
    runner = SentinelRunner()
    runner.run_sweep()
