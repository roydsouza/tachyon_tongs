import pytest
import os
import hmac
import hashlib
from tachyon.core.state_manager import StateManager

@pytest.fixture
def clean_state():
    db_path = "/tmp/test_integrity.db"
    catalog_path = "/tmp/EXPLOITATION_CATALOG_TEST.md"
    sig_path = catalog_path + ".sig"
    
    # Cleanup before
    for p in [db_path, catalog_path, sig_path]:
        if os.path.exists(p):
            os.remove(p)
            
    os.environ["TACHYON_DB_PATH"] = db_path
    
    # Needs to be a fresh instance
    StateManager._instance = None
    sm = StateManager()
    
    yield sm, catalog_path, sig_path
    
    # Cleanup after
    for p in [db_path, catalog_path, sig_path]:
        if os.path.exists(p):
            os.remove(p)
    StateManager._instance = None

def test_state_manager_integrity_signing(clean_state):
    sm, catalog_path, sig_path = clean_state
    
    # Insert a threat, this should trigger export and signing
    threat = {"id": "CVE-TEST-1", "description": "Test", "source": "pytest"}
    sm.log_exploitation([threat], catalog_file=catalog_path)
    
    assert os.path.exists(catalog_path)
    assert os.path.exists(sig_path)
    
    # Verify via the official IntegrityManager logic (handles Hybrid PQC)
    assert sm._verify_catalog_integrity(catalog_path) is True

def test_state_manager_tampering_detection(clean_state):
    sm, catalog_path, sig_path = clean_state
    
    # Stage a valid catalog and signature
    with open(catalog_path, "w") as f:
        f.write("# Valid Catalog")
    sm._sign_document(catalog_path)
    
    # Verify it passes initially
    sm._verify_catalog_integrity(catalog_path)
    
    # Tamper with the file
    with open(catalog_path, "a") as f:
        f.write("\nMALICIOUS ENTRY")
        
    # Verify it throws an error
    with pytest.raises(RuntimeError, match="INTEGRITY COMPROMISED"):
        sm._verify_catalog_integrity(catalog_path)
