import subprocess
import os
import tempfile
import ast
from typing import Dict, Any, List

class DependencyScanner:
    """
    Simulates the Protect AI LLM Guard supply chain scanner.
    Parses the AST of Python scripts to prevent execution of known malware/typosquat packages.
    """
    POISONED_LIBRARIES = {
        "requestz", "urllib5", "colorama-backdoor", 
        "discord-webhook-stealer", "browser-cookie3", "malicious_crypto_miner"
    }
    
    @classmethod
    def scan_file(cls, filepath: str) -> bool:
        """Returns True if safe, False if a poisoned dependency is found."""
        if not os.path.exists(filepath):
            return True
        try:
            with open(filepath, 'r') as f:
                tree = ast.parse(f.read(), filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in cls.POISONED_LIBRARIES:
                            return False
                elif isinstance(node, ast.ImportFrom):
                    if node.module in cls.POISONED_LIBRARIES:
                        return False
        except Exception:
            pass # If it's not valid python, we ignore it for dependency scanning
        return True

class AppleSandbox:
    """
    Tier 0 computational isolation layer using macOS 'sandbox-exec' (Seatbelt).
    Provides millisecond-latency sandboxing for low-risk, compute-only agent tasks.
    """
    
    # Profile that denies network and limits writes to a specific workspace directory.
    # Note: Allows reading globally (like libraries/Python) to allow commands to start.
    COMPUTE_ONLY_PROFILE = """
    (version 1)
    (deny default)
    (allow process-exec)
    (allow process-fork)
    (allow sysctl-read)
    (allow file-read*)
    (deny network*)
    (allow file-write* (subpath "{workspace_dir}"))
    (allow file-write* (subpath "/dev/null"))
    """
    
    def __init__(self, workspace_dir: str = "/tmp/tachyon_tier0"):
        self.workspace_dir = os.path.realpath(workspace_dir)
        os.makedirs(self.workspace_dir, exist_ok=True)
        
    def execute(self, command: List[str], profile_template: str = COMPUTE_ONLY_PROFILE) -> Dict[str, Any]:
        """
        Executes a command inside the macOS Seatbelt sandbox.
        """
        # --- Pre-Execution Supply Chain Gating ---
        for arg in command:
            if arg.endswith('.py') and os.path.exists(arg):
                is_safe = DependencyScanner.scan_file(arg)
                if not is_safe:
                    return {
                        "status": "BLOCKED",
                        "error": f"Supply Chain Attack Prevented: {arg} contains known poisoned dependencies.",
                        "exit_code": -3
                    }
        # ------------------------------------------

        profile = profile_template.replace("{workspace_dir}", self.workspace_dir)
        
        # Write the profile to a temporary file
        fd, profile_path = tempfile.mkstemp(suffix=".sb", text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(profile)
                
            sandbox_cmd = ["sandbox-exec", "-f", profile_path] + command
            
            # Execute process safely
            result = subprocess.run(
                sandbox_cmd,
                capture_output=True,
                text=True,
                timeout=30,  # Prevent runaway infinite loops
                cwd=self.workspace_dir
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Execution exceeded limits.",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "status": "exception",
                "error": str(e),
                "exit_code": -2
            }
        finally:
            if os.path.exists(profile_path):
                os.remove(profile_path)
