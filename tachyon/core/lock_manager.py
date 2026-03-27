import os
import uuid
import time
from typing import Optional

class MutantLockManager:
    """
    Centralized High-Assurance Lock Service.
    Implements Secure Enclave tokens and auto-expiry logic (60s).
    """
    
    def __init__(self, lock_dir: Optional[str] = None, default_ttl: int = 60):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.lock_dir = lock_dir or os.path.join(root_dir, "memory", "locks")
        self.default_ttl = default_ttl
        self._suppression_counts = {} # Simple in-memory counter for excessive alerts
        os.makedirs(self.lock_dir, exist_ok=True)

    def _get_lock_path(self, name: str) -> str:
        return os.path.join(self.lock_dir, f"{name}.lock")

    def acquire_lock(self, name: str, agent_id: str, ttl: Optional[int] = None) -> Optional[str]:
        """
        Attempt to acquire a mutually exclusive lock.
        Returns a Lock Token (UUID) if successful, None otherwise (M-01: Forensics Added).
        """
        path = self._get_lock_path(name)
        ttl = ttl or self.default_ttl
        now = time.time()
        
        # 1. Check for existing lock and handle expiry (Stale Lock Mitigation)
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = f.read().split("|")
                    if len(data) == 3:
                        expires_at = float(data[2])
                        if now > expires_at:
                            pass
                        else:
                            # M-01: Record suppressed mutation attempt
                            self._record_suppression(name, agent_id)
                            return None # Lock is held and active
            except (ValueError, OSError):
                pass

        # 2. Atomic Acquisition
        token = str(uuid.uuid4())
        lock_data = f"{agent_id}|{token}|{now + ttl}"
        
        try:
            tmp_path = path + ".tmp"
            with open(tmp_path, "w") as f:
                f.write(lock_data)
            os.rename(tmp_path, path)
            # Reset suppression count on successful lock acquisition (or just allow it to persist)
            return token
        except OSError:
            self._record_suppression(name, agent_id)
            return None

    def _record_suppression(self, lock_name: str, agent_id: str):
        """Forensic logging of suppressed security alerts (M-01)."""
        from tachyon.core.telemetry import TelemetryBus
        bus = TelemetryBus()
        
        count = self._suppression_counts.get(agent_id, 0) + 1
        self._suppression_counts[agent_id] = count
        
        # Log to the forensic channel
        bus.emit_event(
            event_type="MUTATION_SUPPRESSED",
            agent_id=agent_id,
            details={
                "lock_name": lock_name,
                "suppression_count": count,
                "timestamp": time.time()
            }
        )
        
        # Alert if we exceed the safety threshold
        if count >= 10:
            bus.emit_event(
                event_type="EXCESSIVE_MUTATION_SUPPRESSION",
                agent_id=agent_id,
                details={
                    "lock_name": lock_name,
                    "total_count": count,
                    "reason": "Mutation lock held persistently by unauthorized or deadlocked agent."
                }
            )

    def release_lock(self, name: str, token: str) -> bool:
        """
        Verified Release: Only allows the holder with the correct token to unlock.
        """
        path = self._get_lock_path(name)
        if not os.path.exists(path):
            return True
            
        try:
            with open(path, "r") as f:
                data = f.read().split("|")
                if len(data) >= 2 and data[1] == token:
                    os.remove(path)
                    return True
        except OSError:
            pass
        return False

    def is_locked(self, name: str) -> bool:
        """Check if a lock is currently active and not expired."""
        path = self._get_lock_path(name)
        if not os.path.exists(path):
            return False
            
        try:
            with open(path, "r") as f:
                data = f.read().split("|")
                if len(data) == 3:
                    return time.time() < float(data[2])
        except (ValueError, OSError):
            return False
        return False
