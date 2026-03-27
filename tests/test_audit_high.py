import pytest
import asyncio
import base64
import json
import os
from tachyon.api.pep import PEPLayer
from tachyon.api.schema import ToolRequest
from tachyon.policy.checkers.alignment_pdp import AlignmentPDP
from tachyon.pipeline.pii_scanner import PIIScanner
from tachyon.enforcement.safe_fetch import SafeFetch, SecurityViolationError as SafeFetchError
from tachyon.core.state_manager import StateManager
from tachyon.core.signing import IntegrityManager, SecurityViolationError as SigningError

# --- H-01: PEP Rate Limiting ---

@pytest.mark.asyncio
async def test_pep_rate_limiting_violation():
    """
    Assert that the PEP layer rejects requests when an agent exceeds its rate limit (H-01).
    """
    pep = PEPLayer()
    pep.rate_limiter.default_rpm = 5
    
    agent_id = "flood_agent"
    action = "SAFE_MATH"
    params = {"val1": 1, "val2": 2, "intent": "perform addition"}
    
    # 1. Send 5 allowed requests
    for i in range(5):
        request = ToolRequest(agent_id=agent_id, action=action, parameters=params)
        response = await pep.execute(request)
        assert response.status in ["SUCCESS", "FALLBACK_SUCCESS"]

    # 2. The 6th request should be RATE_LIMITED
    request = ToolRequest(agent_id=agent_id, action=action, parameters=params)
    response = await pep.execute(request)
    assert response.status == "RATE_LIMITED"
    assert "limit exceeded" in response.error

# --- H-03: Semantic Drift (Synonym Resistance) ---

@pytest.mark.asyncio
async def test_semantic_drift_resiliency():
    """
    H-03 goal: Ensure synonyms DO NOT cause drift (score stays high) 
    and mismatched intents ARE detected as drift (score stays low).
    """
    pdp = AlignmentPDP(threshold=0.7)
    
    # CASE 1: Synonym Alignment (H-03 Fix)
    # Both intent and params use different words but same 'concepts' (DESTRUCTION + SUBSTRATE)
    params_align = {
        "intent": "perform routine cleanup of the base layer",
        "action": "mutate_substrate",
        "command": "rm -rf /" 
    }
    verdict_align = await pdp.evaluate("agent_007", "mutate_substrate", params_align)
    # Score should be high (>0.7) because synapses map to same concept
    assert verdict_align.verdict.name == "ALLOW"
    assert verdict_align.metadata.get("alignment_score") > 0.8

    # CASE 2: Semantic Drift (The actual security trigger)
    # Intent is unrelated to the action (Goal Aliasing)
    params_drift = {
        "intent": "check system heartbeat and telemetry",
        "action": "mutate_substrate",
        "command": "rm -rf /"
    }
    verdict_drift = await pdp.evaluate("agent_007", "mutate_substrate", params_drift)
    # Score should be low because 'heartbeat' does not map to 'DESTRUCTION'
    assert verdict_drift.verdict.name == "DENY"
    # Even if it passes initial check, it should hit the 'Refine Alignment' logic
    if "refinement_status" in verdict_drift.metadata:
        assert verdict_drift.metadata["refinement_status"] in ["ADVERSARIAL_DETECTED", "DOUBT_EXPRESSED"]

# --- H-04: Advanced PII (Base64/Hex/Entropy) ---

def test_encoded_pii_detection():
    """
    Assert that Base64 and Hex encoded secrets are detected by the scanner (H-04).
    """
    scanner = PIIScanner()
    
    # 1. Base64 encoded secret
    secret = "sk-ant-api01-secretkey12345678"
    encoded_b64 = base64.b64encode(secret.encode()).decode()
    payload_b64 = f"data: {encoded_b64}"
    
    results = scanner.scan(payload_b64)
    assert any("ENCODED_B64" in f[0] for f in results["findings"])

    # 2. Hex encoded secret
    encoded_hex = secret.encode().hex()
    payload_hex = f"hex: {encoded_hex}"
    results = scanner.scan(payload_hex)
    assert any("ENCODED_HEX" in f[0] for f in results["findings"])

def test_high_entropy_detection():
    """
    Assert that high-entropy data (encrypted blobs) is flagged (H-04).
    """
    scanner = PIIScanner()
    
    import string
    import random
    char_variety = string.ascii_letters + string.digits + string.punctuation
    high_entropy_str = "".join(random.choice(char_variety) for _ in range(100))
    
    results = scanner.scan(high_entropy_str)
    findings = [f[0] for f in results["findings"]]
    assert "HIGH_ENTROPY" in findings

# --- H-06: Signature Stripping (Hybrid) ---

def test_signature_stripping_rejection():
    """
    Assert that malformed or 'stripped' signatures are rejected (H-06).
    """
    from tachyon.core.keys.hybrid import HybridSigner
    from cryptography.hazmat.primitives.asymmetric import ed25519
    
    sk = ed25519.Ed25519PrivateKey.generate()
    signer = HybridSigner(ed25519_sk=sk, ed25519_pk=sk.public_key())
    
    content = b"sensitive data"
    
    # 1. Malformed stripping: "ed25519:" (missing value)
    stripped_malformed = "ed25519:"
    with pytest.raises(ValueError, match="Signature value missing"):
        signer.verify(content, stripped_malformed)
        
    # 2. Unknown algorithm
    unknown_sig = "future-alg:deadbeef"
    with pytest.raises(RuntimeError, match="Packet contains signatures but none could be verified"):
        signer.verify(content, unknown_sig)

# --- H-05: SafeFetch (Redirect Bypasses) ---

def test_safefetch_redirect_block():
    """
    Assert that URLs containing redirect parameters to untrusted domains are blocked (H-05).
    """
    fetcher = SafeFetch(rego_mock=True)
    malicious_redirect = "https://scholar.google.com/url?q=https://malicious-site.com/exploit.sh"
    
    with pytest.raises(SafeFetchError, match="Redirect to untrusted domain"):
        fetcher.fetch(malicious_redirect, intent="RESEARCH")

# --- H-07: Identity Confusion (Process Binding) ---

def test_identity_confusion_prevention():
    """
    Assert that an agent process cannot load keys for a different role (H-07).
    """
    old_test_mode = os.environ.get("TACHYON_TEST_MODE")
    if old_test_mode:
        del os.environ["TACHYON_TEST_MODE"]
    
    try:
        im = IntegrityManager()
        with pytest.raises(SigningError, match="Identity mismatch"):
            im.load_agent_identity("engineer")
    finally:
        if old_test_mode:
            os.environ["TACHYON_TEST_MODE"] = old_test_mode
