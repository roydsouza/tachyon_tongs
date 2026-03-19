import logging
import yaml
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("tachyon.core.routing")

class ModelRouter:
    """
    Autonomous Model Router for Substrate Optimization.
    Routes tasks to the appropriate model based on complexity and skill-defined logic.
    """
    
    DEFAULT_SKILL_PATH = "agents/skills/substrate-optimizer/SKILL.md"
    
    def __init__(self, skill_path: Optional[str] = None):
        self.skill_path = Path(skill_path or self.DEFAULT_SKILL_PATH)
        self.routing_matrix = self._load_routing_matrix()
        self.lpm_threshold = 0.15 # 15% quota
        
    def _load_routing_matrix(self) -> Dict[str, str]:
        """Loads the routing matrix from the SKILL.md file."""
        # In a real implementation, this would parse the markdown table.
        # For simplicity, we hardcode based on the SKILL.md content.
        return {
            "L1": "gemini-3-flash",
            "L2": "gemini-3-flash",
            "L3": "gemini-3.1-pro"
        }
        
    def select_model(self, task_description: str, complexity_score: float, current_quota: float = 1.0) -> str:
        """
        Selects the appropriate model based on task complexity and current quota.
        """
        # Low Power Mode (LPM) check
        if current_quota < self.lpm_threshold:
            logger.warning("Low Power Mode active! Forcing Flash model.")
            return "gemini-3-flash"
            
        # Complexity-based routing
        if complexity_score < 0.4:
            return self.routing_matrix["L1"]
        elif complexity_score < 0.7:
            return self.routing_matrix["L2"]
        else:
            return self.routing_matrix["L3"]

    def detect_complexity(self, prompt: str) -> float:
        """
        Rudimentary complexity detection based on prompt analysis.
        (Placeholder for a more sophisticated LLM-based or heuristic-based algorithm)
        """
        prompt_lower = prompt.lower()
        score = 0.1 # Lower baseline for simple tasks
        
        keywords_high = ["adr", "architectural", "refactor", "regression", "root cause", "attestation", "pqc"]
        for kw in keywords_high:
            if kw in prompt_lower:
                score += 0.4 # Significant jump for high-intel keywords
                
        return min(score, 1.0)
