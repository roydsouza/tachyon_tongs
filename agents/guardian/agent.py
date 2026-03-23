import os
from typing import Dict, Any
from agents._core.base import BaseAgentPlugin
from agents._core.registry import AgentRegistry
from tachyon.core.signing import IntegrityManager

@AgentRegistry.register("guardian")
class GuardianPlugin(BaseAgentPlugin):
    """
    Guardian Plugin: Specialized in substrate integrity.
    """
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "Guardian", config)
        self.integrity_manager = IntegrityManager()
        self.im = self.integrity_manager # Phase 33 compatibility alias

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "verify_file":
            filepath = parameters.get("filepath")
            if not filepath:
                return {"status": "ERROR", "message": "filepath required"}
            
            # Ensure absolute path for deterministic verification
            abs_path = os.path.abspath(filepath)
            is_valid = self.integrity_manager.verify_integrity(abs_path)
            
            # Mutant Lock Bypass: Check if mutation is authorized
            from tachyon.core.state import StateManager
            state = StateManager()
            is_authorized = state.is_mutant_lock_active()
            
            if not is_valid and is_authorized:
                # Downgrade to informational warning instead of failure
                return {
                    "status": "WARNING",
                    "is_valid": False,
                    "authorized_mutation": True,
                    "filepath": abs_path,
                    "message": "Integrity mismatch detected, but authorized Mutant Lock is active. Suppression engaged."
                }

            return {
                "status": "SUCCESS" if is_valid else "FAILURE",
                "is_valid": is_valid,
                "filepath": abs_path
            }
        
        if action == "verify_substrate":
            # Phase 30: Full substrate sweep using git ls-files
            import subprocess
            # Correct path traversal from agents/code-only/guardian/agent.py to root
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            try:
                # Get list of all tracked files
                result = subprocess.run(
                    ["git", "ls-files"], 
                    cwd=root_dir, 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                tracked_files = result.stdout.splitlines()
                
                violations = []
                for relative_path in tracked_files:
                    # Skip .sig files themselves and ignored/system dirs
                    if relative_path.endswith(".sig"): continue
                    if any(x in relative_path for x in ["logs/", "tmp/", ".agent/", ".gemini/", "umbra/"]):
                        continue
                        
                    full_path = os.path.join(root_dir, relative_path)
                    if not self.im.verify_integrity(full_path):
                        print(f"[Guardian Debug] Integrity Violation Found: {relative_path}")
                        violations.append(relative_path)
                
                if violations:
                    msg = f"INTEGRITY FAILURE: Unsigned or tampered files detected: {', '.join(violations[:5])}"
                    print(f"[Guardian Debug] Emitting Alert: {msg}")
                    if len(violations) > 5:
                        msg += f" (and {len(violations) - 5} more)"
                    # Note: StateManager is already imported in verify_file logic above if needed, 
                    # but I'll use direct import here for clarity.
                    from tachyon.core.state import StateManager
                    StateManager().emit_alert("STATE_COMPROMISED", msg)
                    return {"status": "FAILURE", "violations": violations}
                
                return {"status": "SUCCESS", "checked_count": len(tracked_files)}
            except Exception as e:
                from tachyon.core.state import StateManager
                StateManager().emit_alert("GUARDIAN_ERROR", f"Failed full substrate sweep: {str(e)}")
                return {"status": "ERROR", "message": str(e)}
        
        return {"status": "ERROR", "message": f"Unknown action: {action}"}
