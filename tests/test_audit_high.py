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
from tachyon.core.state import StateManager
from tachyon.core.signing import IntegrityManager, SecurityViolationError as SigningError

# --- H-01: ToolRouter Rate Limiting ---

@pytest.mark.asyncio
async def test_pep_rate_limiting_violation():
    """
    Assert that the ToolRouter rejects requests when an agent exceeds its rate limit (H-01).
    """
    from tachyon.enforcement.router import ToolRouter
    from tachyon.enforcement.rate_limiter import AdaptiveRateLimiter
    from unittest.mock import MagicMock, AsyncMock

    # 3. Setup ToolRouter with a restricted rate limit
    limiter = AdaptiveRateLimiter(default_rpm=5)
    
    # 4. Mock policy engine to return ALLOW
    policy_engine = AsyncMock()
    from tachyon.policy.engine import PolicyVerdict, Verdict
    policy_engine.evaluate.return_value = PolicyVerdict(verdict=Verdict.ALLOW, reason="Access granted", engine_id="mock_pdp", metadata={})

    # Minimal mocks for router dependencies
    router = ToolRouter(
        orchestrator=MagicMock(),
        sandbox=MagicMock(),
        policy_engine=policy_engine,
        cot_monitor=MagicMock(),
        syscall_monitor=MagicMock(),
        rate_limiter=limiter
    )
    
    # 5. Register a mock handler to avoid ERROR: Unknown action
    async def mock_handler(agent_id, params):
        return {"status": "SUCCESS", "result": 3}
    router.registry.register("SAFE_MATH", mock_handler)
    
    agent_id = "flood_agent"
    action = "SAFE_MATH"
    params = {"val1": 1, "val2": 2}
    
    # 3. Send 5 allowed requests
    for i in range(5):
        response = await router.route(agent_id=agent_id, action=action, params=params)
        assert response["status"] == "SUCCESS"

    # 4. The 6th request should be BLOCKED by rate limiter
    response = await router.route(agent_id=agent_id, action=action, params=params)
    assert response["status"] == "BLOCKED"
    assert "RATE_LIMIT_EXCEEDED" in response["error"]

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

def test_safefetch_redirect_block(monkeypatch):
    """
    Assert that URLs containing redirect parameters to untrusted domains are blocked (H-05).
    """
    monkeypatch.setenv("TACHYON_TEST_MODE", "1")
    fetcher = SafeFetch()
    malicious_redirect = "https://scholar.google.com/url?q=https://malicious-site.com/exploit.sh"
    
    result = fetcher.fetch(malicious_redirect, intent="RESEARCH")
    assert result.status == "BLOCKED"
    assert "untrusted domain" in result.error or "private host" in result.error or "unauthorized" in result.error.lower()

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

# --- VX-04: Immunologist Registration ---

def test_vx04_immunologist_registration():
    """Assert AgentRegistry successfully resolves the previously missing Immunologist."""
    from agents._core.registry import AgentRegistry
    # AgentRegistry._plugins should contain "immunologist"
    import agents.immunologist.agent  # Ensure module loads
    plugin_class = AgentRegistry.get_plugin("immunologist")
    assert plugin_class is not None, "Immunologist is missing from the AgentRegistry."
    assert plugin_class.__name__ == "ImmunologistPlugin"

# --- VX-05: Ephemeral Test Identities ---

def test_vx05_ephemeral_test_identities(monkeypatch, tmp_path):
    """Assert TEST_MODE key derivation refuses to save persistence to disk."""
    import os
    from tachyon.core.signing import IntegrityManager
    
    # Temporarily set test keys path to somewhere we can watch
    test_key_dir = tmp_path / "keys"
    test_key_dir.mkdir()
    
    # We must patch load_agent_identity since we want to only test derive_agent_key behavior
    monkeypatch.setenv("TACHYON_TEST_MODE", "1")
    im = IntegrityManager(use_hardware=False)
    
    # Monkeypatch the key_dir logic if accessible, or just verify base plugin logic.
    # The actual requirement is that derived identities do NOT hit the disk.
    # The patch changed `save_to_disk=True` to `save_to_disk=False` in base.py.
    from agents._core.base import BaseAgentPlugin
    
    class DummyPlugin(BaseAgentPlugin):
        def execute_action(self, action, parameters):
            pass
            
    # Mock IM to see what base plugin passes to derive_agent_key
    derived_with_disk = []
    original_derive = im.derive_agent_key
    
    def mock_derive(role, save_to_disk=False):
        if save_to_disk:
            derived_with_disk.append(role)
        return original_derive(role, save_to_disk=save_to_disk)
        
    monkeypatch.setattr(im, "derive_agent_key", mock_derive)
    
    # If production, it should crash.
    monkeypatch.setenv("TACHYON_ENV", "production")
    with pytest.raises(RuntimeError, match="SECURITY_VIOLATION: TEST_MODE cannot be enabled in production environments"):
        DummyPlugin("agent_x", "Dummy", {"integrity_manager": im, "event_bus": None})
        
    # If not production, it should derive but NOT save to disk.
    monkeypatch.setenv("TACHYON_ENV", "development")
    agent = DummyPlugin("agent_x", "Dummy", {"integrity_manager": im, "event_bus": None})
    assert len(derived_with_disk) == 0, "TEST_MODE derived keys were saved to disk!"

# --- VX-06: Sandbox Hardening (AST Parsing) ---

def test_vx06_ast_sandboxing_evasion():
    """Assert AST execution evaluation blocks obfuscated __import__ evasion."""
    from agents.pathogen.agent import PathogenPlugin
    from unittest.mock import MagicMock
    
    agent = PathogenPlugin("pathogen_x", {"event_bus": MagicMock(), "integrity_manager": MagicMock()})
    
    # Traditional bypass
    payload_1 = "__import__('os').system('id')"
    res_1 = agent.execute_action("verify_variant", {"variant": payload_1})
    assert res_1["status"] == "FAILED"
    assert "Any import is dangerous" in res_1["reason"] or "Dangerous call" in res_1["reason"]

    # Obfuscated eval
    payload_2 = "eval('__import__(\\'os\\')')"
    res_2 = agent.execute_action("verify_variant", {"variant": payload_2})
    assert res_2["status"] == "FAILED"
    assert "eval" in res_2["reason"] or "import" in res_2["reason"]

# --- VX-07: Parameterize SBOM Resolver Directory ---

def test_vx07_sbom_resolver(monkeypatch, tmp_path):
    """Assert missing SBOM strictly fails without leaking local developer paths."""
    from agents._core.registry import _verify_agent_hash, RegistrationError
    import os
    
    monkeypatch.setenv("TACHYON_STRICT_MODE", "1")
    fake_sbom_path = tmp_path / "fake_sbom.json"
    monkeypatch.setenv("TACHYON_SBOM_PATH", str(fake_sbom_path))
    
    # Provide a fake module path
    module_path = "agents/dummy/agent.py"
    try:
        os.makedirs(os.path.dirname(module_path), exist_ok=True)
        with open(module_path, "w") as f:
            f.write("pass")
            
        with pytest.raises(RegistrationError, match="SBOM Missing"):
            _verify_agent_hash("agents", module_path)
    finally:
        if os.path.exists(module_path):
            os.remove(module_path)

