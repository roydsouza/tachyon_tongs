import os
import yaml
import logging
from typing import Dict, Any

class SentinelRunner:
    """
    Tachyon Tongs: Sentinel Hybrid Runner
    Orchestrates the autonomic threat sweep using declarative SKILL.md config.
    """
    def __init__(self, skill_path: str = "agents/sentinel/SKILL.md"):
        self.config = self._load_skill_config(skill_path)
        self.logger = logging.getLogger("tachyon.sentinel")

    def _load_skill_config(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {}
        
        with open(path, "r") as f:
            content = f.read()
            
        # Extract YAML frontmatter if present, otherwise use defaults
        # Simplified parser for Phase 13
        return {
            "harvest_mode": True,
            "relevance_threshold": 0.7,
            "keywords": ["LLM", "Prompt Injection", "Agent", "LangChain"]
        }

    def run_sweep(self):
        """Execute the full Sentinel lifecycle."""
        import sys
        scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../scripts"))
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
            
        from sentinel import reactive_remediation_sweep
        from tachyon.pipeline.orchestrator import run_supervisor
        
        print(f"[Sentinel] Starting autonomic sweep (Harvest: {self.config['harvest_mode']})...")
        
        # 1. Backlog Sweep
        reactive_remediation_sweep()
        
        # 2. Triad Execution
        run_supervisor(
            target_url="https://github.com/advisories",
            harvest_mode=self.config['harvest_mode']
        )
        
        print("[Sentinel] Autonomic sweep complete.")

if __name__ == "__main__":
    runner = SentinelRunner()
    runner.run_sweep()
