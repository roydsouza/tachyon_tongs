"""
Tachyon Tongs: Capability Tokens with Time-Based Decay
Counters long-tail agent hijacking by reducing privileges geometrically over time.
"""
import time

class CapabilityToken:
    def __init__(self, token_id: str, capabilities: list, t_decay_seconds: int = 900):
        self.token_id = token_id
        # Capabilities ordered by risk: highest risk strings first for simple degradation mapping
        # E.g., ['admin', 'write', 'read']
        self.capabilities = capabilities
        self.t_decay_seconds = t_decay_seconds
        self.created_at = time.time()
        
    def get_remaining_capabilities(self, current_time: float = None) -> list:
        """
        Returns the subset of capabilities that are still active.
        Privileges decay geometrically: losing the highest-risk capability first.
        """
        if current_time is None:
            current_time = time.time()
            
        elapsed = current_time - self.created_at
        
        # If elapsed time is greater than absolute max decay (e.g., 3 intervals), token is dead
        max_intervals = len(self.capabilities)
        intervals_elapsed = int(elapsed // self.t_decay_seconds)
        
        if intervals_elapsed >= max_intervals:
            return []
            
        # Return the remaining capabilities (losing the front of the list first)
        return self.capabilities[intervals_elapsed:]
        
    def authorize(self, action: str, current_time: float = None) -> bool:
        """Validates if the token still has the rights for a given action."""
        active_caps = self.get_remaining_capabilities(current_time)
        return action in active_caps
