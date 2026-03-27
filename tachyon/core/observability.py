import time
import os
import json
import logging
from typing import Dict, Any, Optional

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger("tachyon.core.observability")

class LogContext:
    """Structured, correlation-aware logging context for Tachyon agents."""
    def __init__(self, agent_id: str, correlation_id: Optional[str] = None):
        self.agent_id = agent_id
        self.correlation_id = correlation_id or f"corr_{int(time.time())}"
        
    def info(self, event: str, **kwargs):
        self._log(logging.INFO, event, **kwargs)
        
    def warn(self, event: str, **kwargs):
        self._log(logging.WARNING, event, **kwargs)
        
    def error(self, event: str, **kwargs):
        self._log(logging.ERROR, event, **kwargs)
        
    def _log(self, level: int, event: str, **kwargs):
        payload = {
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "correlation_id": self.correlation_id,
            "event": event,
            **kwargs
        }
        # In a real system, this would go to a structured logger (e.g. structlog)
        # For the substrate, we emit to standard logger for ingestion by collectors
        logger.log(level, json.dumps(payload))

class AdaptiveTimeout:
    """Calculates security-related timeouts based on system load (L-03)."""
    @staticmethod
    def get_timeout(base_ms: float, multiplier: float = 1.0) -> float:
        """Returns a timeout in seconds, scaled by CPU load."""
        load = 10.0 # Baseline if psutil missing
        if psutil:
            load = psutil.cpu_percent(interval=None) or 10.0
            
        # Scale timeout: 1x at 10% load, up to 5x at 95% load
        scaling_factor = 1.0 + (max(0, load - 10) / 20.0) # Linearly scale
        return (base_ms * scaling_factor * multiplier) / 1000.0

def measure_latency(func):
    """Decorator to measure and log function latency (L-04)."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        latency_ms = (end - start) * 1000.0
        
        # Emit to TelemetryBus if possible (simplified here)
        from tachyon.core.state import StateManager
        state = StateManager()
        state.log_evolution("METRIC", f"Latency: {func.__name__} took {latency_ms:.2f}ms")
        
        return result
    return wrapper
