import os
from .exceptions import BehaviorAnomalyError

class SyscallBehaviorMonitor:
    """
    Tachyon Tongs: Statistical Syscall Monitor.
    Tracks the statistical ratio of network vs filesystem/execution actions.
    If an agent dramatically shifts its baseline, it flags a potential hijack.
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
        ratio = stats["network"] / float(stats["execute"])
        
        total_calls = stats["network"] + stats["execute"]
        if total_calls > 10:  # Allow grace period
            if ratio > self.drift_threshold or ratio < (1.0 / self.drift_threshold):
                self._flag_anomaly(agent_id, stats)
                raise BehaviorAnomalyError(f"Statistical syscall drift detected for {agent_id}.")
                
        return True
        
    def _flag_anomaly(self, agent_id: str, stats: dict):
        """Write an anomaly report to alert the operator."""
        report = f"""# ANOMALY DETECTED: {agent_id}
**Incident Type:** Identity Hijacking / Statistical Drift
**Details:** The agent's baseline access ratio exceeded the `{self.drift_threshold}` safety threshold. 
**Current State:**
- Network Fetches: {stats['network']}
- System Executions: {stats['execute']}
The agent has been automatically halted.
"""
        base_dir = os.path.dirname(__file__)
        error_path = os.path.join(base_dir, '..', '..', 'ERROR.md')
        with open(error_path, 'a') as f:
            f.write(report + "\n---\n")

# Global singleton
syscall_monitor = SyscallBehaviorMonitor()
