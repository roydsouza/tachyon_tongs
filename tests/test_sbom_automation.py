import os
import json
import sqlite3
import pytest
from scripts.forensics.generate_sbom import generate_sbom
from tachyon.core.state import StateManager

def reset_state_manager():
    StateManager._instance = None

def test_sbom_generation_and_signing():
    """
    Verifies that generate_sbom() creates a valid, signed CycloneDX manifest.
    """
    reset_state_manager()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_db = os.path.join(root_dir, "tests", "tmp", "test_sbom.db")
    if os.path.exists(test_db): os.remove(test_db)
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sbom_path = os.path.join(root_dir, "forensics", "SBOM.json")
    sig_path = sbom_path + ".sig"
    
    # Cleanup previous runs
    if os.path.exists(sbom_path): os.remove(sbom_path)
    if os.path.exists(sig_path): os.remove(sig_path)

    try:
        # 1. Setup StateManager with a fake whitelist
        os.environ["TACHYON_TEST_MODE"] = "1"
        sm = StateManager(db_path=test_db)
        
        with sqlite3.connect(test_db) as conn:
            conn.execute(
                "INSERT INTO package_whitelist (package_name, version, checksum) VALUES (?, ?, ?)",
                ("requests", "2.31.0", "sha256:abcd")
            )
            conn.commit()
            
        # 2. Run SBOM Generation
        generate_sbom()
        
        # 3. Verify SBOM.json
        assert os.path.exists(sbom_path)
        with open(sbom_path, "r") as f:
            sbom = json.load(f)
            assert sbom["bomFormat"] == "CycloneDX"
            assert any(c["name"] == "requests" for c in sbom["components"])
            
        # 4. Verify Signature
        assert os.path.exists(sig_path)
        # Verify can be performed by IntegrityManager
        is_valid = sm.integrity.verify_integrity(sbom_path)
        assert is_valid is True
        
    finally:
        if os.path.exists(test_db): os.remove(test_db)
        # We leave the file if the user wants to see it, OR cleanup
        # if os.path.exists(sbom_path): os.remove(sbom_path)
