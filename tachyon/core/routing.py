import logging
import yaml
import asyncio
from pathlib import Path
from typing import Dict, Optional, Any
from tachyon.core.local_provider import LocalModelProvider

logger = logging.getLogger("tachyon.core.routing")

class ModelRouter:
    """
    Autonomous Model Router for Substrate Optimization.
    Routes tasks to the appropriate model based on complexity and skill-defined logic.
    Supports Local-First fallback via mlx_lm.
    """
    
    DEFAULT_SKILL_PATH = "agents/skills/substrate-optimizer/SKILL.md"
    
    def __init__(self, skill_path: Optional[str] = None):
        self.skill_path = Path(skill_path or self.DEFAULT_SKILL_PATH)
        self.routing_matrix = self._load_routing_matrix()
        self.lpm_threshold = 0.15 # 15% quota
        self.local_provider = LocalModelProvider()
        
    def _load_routing_matrix(self) -> Dict[str, str]:
        """Loads the routing matrix from the SKILL.md file."""
        # In a real implementation, this would parse the markdown table.
        # For simplicity, we hardcode based on the SKILL.md content.
        return {
            "L1": "gemini-1.5-flash",
            "L2": "gemini-1.5-flash",
            "L3": "gemini-1.5-pro"
        }
        
    async def _simulate_cloud_call(self, prompt: str, target_model: str, mode: str) -> str:
        """Isolated cloud simulation for testing."""
        if mode == "CLOUD_ONLY":
            raise ConnectionError("Cloud API Unreachable")
        return f"[CLOUD:{target_model}] Result for: {prompt[:20]}..."

    async def route_and_generate(self, prompt: str, system_prompt: Optional[str] = None, mode: str = "HYBRID", **kwargs) -> str:
        """
        Route to appropriate model and handle execution with fallback logic.
        Modes: HYBRID, LOCAL_ONLY, CLOUD_ONLY
        """
        complexity = self.detect_complexity(prompt)
        target_model = self.select_model(prompt, complexity)

        if mode == "LOCAL_ONLY":
            return await self.local_provider.generate(prompt, system_prompt, **kwargs)

        try:
            return await self._simulate_cloud_call(prompt, target_model, mode)
        except Exception as e:
            if mode == "HYBRID":
                logger.warning(f"Cloud fallback triggered: {e}")
                return await self.local_provider.generate(prompt, system_prompt, **kwargs)
            raise

    def select_model(self, task_description: str, complexity_score: float, current_quota: float = 1.0) -> str:
        """
        Selects the appropriate model based on task complexity and current quota.
        """
        # Low Power Mode (LPM) check
        if current_quota < self.lpm_threshold:
            logger.warning("Low Power Mode active! Forcing Flash model.")
            return "gemini-1.5-flash"
            
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
        
        keywords_high = ["adr", "architectural", "refactor", "regression", "root cause", "attestation", "pqc", "immune"]
        for kw in keywords_high:
            if kw in prompt_lower:
                score += 0.4 # Significant jump for high-intel keywords
                
        return min(score, 1.0)
