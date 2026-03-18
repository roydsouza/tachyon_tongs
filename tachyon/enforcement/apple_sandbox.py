import subprocess
import os
import tempfile
import ast
from typing import Dict, Any, List, Tuple

class StaticAnalyzer:
    """
    Tachyon Tongs: Pre-Execution Static Analysis
    Detects dangerous Python patterns before they enter the sandbox.
    """
    DANGEROUS_FUNCTIONS = {"os.system", "subprocess.Popen", "eval", "exec", "pickle.load", "marshal.load"}
    
    @classmethod
    def scan_file(cls, filepath: str) -> Tuple[bool, str]:
        """Returns (is_safe, reason)."""
        if not os.path.exists(filepath):
            return True, "File not found"
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                # Check for direct attribute calls like os.system()
                if isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name):
                            func_name = f"{node.func.value.id}.{node.func.attr}"
                    elif isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        
                    if func_name in cls.DANGEROUS_FUNCTIONS:
                        return False, f"Dangerous function detected: {func_name}"
                        
            return True, "Safe"
        except Exception as e:
            return True, f"Scan skipped: {str(e)}"

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
        # --- Pre-Execution Supply Chain & Static Analysis Gating ---
        for arg in command:
            if arg.endswith('.py') and os.path.exists(arg):
                # 1. Dependency Scan
                if not DependencyScanner.scan_file(arg):
                    return {
                        "status": "BLOCKED",
                        "error": f"Supply Chain Attack Prevented: {arg} contains known poisoned dependencies.",
                        "exit_code": -3
                    }
                
                # 2. Static Analysis Scan
                is_safe, reason = StaticAnalyzer.scan_file(arg)
                if not is_safe:
                    return {
                        "status": "BLOCKED",
                        "error": f"Static Analysis Violation: {reason}",
                        "exit_code": -5
                    }
        
        # Hallucination Squatting / Malicious Package Audit
        if command and command[0] == "pip" and "install" in command:
            from tachyon.agents.legacy.integrity_agent import IntegrityAgent
            agent = IntegrityAgent()
            # Extract package names (basic heuristic: everything after 'install' that doesn't start with '-')
            try:
                install_idx = command.index("install")
                packages = [pkg for pkg in command[install_idx+1:] if not pkg.startswith("-")]
                for pkg in packages:
                    verdict = agent.audit_install_request(pkg)
                    if verdict["status"] == "REJECTED":
                        return {
                            "status": "BLOCKED",
                            "error": f"Integrity Violation: {verdict['reason']}",
                            "exit_code": -4
                        }
            except ValueError:
                pass
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
