import pytest
import os
import shutil
from agents.auditor.agent import AuditorPlugin
from tachyon.core.state import StateManager

@pytest.fixture
def auditor():
    os.environ["TACHYON_TEST_MODE"] = "1"
    # Reset StateManager instance for clean DB
    StateManager._instance = None
    state = StateManager(db_path="tests/tmp/test_auditor.db")
    return AuditorPlugin(agent_id="test-auditor", plugin_name="Auditor", config={})

@pytest.mark.asyncio
async def test_audit_supply_chain_integrity(auditor):
    # 1. Add a valid attestation
    package_name = "test-pkg"
    provenance = {"auth": "root"}
    import json
    provenance_str = json.dumps(provenance, sort_keys=True)
    signature = auditor.state.integrity.sign_text(provenance_str)
    auditor.oracle.attest_package(package_name, provenance, signature)
    
    # 2. Run audit
    res = await auditor.audit_supply_chain()
    assert res["status"] == "SUCCESS"
    assert any(r["package"] == package_name and r["status"] == "VERIFIED" for r in res["results"])

@pytest.mark.asyncio
async def test_audit_quarantine_violations(auditor):
    # 1. Setup quarantine dir
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    quarantine_dir = os.path.join(root_dir, "quarantine")
    if not os.path.exists(quarantine_dir): os.makedirs(quarantine_dir)
    
    # Clean it
    for f in os.listdir(quarantine_dir):
        os.remove(os.path.join(quarantine_dir, f))
        
    # 2. Create insecure file
    bad_file = os.path.join(quarantine_dir, "malicious.py")
    with open(bad_file, "w") as f: f.write("print('bad')")
    
    # 3. Create secure file
    good_file = os.path.join(quarantine_dir, "secure.py")
    with open(good_file, "w") as f: f.write("print('good')")
    auditor.state.integrity.sign_document(good_file)
    
    # 4. Run audit
    res = await auditor.audit_quarantine()
    assert res["status"] == "SUCCESS"
    violations = [v["file"] for v in res["violations"]]
    assert "malicious.py" in violations
    assert "secure.py" not in violations
    
    # Cleanup
    shutil.rmtree(quarantine_dir)
