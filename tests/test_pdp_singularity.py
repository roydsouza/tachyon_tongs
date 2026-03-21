import pytest
import os
from tachyon.policy.singularity import SingularityPDP
from tachyon.policy.engine import Verdict
from tachyon.core.signing import IntegrityManager

def test_singularity_initialization():
    pdp = SingularityPDP()
    assert len(pdp.engines) >= 1
    assert any(e.engine_id == "REGO_OPA" for e in pdp.engines)

def test_rego_integrity_enforcement():
    # Create a dummy rego file without a signature
    os.makedirs("policies/rego/manual", exist_ok=True)
    rego_path = "policies/rego/manual/test_integrity.rego"
    with open(rego_path, "w") as f:
        f.write('package test\ndefault allow = false')
    
    # Sig file is missing, so Rego engine should return DENY with integrity error
    # We must configure the PDP to look in the manual dir
    pdp = SingularityPDP()
    for engine in pdp.engines:
        if engine.engine_id == "REGO_OPA":
            engine.policy_dir = "policies/rego/manual"
    verdict = pdp.evaluate("agent_x", "do_something", {})
    
    assert verdict.verdict == Verdict.DENY
    assert "INTEGRITY FAILURE" in verdict.reason
    assert "test_integrity.rego" in verdict.reason

def test_rego_integrity_pass():
    rego_path = "policies/rego/manual/test_integrity.rego"
    im = IntegrityManager()
    im.sign_document(rego_path)
    
    # Now it should pass integrity check (and use the mock allow logic)
    pdp = SingularityPDP()
    for engine in pdp.engines:
        if engine.engine_id == "REGO_OPA":
            engine.policy_dir = "policies/rego/manual"
    verdict = pdp.evaluate("agent_x", "do_something", {})
    
    assert verdict.verdict == Verdict.ALLOW
    
    # Cleanup
    os.remove(rego_path)
    os.remove(rego_path + ".sig")
