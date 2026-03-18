import pytest
import os
import sqlite3
from tachyon.core.state import StateManager

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_state.db"
    return str(db_file)

def test_state_manager_integrity_gate(temp_db):
    """Verify that StateManager detects out-of-band catalog tampering."""
    # 1. Initialize StateManager (creates catalog and .sig)
    sm = StateManager(db_path=temp_db)
    catalog_path = "EXPLOITATION_CATALOG.md"
    
    # Ensure it's signed
    sm.export_catalog(catalog_file=catalog_path)
    assert os.path.exists(f"{catalog_path}.sig")
    
    # 2. Tamper with the catalog
    with open(catalog_path, "a") as f:
        f.write("\nTAMPERED_ENTRY: CVE-2026-FAKE\n")
        
    # 3. Reload StateManager or trigger verification
    # StateManager verifies on boot (new instance)
    StateManager._instance = None # Force re-init singleton
    
    with pytest.raises(RuntimeError) as excinfo:
        os.environ["TACHYON_STRICT_MODE"] = "True"
        os.environ["TACHYON_SECRET_KEY"] = "test-secret"
        StateManager(db_path=temp_db)
    
    assert "INTEGRITY COMPROMISED" in str(excinfo.value)
    
    # Cleanup
    if os.path.exists(catalog_path): os.remove(catalog_path)
    if os.path.exists(f"{catalog_path}.sig"): os.remove(f"{catalog_path}.sig")
