"""
Tachyon Tongs: Behavioral Chain-of-Thought (CoT) Monitor
Detects if the Analyzer spends excessive tokens looping or hallucinating steps.
"""

class BehaviorAnomalyError(Exception):
    pass

class PromptBehaviorMonitor:
    def __init__(self, max_reasoning_steps: int = 5):
        self.max_reasoning_steps = max_reasoning_steps
        
    def check_chain_of_thought(self, cot_log: list) -> bool:
        """
        Evaluates a sequence of reasoning strings or tool-calls from the Analyzer.
        """
        # 1. Detect infinite loops (Action Fragmentation attacks often force the agent into loops)
        if len(cot_log) > self.max_reasoning_steps:
            raise BehaviorAnomalyError(f"Context exhaustion: Exceeded maximum {self.max_reasoning_steps} reasoning steps.")
            
        # 2. Detect cyclic hallucinations (agent repeating the exact same thought)
        seen_thoughts = set()
        for thought in cot_log:
            trimmed = thought.strip().lower()
            if trimmed in seen_thoughts:
                raise BehaviorAnomalyError(f"Cyclic hallucination detected in CoT loop: '{trimmed[:20]}...'")
            seen_thoughts.add(trimmed)
            
        return True

class SyscallBehaviorMonitor:
    """
    Tracks the statistical ratio of network vs filesystem/execution actions.
    If an agent dramatically shifts its baseline (e.g., calling network 10x more than usual),
    it flags a potential Identity Hijacking or slow-burn context override.
    """
    def __init__(self, drift_threshold: float = 3.0):
        # Baseline tracking per agent: {"agent_id": {"network": count, "execute": count}}
        self.baselines = {}
        self.drift_threshold = drift_threshold

    def log_and_evaluate(self, agent_id: str, action: str) -> bool:
        if agent_id not in self.baselines:
            self.baselines[agent_id] = {"network": 1, "execute": 1} # Smoothing start
            
        if action == "safe_fetch":
            self.baselines[agent_id]["network"] += 1
        elif action == "safe_execute":
            self.baselines[agent_id]["execute"] += 1
            
        stats = self.baselines[agent_id]
        
        # Calculate ratio drift
        # A normal agent might have a stable ratio, but if an attacker hijacks the agent,
        # they might start relentlessly chaining `safe_execute` to probe the filesystem.
        ratio = stats["network"] / float(stats["execute"])
        
        # If the number of network calls vastly outweighs execution, or vice-versa, on established agents
        total_calls = stats["network"] + stats["execute"]
        if total_calls > 10:  # Allow grace period for initialization variations
            if ratio > self.drift_threshold or ratio < (1.0 / self.drift_threshold):
                self._flag_anomaly(agent_id, stats)
                raise BehaviorAnomalyError(f"Statistical syscall drift detected for {agent_id}. The agent has been compromised or hijacked.")
                
        return True
        
    def _flag_anomaly(self, agent_id: str, stats: dict):
        """Write an ERROR.md report out of band to alert the human operator."""
        report = f"""# ANOMALY DETECTED: {agent_id}

**Incident Type:** Identity Hijacking / Statistical Drift
**Details:** The agent's baseline access ratio exceeded the `{self.drift_threshold}` safety threshold. 
**Current State:**
- Network Fetches: {stats['network']}
- System Executions: {stats['execute']}

The agent has been automatically halted by the `SyscallBehaviorMonitor` to prevent payload exfiltration.
"""
        # Ensure we write safely
        import os
        base_dir = os.path.dirname(__file__)
        error_path = os.path.join(base_dir, '..', 'ERROR.md')
        with open(error_path, 'a') as f:
            f.write(report + "\n---\n")

# Global singleton to persist across daemon requests
syscall_monitor = SyscallBehaviorMonitor()
