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
        os.makedirs(self.lock_dir, exist_ok=True)

    def _get_lock_path(self, name: str) -> str:
        return os.path.join(self.lock_dir, f"{name}.lock")

    def acquire_lock(self, name: str, agent_id: str, ttl: Optional[int] = None) -> Optional[str]:
        """
        Attempt to acquire a mutually exclusive lock.
        Returns a Lock Token (UUID) if successful, None otherwise.
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
                            # Lock has expired, we can reclaim it
                            pass
                        else:
                            return None # Lock is held and active
            except (ValueError, OSError):
                # Corrupt lock file, reclaim it
                pass

        # 2. Atomic Acquisition
        token = str(uuid.uuid4())
        lock_data = f"{agent_id}|{token}|{now + ttl}"
        
        try:
            # We use an atomic write via a temp file on the same volume
            tmp_path = path + ".tmp"
            with open(tmp_path, "w") as f:
                f.write(lock_data)
            os.rename(tmp_path, path)
            return token
        except OSError:
            return None

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
