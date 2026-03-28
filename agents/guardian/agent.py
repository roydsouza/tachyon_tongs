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
        self.integrity_manager = self.im

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> TachyonResult:
        from tachyon.core.results import TachyonResult, TachyonStatus
        
        if action == "verify_file":
            filepath = parameters.get("filepath")
            if not filepath:
                return TachyonResult.failure("filepath required")
            
            # Ensure absolute path for deterministic verification
            abs_path = os.path.abspath(filepath)
            try:
                is_valid = self.integrity_manager.verify_integrity(abs_path)
            except Exception as e:
                # TD-02: Map exception to TachyonResult(status=DENIED)
                return TachyonResult(
                    status=TachyonStatus.DENIED,
                    error=f"Integrity Violation: {str(e)}",
                    data={"is_valid": False, "filepath": abs_path}
                )
            
            # Mutant Lock Bypass: Check if mutation is authorized
            from tachyon.core.state import StateManager
            state = StateManager()
            is_authorized = state.is_mutant_lock_active()
            
            if not is_valid and is_authorized:
                # Downgrade to informational warning instead of failure
                return TachyonResult(
                    status=TachyonStatus.SUCCESS, # Authorized error is still a success for the agent
                    error="Integrity mismatch detected, but authorized Mutant Lock is active. Suppression engaged.",
                    data={"is_valid": False, "authorized_mutation": True, "filepath": abs_path}
                )

            if is_valid:
                return TachyonResult.success({"is_valid": True, "filepath": abs_path})
            else:
                return TachyonResult.failure(f"Integrity violation: {abs_path}", status=TachyonStatus.DENIED)
        
        if action == "verify_substrate":
            # Phase 30: Full substrate sweep using git ls-files
            import subprocess
            # Correct path traversal from agents/code-only/guardian/agent.py to root
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
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
                    if not os.path.exists(full_path):
                        continue
                        
                    if not self.im.verify_integrity(full_path):
                        print(f"[Guardian Debug] Integrity Violation Found: {relative_path}")
                        violations.append(relative_path)
                
                if violations:
                    msg = f"INTEGRITY FAILURE: Unsigned or tampered files detected: {', '.join(violations[:5])}"
                    print(f"[Guardian Debug] Emitting Alert: {msg}")
                    
                    from tachyon.core.state import StateManager
                    state = StateManager()
                    
                    if state.is_mutant_lock_active():
                        print("[Guardian Debug] Authorized mutation in progress. Suppressing alert.")
                        return TachyonResult(
                            status=TachyonStatus.ERROR,
                            error="Integrity violations detected, but authorized Mutant Lock is active. Suppression engaged.",
                            data={"violations": violations, "authorized_mutation": True}
                        )
                    
                    if len(violations) > 5:
                        msg += f" (and {len(violations) - 5} more)"
                        
                    state.emit_alert("STATE_COMPROMISED", msg)
                    return TachyonResult.failure(msg, status=TachyonStatus.FATAL, data={"violations": violations})
                
                return TachyonResult.success({"checked_count": len(tracked_files)})
            except Exception as e:
                from tachyon.core.state import StateManager
                StateManager().emit_alert("GUARDIAN_ERROR", f"Failed full substrate sweep: {str(e)}")
                return TachyonResult.failure(str(e))
        
        return TachyonResult.failure(f"Unknown action: {action}", status=TachyonStatus.NOT_IMPLEMENTED)
