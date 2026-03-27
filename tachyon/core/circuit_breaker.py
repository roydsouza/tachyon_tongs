import time
from typing import Dict, Any, Optional

class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern (M-02).
    States: CLOSED, OPEN, HALF_OPEN.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = 0.0

    def can_execute(self) -> bool:
        """Checks if the circuit is closed or ready for a half-open retry."""
        if self.state == "CLOSED":
            return True
            
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
            
        if self.state == "HALF_OPEN":
            return True
            
        return False

    def record_success(self):
        """Resets the circuit on successful execution."""
        self.state = "CLOSED"
        self.failures = 0

    def record_failure(self):
        """Increments failure count and opens circuit if threshold reached."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
