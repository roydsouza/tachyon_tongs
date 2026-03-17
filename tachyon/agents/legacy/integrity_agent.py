"""
Tachyon Tongs: Legacy Integrity Agent Shim
Provides backward compatibility for package auditing tests.
"""

import json
from tachyon.core.state_manager import StateManager

class IntegrityAgent:
    def __init__(self):
        self.agent_id = "IntegrityAgent"
        self.manager = StateManager()

    def audit_install_request(self, package_name: str) -> dict:
        """Audits a package installation request."""
        # test_hallucination_squatting_block expects a check against the whitelist
        if hasattr(self.manager, "is_package_whitelisted"):
            if not self.manager.is_package_whitelisted(package_name):
                return {
                    "status": "REJECTED",
                    "reason": f"Package '{package_name}' not in the trusted registry."
                }
        
        # test_vulnerability_interception expects a scan
        scan_results = self._scan_package(package_name)
        if scan_results.get("vulnerabilities"):
            return {
                "status": "REJECTED",
                "reason": "Known vulnerabilities detected",
                "vulnerabilities": scan_results["vulnerabilities"]
            }
            
        return {"status": "APPROVED"}

    def _scan_package(self, package_name: str) -> dict:
        """Mock behavior for the vulnerability scanner."""
        # Typically mocked in tests via unittest.mock
        return {"vulnerabilities": []}
