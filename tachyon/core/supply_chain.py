import json
import os
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from tachyon.core.state import StateManager
from tachyon.core.signing import IntegrityManager

class SupplyChainOracle:
    """
    Supply-Chain Oracle (Phase 25.1 Graduation):
    Enforces SLSA Level 3 attestations for all substrate imports.
    Binds package provenance to the Hybrid Root.
    """
    def __init__(self):
        self.state = StateManager()
        self.integrity = IntegrityManager()

    def attest_package(self, package_name: str, provenance: Dict[str, Any], signature: str) -> bool:
        """
        Records a signed SLSA attestation for a package.
        """
        # 1. Verify the signature against the Root Key
        # In SLSA L3, the attestation itself should be signed by a trusted build authority or the Root.
        # For simplicity in this graduation, we assume the Root signs the attestation.
        
        provenance_str = json.dumps(provenance, sort_keys=True)
        if not self.integrity.verify_text_signature(provenance_str, signature):
             print(f"[SupplyChainOracle] ERROR: Invalid attestation signature for {package_name}")
             return False
             
        # 2. Persist to StateManager
        with self.state._lock:
            import sqlite3
            with sqlite3.connect(self.state.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO package_attestations (package_name, attestation_type, provenance_json, signature, verified_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (package_name, "SLSA_V1", provenance_str, signature, datetime.now().isoformat()))
                conn.commit()
        
        print(f"[SupplyChainOracle] Attestation verified and anchored: {package_name}")
        return True

    def verify_provenance(self, package_name: str) -> bool:
        """
        High-Assurance check for SLSA L3 provenance.
        Returns True if a valid, verified attestation exists.
        """
        import sqlite3
        with sqlite3.connect(self.state.db_path) as conn:
            cursor = conn.execute("SELECT provenance_json, signature FROM package_attestations WHERE package_name = ?", (package_name,))
            row = cursor.fetchone()
            if not row:
                return False
            
            provenance_json, signature = row
            # Re-verify the signature in real-time
            return self.integrity.verify_text_signature(provenance_json, signature)

    def is_import_allowed(self, package_name: str) -> bool:
        """
        Unified gate for substrate imports.
        Enforces: Whitelist (L1) AND SLSA L3 (L2).
        """
        if not self.state.is_package_whitelisted(package_name):
             return False
        
        # For Phase 38, we require SLSA L3 for all non-standard library packages
        import sys
        if package_name in sys.builtin_module_names:
            return True
            
        return self.verify_provenance(package_name)
