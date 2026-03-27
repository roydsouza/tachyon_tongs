import pytest
import os
import json
from tachyon.core.supply_chain import SupplyChainOracle
from tachyon.core.state import StateManager
from tachyon.core.signing import IntegrityManager

@pytest.fixture
def oracle():
    os.environ["TACHYON_TEST_MODE"] = "1"
    # Ensure a fresh DB for each test
    db_path = "tests/tmp/test_supply_chain.db"
    if os.path.exists(db_path): os.remove(db_path)
    
    # Initialize StateManager with test DB, forcing reset for test
    StateManager._instance = None
    state = StateManager(db_path=db_path)
    return SupplyChainOracle()

def test_slsa_attestation_roundtrip(oracle):
    package_name = "test-pkg-v1"
    provenance = {
        "builder": "tachyon-root-build",
        "recipe": "secure-import",
        "digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    
    # 1. Sign the provenance
    provenance_str = json.dumps(provenance, sort_keys=True)
    signature = oracle.integrity.sign_text(provenance_str)
    
    # 2. Attest
    assert oracle.attest_package(package_name, provenance, signature) == True
    
    # 3. Verify
    assert oracle.verify_provenance(package_name) == True
    
    # 4. Tamper
    with oracle.state._lock:
        import sqlite3
        with sqlite3.connect(oracle.state.db_path) as conn:
            conn.execute("UPDATE package_attestations SET provenance_json = ? WHERE package_name = ?", 
                         (provenance_str.replace("secure-import", "malicious-import"), package_name))
            conn.commit()
            
    assert oracle.verify_provenance(package_name) == False

def test_import_enforcement(oracle):
    package_name = "secret-module"
    
    # 1. Not whitelisted
    assert oracle.is_import_allowed(package_name) == False
    
    # 2. Whitelisted but no attestation
    oracle.state.sync_whitelist_from_manifest() # Mock whitelist
    with oracle.state._lock:
        import sqlite3
        with sqlite3.connect(oracle.state.db_path) as conn:
            conn.execute("INSERT INTO package_whitelist (package_name) VALUES (?)", (package_name,))
            conn.commit()
            
    assert oracle.is_import_allowed(package_name) == False
    
    # 3. Whitelisted + Attestation
    provenance = {"auth": "root"}
    provenance_str = json.dumps(provenance, sort_keys=True)
    signature = oracle.integrity.sign_text(provenance_str)
    oracle.attest_package(package_name, provenance, signature)
    
    assert oracle.is_import_allowed(package_name) == True
