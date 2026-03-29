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
        import logging
        
        if action == "verify_file":
            filepath = parameters.get("filepath")
            if not filepath:
                return TachyonResult.failure("filepath required")
            
            # Ensure absolute path for deterministic verification
            abs_path = os.path.abspath(filepath)
            try:
                is_valid = self.integrity_manager.verify_integrity(abs_path)
                if is_valid:
                    return TachyonResult.success({"is_valid": True, "filepath": abs_path})
                else:
                    # Case 1: File exists but hash/signature mismatch (DENIED)
                    return TachyonResult.failure(f"Integrity violation: {abs_path}", status=TachyonStatus.DENIED, data={"is_valid": False})
            except Exception as e:
                # Case 2: Verification system failure (ERROR)
                # Fail-closed: system failure must STILL block, but is logged as an internal ERROR.
                logging.error(f"[Guardian] Verification System Error for {abs_path}: {e}")
                return TachyonResult.failure(
                    error=f"Verification System Error: {str(e)}",
                    status=TachyonStatus.ERROR,
                    data={"is_valid": False, "system_failure": True, "filepath": abs_path}
                )
        
        if action == "verify_substrate":
            # Full substrate sweep using git ls-files
            import subprocess
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            try:
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
                    if relative_path.endswith(".sig"): continue
                    if any(x in relative_path for x in ["logs/", "tmp/", ".agent/", ".gemini/", "umbra/"]):
                        continue
                        
                    full_path = os.path.join(root_dir, relative_path)
                    if not os.path.exists(full_path):
                        continue
                        
                    if not self.im.verify_integrity(full_path):
                        violations.append(relative_path)
                
                if violations:
                    msg = f"INTEGRITY FAILURE: Unsigned or tampered files detected: {', '.join(violations[:5])}"
                    if len(violations) > 5:
                        msg += f" (and {len(violations) - 5} more)"
                    
                    # TT-2026-001 FIX: No Mutant Lock suppression. Always alert, always deny.
                    try:
                        from tachyon.core.state import StateManager
                        StateManager().emit_alert("STATE_COMPROMISED", msg)
                    except Exception as alert_err:
                        logging.critical(f"[Guardian] ALERT DELIVERY FAILED during substrate sweep: {alert_err}")
                    
                    return TachyonResult.failure(msg, status=TachyonStatus.FATAL, data={"violations": violations})
                
                return TachyonResult.success({"checked_count": len(tracked_files)})
            except Exception as e:
                logging.error(f"[Guardian] Failed full substrate sweep: {e}")
                try:
                    from tachyon.core.state import StateManager
                    StateManager().emit_alert("GUARDIAN_ERROR", f"Failed full substrate sweep: {str(e)}")
                except Exception:
                    logging.critical(f"[Guardian] ALERT DELIVERY FAILED for substrate sweep error: {e}")
                return TachyonResult.failure(str(e))
        
        return TachyonResult.failure(f"Unknown action: {action}", status=TachyonStatus.NOT_IMPLEMENTED)
