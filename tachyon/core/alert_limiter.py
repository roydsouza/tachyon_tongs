import time
from collections import defaultdict
from threading import Lock

class AlertRateLimiter:
    """
    Prevents log-flooding DoS by rate-limiting similar alert types.
    """
    def __init__(self, window_seconds: int = 60, max_per_window: int = 5):
        self.window_seconds = window_seconds
        self.max_per_window = max_per_window
        self.alert_history = defaultdict(list)
        self._lock = Lock()

    def should_allow(self, alert_type: str) -> bool:
        """
        Returns True if the alert should be emitted, False if it should be suppressed.
        """
        now = time.time()
        with self._lock:
            # Clean up old entries
            self.alert_history[alert_type] = [
                t for t in self.alert_history[alert_type] 
                if now - t < self.window_seconds
            ]
            
            if len(self.alert_history[alert_type]) < self.max_per_window:
                self.alert_history[alert_type].append(now)
                return True
                
            return False
