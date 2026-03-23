import os
from typing import Dict, Any, Optional

class Healer:
    """
    Autonomic Self-Healing Engine for Tachyon Tongs.
    Attempts to repair known failure patterns detected by the Herald.
    """
    def __init__(self):
        self.recovery_patterns = {
            r"No such file or directory: '(.*?)'": self._fix_missing_path,
            r"Permission denied: '(.*?)'": self._fix_permissions
        }

    def attempt_repair(self, failure_msg: str) -> Optional[str]:
        """Try to fix the problem and return a resolution message if successful."""
        import re
        for pattern, handler in self.recovery_patterns.items():
            match = re.search(pattern, failure_msg)
            if match:
                path = match.group(1)
                return handler(path)
        return None

    def _fix_missing_path(self, path: str) -> Optional[str]:
        try:
            # If it's a file ending in .md, try creating parent dirs and empty file
            if path.endswith(".md"):
                parent = os.path.dirname(path)
                if parent and not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)
                if not os.path.exists(path):
                    with open(path, "w") as f:
                        f.write(f"# [RECOVERED] {os.path.basename(path)}\n\nAutomated recovery by Herald.")
                return f"Successfully recreated missing path: {path}"
            
            # If it's a directory
            elif not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                return f"Successfully recreated missing directory: {path}"
        except Exception as e:
            return f"Healer failed to fix path {path}: {str(e)}"
        return None

    def _fix_permissions(self, path: str) -> Optional[str]:
        try:
            if os.path.exists(path):
                import stat
                os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE | stat.S_IREAD)
                return f"Restored read/write permissions for {path}"
        except Exception as e:
            return f"Healer failed to fix permissions for {path}: {str(e)}"
        return None
