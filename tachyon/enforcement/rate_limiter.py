import time
from typing import Dict, Any, Tuple
from dataclasses import dataclass, field

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    burst_limit: int = 10

class AdaptiveRateLimiter:
    """
    Tachyon Tongs: Adaptive Rate-Limiter
    Throttles agent tool calls to prevent loops and substrate abuse.
    """
    def __init__(self, default_rpm: int = 30):
        self.default_rpm = default_rpm
        # Key: (agent_id, action), Value: [timestamps]
        self.history: Dict[Tuple[str, str], list] = {}
        
    def is_allowed(self, agent_id: str, action: str) -> Tuple[bool, str]:
        """Checks if the action is within rate limits for the given agent."""
        key = (agent_id, action)
        now = time.time()
        
        if key not in self.history:
            self.history[key] = []
            
        # Clean up history older than 60 seconds
        self.history[key] = [t for t in self.history[key] if now - t < 60]
        
        # Check against threshold
        if len(self.history[key]) >= self.default_rpm:
            return False, f"Rate limit exceeded for tool '{action}'. Maximum {self.default_rpm} requests per minute."
            
        # Record this request
        self.history[key].append(now)
        return True, "Allowed"

    def reset(self, agent_id: str = None):
        """Resets counters for an agent or all agents."""
        if agent_id:
            keys_to_remove = [k for k in self.history.keys() if k[0] == agent_id]
            for k in keys_to_remove:
                del self.history[k]
        else:
            self.history.clear()
