import os
import fcntl
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class TelemetryBus:
    """
    High-Frequency Structured Event Bus for Tachyon Tongs Agents.
    Writes JSONL to memory/operational/telemetry.jsonl with flock() atomic locking
    to gracefully handle multi-agent concurrency.
    """
    _instance = None
    
    def __new__(cls, log_path=None):
        if cls._instance is None:
            cls._instance = super(TelemetryBus, cls).__new__(cls)
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            mem_dir = os.path.join(root_dir, "memory", "operational")
            os.makedirs(mem_dir, exist_ok=True)
            from tachyon.core.forensics import ForensicStore
            cls._instance.log_path = log_path or os.path.join(mem_dir, "telemetry.jsonl")
            cls._instance.forensic_store = ForensicStore()
            import threading
            cls._instance._lock = threading.Lock()
            cls._instance._log_file = None
        return cls._instance

    def _get_log_file(self):
        """Returns a persistent file handle for the telemetry log."""
        if self._log_file is None:
            self._log_file = open(self.log_path, "a", buffering=1) # Line-buffered
        return self._log_file

    def emit_event(
        self, 
        event_type: str, 
        agent_id: str, 
        action: str = "UNKNOWN",
        status: str = "INFO", 
        details: Optional[Dict[str, Any]] = None,
        source: str = "internal"
    ):
        """
        Atomically append a structured telemetry event.
        
        Args:
            event_type: Category of the event (e.g., TOOL_CALL, AGENT_SIGNATURE, HEARTBEAT)
            agent_id: The ID or Role of the agent emitting the event
            action: Specific action being taken (e.g., safe_execute, signature_generated)
            status: Status of the action (SUCCESS, BLOCKED, FAILED, INFO)
            details: Additional context (e.g., policy violation reason, tool params)
            source: Source of the event (internal or transit)
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "action": action,
            "status": status,
            "source": source,
            "details": details or {}
        }
        
        # 1. Forensic SQL Ledger (PQC-Signed)
        event_id = 0
        try:
            event_id = self.forensic_store.log_event(agent_id, event_type, action, status, details, source=source)
        except Exception as e:
            import sys
            print(f"[TelemetryBus] SQL LOG FAILURE: {e}", file=sys.stderr)

        # 2. Legacy JSONL (Atomic Append)
        event_str = json.dumps(event) + "\n"
        try:
            with self._lock:
                f = self._get_log_file()
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.write(event_str)
                    f.flush()
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            # Fallback to stderr if file IO fails to ensure blindspots are reported
            import sys
            print(f"[TelemetryBus] FAILED TO WRITE EVENT: {e} -> {event_str.strip()}", file=sys.stderr)
        
        return event_id

    def get_events_after(self, last_id: int, limit: int = 100) -> list:
        """Read events after the specified ID from the ForensicStore."""
        return self.forensic_store.query_after(last_id, limit)

    def get_events(self, limit: int = 100) -> list:
        """Read the last N events from the telemetry bus."""
        if not os.path.exists(self.log_path):
            return []
            
        events = []
        try:
            with open(self.log_path, "r") as f:
                # Naive tail implementation for JSONL
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        events.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return events
