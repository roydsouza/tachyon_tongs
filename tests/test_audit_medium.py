import pytest
import os
import json
import time
from tachyon.core.lock_manager import MutantLockManager
from tachyon.api.pep import PEPLayer
from tachyon.api.schema import ToolRequest, SignedCommand
from tachyon.pipeline.verifier import VerifierAgent, VerificationFailedError
from tachyon.core.signing import IntegrityManager, SecurityViolationError

def test_m01_mutant_lock_forensics():
    """Verify lock suppression logging and excessive suppression alerts."""
    import shutil
    lock_dir = "/tmp/tachyon_test_locks"
    if os.path.exists(lock_dir): shutil.rmtree(lock_dir)
    os.makedirs(lock_dir)
    
    manager = MutantLockManager(lock_dir=lock_dir)
    # Acquire lock for agent A
    manager.acquire_lock("resource", "agent_a", ttl=10)
    
    # Attempt acquire for agent B (Should fail and log suppression)
    token = manager.acquire_lock("resource", "agent_b")
    assert token is None
    
    # Check suppression count
    assert manager._suppression_counts["agent_b"] == 1
    
    # Force 9 more suppressions to trigger excessive alert
    for _ in range(9):
        manager.acquire_lock("resource", "agent_b")
    
    assert manager._suppression_counts["agent_b"] == 10
    # In a real environment, we'd check the TelemetryBus, but here we check internal state
    if os.path.exists(lock_dir): shutil.rmtree(lock_dir)

@pytest.mark.asyncio
async def test_m02_pep_circuit_breaker():
    """Verify circuit opens after repeated tool failures."""
    pep = PEPLayer()
    request = ToolRequest(agent_id="SENTRY", action="SAFE_MATH", parameters={"val1": 1, "val2": 2})
    
    # Mock the wasm_runner to fail
    pep.wasm_runner.run_tool = lambda *args: exec('raise Exception("WASM CRASH")')
    
    # 1-4: Failed but circuit stays CLOSED
    for _ in range(4):
        resp = await pep.execute(request)
        assert resp.status == "FALLBACK_SUCCESS"
        
    # 5: Trigger Circuit OPEN
    resp = await pep.execute(request)
    assert resp.status == "FALLBACK_SUCCESS" # The fifth one still records failure but tries execution
    
    # 6: Circuit should now be OPEN
    resp = await pep.execute(request)
    assert resp.status == "CIRCUIT_OPEN"
    assert "is OPEN" in resp.error

def test_m03_pickle_ban():
    """Verify ToolRequest rejects pickle bytecode."""
    # Pickle protocol 4 starts with \x80\x04
    illegal_params = {"data": "\x80\x04\x95..."}
    with pytest.raises(ValueError, match="Potential Pickle payload detected"):
        ToolRequest(agent_id="TEST", action="LOG", parameters=illegal_params)

def test_m04_recursive_verifier():
    """Verify Verifier catches contamination in nested structures."""
    verifier = VerifierAgent()
    
    # Deeply nested malicious payload
    nested_output = {
        "status": "success",
        "data": {
            "metadata": {
                "script": "#!/bin/bash\nrm -rf /"
            }
        }
    }
    
    with pytest.raises(VerificationFailedError, match="data.metadata.script"):
        verifier.verify(nested_output)

def test_m05_model_router_repetition():
    """Verify ModelRouter detects repetitive token injection bypasses."""
    from tachyon.core.routing import ModelRouter
    router = ModelRouter()
    
    # Normal prompt
    assert router.detect_complexity("Design an architectural refactor for PQC.") > 0.5
    
    # Repetitive spam (unique ratio < 0.3)
    spam = "spam " * 20
    assert router.detect_complexity(spam) == 0.05

def test_m06_pathogen_sandbox():
    """Verify Pathogen agent filters malicious OS calls via static analysis."""
    from agents.pathogen.agent import PathogenPlugin
    pathogen = PathogenPlugin("PATHOGEN", {})
    
    # 1. Block os.system
    resp = pathogen.execute_action("verify_variant", {"variant": "import os; os.system('rm -rf /')"})
    assert resp["status"] == "FAILED"
    assert "Malicious system call" in resp["reason"]
    
    # 2. Block subprocess
    resp = pathogen.execute_action("verify_variant", {"variant": "import subprocess; ..."})
    assert resp["status"] == "FAILED"
    
    # 3. Allow safe logic
    resp = pathogen.execute_action("verify_variant", {"variant": "x = 1 + 2"})
    assert resp["status"] == "SUCCESS"

def test_m08_role_path_traversal():
    """Verify IntegrityManager rejects path traversal in role names."""
    im = IntegrityManager(use_hardware=False)
    
    with pytest.raises(SecurityViolationError, match="Invalid Agent Role"):
        im.load_agent_identity("../../etc/passwd")
        
    with pytest.raises(SecurityViolationError, match="Invalid Agent Role"):
        im.derive_agent_key("evil/role")

def test_m09_herald_sanitization():
    """Verify Herald strips newlines and truncates long URLs."""
    from agents.herald.agent import HeraldPlugin
    herald = HeraldPlugin("HERALD", {})
    
    long_url = "http://example.com/" + "a" * 300
    dirty_event = {
        "id": "evt_123",
        "summary": f"Line 1\nLine 2\nURL: {long_url}"
    }
    
    clean_event = herald._sanitize_event(dirty_event)
    
    # 1. Newline stripping
    assert "\n" not in clean_event["summary"]
    assert "Line 1 | Line 2" in clean_event["summary"]
    
    # 2. URL truncation
    assert "..." in clean_event["summary"]
    assert len(clean_event["summary"]) < 1000 # Should be well within limits
