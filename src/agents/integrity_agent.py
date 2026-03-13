"""
Tachyon Tongs: Integrity Agent (Supply Chain Defense)
Pillar 5: Auditing library and module provenance.
"""
from typing import Dict, Any, List

class IntegrityAgent:
    """
    The Integrity Agent intercepts requests for external code (pip installs, imports).
    It verifies them against known vulnerability databases and trusted registries.
    """

    def __init__(self, state_manager=None):
        from src.state_manager import StateManager
        self.state_manager = state_manager or StateManager()

    def audit_install_request(self, package_spec: str) -> Dict[str, Any]:
        """
        Audits a 'pip install' or dependency requirement.
        - Checks for 'Hallucination Squatting' (unknown packages).
        - Scans for known vulnerabilities (pip-audit).
        """
        # 1. Deterministic Capability Binding Check
        # If the package isn't in a 'trusted_registry' or 'SKILL.md', we block by default.
        if not self.state_manager.is_package_whitelisted(package_spec):
            return {
                "status": "REJECTED",
                "reason": f"Package '{package_spec}' is not in the trusted registry. Possible Hallucination Squatting detected."
            }

        # 2. Vulnerability Scan (Mocking pip-audit/safety for now)
        vulnerabilities = self._scan_package(package_spec)
        if vulnerabilities.get("vulnerabilities"):
            return {
                "status": "REJECTED",
                "reason": "Critical vulnerability found in package upstream.",
                "vulnerabilities": vulnerabilities["vulnerabilities"]
            }

        return {"status": "APPROVED", "package": package_spec}

    def _scan_package(self, package_spec: str) -> Dict[str, List[str]]:
        """
        Internal wrapper for pip-audit / safety APIs.
        """
        # In a real implementation: Subprocess call to 'pip-audit --json'
        return {"vulnerabilities": []}

def integrity_audit_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    ADK Graph Node for Supply Chain Integrity.
    """
    agent = IntegrityAgent()
    
    # Check for library requests in the state
    if "requested_dependencies" in state:
        results = []
        for dep in state["requested_dependencies"]:
            results.append(agent.audit_install_request(dep))
        state["integrity_audit_results"] = results
        
    return state
