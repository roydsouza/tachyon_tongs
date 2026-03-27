import pytest
import os
import json
from tachyon.core.observability import LogContext, AdaptiveTimeout
from tachyon.enforcement.safe_fetch import SafeFetch, FetchResult, SecurityViolationError
from agents._core.registry import AgentRegistry, RegistrationError
from tachyon.pipeline.verifier import VerifierAgent, VerificationFailedError

def test_l02_log_context():
    """Verify structured logging context (L-02)."""
    ctx = LogContext(agent_id="test-agent")
    assert ctx.agent_id == "test-agent"
    assert ctx.correlation_id.startswith("corr_")
    # Manual check: This should output JSON logs to stderr/stdout
    ctx.info("UNIT_TEST_EVENT", detail="test")

def test_l03_adaptive_timeout():
    """Verify adaptive timeouts based on load (L-03)."""
    timeout = AdaptiveTimeout.get_timeout(50) # 50ms base
    assert timeout >= 0.05 # Should be at least 50ms
    assert timeout <= 0.25 # Should be reasonably capped at 5x

def test_sf_03_safe_fetch_result():
    """Verify structured FetchResult from SafeFetch (SF-03)."""
    fetcher = SafeFetch(agent_id="test", rego_mock=True)
    # Blocked domain
    res = fetcher.fetch("http://pastebin.com/payload.sh")
    assert isinstance(res, FetchResult)
    assert res.status == "BLOCKED"
    assert "Intent Gate blocked" in res.error
    assert res.latency_ms > 0

    # Allowed domain (mock)
    res = fetcher.fetch("https://google.com")
    assert res.status == "SUCCESS"
    assert res.latency_ms > 0

def test_sf_04_registry_fail_loud():
    """Verify Registry raises RegistrationError (SF-04)."""
    # Test duplicate registration
    @AgentRegistry.register("duplicate_agent")
    class AgentA: pass
    
    with pytest.raises(RegistrationError, match="Duplicate agent ID registered"):
        @AgentRegistry.register("duplicate_agent")
        class AgentB: pass

def test_sf_02_verifier_raise():
    """Verify VerifierAgent raises VerificationFailedError (SF-02)."""
    verifier = VerifierAgent("v1", {})
    # Clean payload
    res = verifier.verify({"data": "safe content"})
    assert res["verified"] is True
    
    # Malicious payload
    with pytest.raises(VerificationFailedError, match="Contamination detected"):
        verifier.verify({"data": "rm -rf / --no-preserve-root"})
