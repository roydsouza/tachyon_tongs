import os
import subprocess
import json
import httpx # For Airlock API calls
from tachyon.core.state_manager import StateManager

from tachyon.agents.roles import EngineerRole

class AutoPatcher:
    """
    The surgical limb of the Tachyon Tongs organism.
    Refactored to delegate to the Unified Substrate (EngineerRole).
    """

    def __init__(self, max_retries=3):
        self.role = EngineerRole("legacy-engineer")

    def apply_and_test(self, patch_files: list, test_file_path: str, test_content: str, cve_id: str):
        """Delegates to the modular EngineerRole."""
        result = self.role.handle_action("apply_and_test", {
            "patch_files": patch_files,
            "test_path": test_file_path,
            "test_code": test_content,
            "cve_id": cve_id
        })
        return result.get("result", result)

def engineer_action_node(state: dict) -> dict:
    """Legacy pipeline node for the triad supervisor."""
    patcher = AutoPatcher()
    
    # Map CVE ID from analysis if not top-level
    cve_id = state.get("cve_id") or state.get("analysis", {}).get("id", "manual-patch")
    
    result = patcher.apply_and_test(
        patch_files=state.get("proposed_patches", []),
        test_file_path=state.get("test_path", "tests/integration/test_patch.py"),
        test_content=state.get("test_code", ""),
        cve_id=cve_id
    )
    state["final_output"] = result
    if "analysis" in state and "threats_found" in state["analysis"]:
        state["threats_found"] = state["analysis"]["threats_found"]
    return state
