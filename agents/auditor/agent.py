import os
import json
import asyncio
from typing import Dict, Any, List
from agents._core.base import BaseAgentPlugin
from agents._core.registry import AgentRegistry
from tachyon.core.supply_chain import SupplyChainOracle
from tachyon.core.state import StateManager
from tachyon.core.signing import IntegrityManager

@AgentRegistry.register("auditor")
class AuditorPlugin(BaseAgentPlugin):
    """
    Quarantine Auditor (v2):
    Performs high-assurance scans of Airlock artifacts and verified package provenance.
    """
    def __init__(self, agent_id: str, plugin_name: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, plugin_name, config or {})
        # Use the same integrity manager for Oracle and State operations
        self.oracle = SupplyChainOracle(integrity_manager=self.im)
        self.state = StateManager()
        self.state.integrity = self.im

    def execute_action(self, action: str, parameters: Dict[str, Any] = None) -> TachyonResult:
        from tachyon.core.results import TachyonResult, TachyonStatus
        if action == "audit_supply_chain":
            res = self.audit_supply_chain()
            return TachyonResult.success(res)
        elif action == "audit_quarantine":
            res = self.audit_quarantine()
            return TachyonResult.success(res)
        else:
            return TachyonResult.failure(f"Action '{action}' not recognized by Auditor.", status=TachyonStatus.NOT_IMPLEMENTED)

    def get_capabilities(self) -> List[str]:
        return ["audit_supply_chain", "audit_quarantine"]

    def audit_supply_chain(self) -> Dict[str, Any]:
        """Scans the database for all attestations and verifies their integrity."""
        self.bus.emit_event("AUDIT_STARTED", self.agent_id, {"scope": "supply_chain"}, certificate=self.certificate)
        
        results = []
        import sqlite3
        with sqlite3.connect(self.state.db_path) as conn:
            cursor = conn.execute("SELECT package_name FROM package_attestations")
            packages = [row[0] for row in cursor.fetchall()]
            
        for pkg in packages:
            is_valid = self.oracle.verify_provenance(pkg)
            results.append({
                "package": pkg,
                "status": "VERIFIED" if is_valid else "COMPROMISED"
            })
            if not is_valid:
                self.state.emit_alert("AUDIT_FAILURE", f"Package {pkg} has an invalid SLSA attestation!")

        self.bus.emit_event("AUDIT_COMPLETED", self.agent_id, {"total": len(results)}, certificate=self.certificate)
        return {"status": "SUCCESS", "results": results}

    def audit_quarantine(self) -> Dict[str, Any]:
        """Scans the 'quarantine/' directory for un-attested or tampered artifacts."""
        self.bus.emit_event("AUDIT_STARTED", self.agent_id, {"scope": "quarantine"}, certificate=self.certificate)
        
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        quarantine_dir = os.path.join(root_dir, "quarantine")
        if not os.path.exists(quarantine_dir):
            return {"status": "SUCCESS", "message": "Quarantine directory empty."}
            
        violations = []
        for root, _, files in os.walk(quarantine_dir):
            for f in files:
                # Support both V1 (.sig) and V2 (.sig.json) signature formats
                if f.endswith(".sig") or f.endswith(".sig.json"): 
                    continue
                fpath = os.path.join(root, f)
                
                # Verify signature using the agent's pre-configured integrity manager
                try:
                    is_valid = self.im.verify_integrity(fpath)
                    if not is_valid:
                        violations.append({"file": f, "reason": "INTEGRITY_FAILURE", "detail": "Verification returned False"})
                except Exception as e:
                    violations.append({"file": f, "reason": "INTEGRITY_FAILURE", "detail": str(e)})

        if violations:
            self.state.emit_alert("QUARANTINE_VIOLATION", f"Found {len(violations)} insecure artifacts in quarantine.")
            
        self.bus.emit_event("AUDIT_COMPLETED", self.agent_id, {"violations": len(violations)}, certificate=self.certificate)
        return {"status": "SUCCESS", "violations": violations}
