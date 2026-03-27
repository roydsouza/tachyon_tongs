import os
import pytest
from tachyon.core.signing import IntegrityManager
from tachyon.core.keys.hybrid import HybridSigner

def test_headless_key_fallback():
    """
    Verifies that the KeychainProvider correctly falls back to memory/keys/
    when hardware access is simulate-failed.
    """
    # Create the memory/keys directory and a dummy root key
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    keys_dir = os.path.join(root_dir, "memory", "keys")
    os.makedirs(keys_dir, exist_ok=True)
    
    root_sk_path = os.path.join(keys_dir, "root_sk.bin")
    # Ed25519 seed is 32 bytes
    dummy_seed = b"A" * 32
    
    with open(root_sk_path, "wb") as f:
        f.write(dummy_seed)
        
    try:
        # Force headless mode to trigger fallback
        os.environ["TACHYON_HEADLESS"] = "1"
        im = IntegrityManager(use_hardware=True) # Even if we ask for hardware, it should fall back
        
        # Verify that a private key was loaded (not None)
        assert im._private_key is not None
        # Verify it matches the dummy seed
        assert im._private_key.private_bytes_raw() == dummy_seed
    finally:
        if os.path.exists(root_key_path := root_sk_path):
            os.remove(root_key_path)
        os.environ.pop("TACHYON_HEADLESS", None)

def test_strip_attack_detection_logic():
    """
    Verifies that HybridSigner correctly detects a stripped signature layer.
    """
    # Create a signer with pure HMAC (no keys)
    signer = HybridSigner(hmac_key=b"test-key")
    content = b"Sensitive Data"
    
    # Sign it (will be HMAC ONLY)
    sig = signer.sign(content)
    assert sig.startswith("hmac:")
    
    # 1. Normal Verification (should pass)
    assert signer.verify(content, sig) is True
    
    # 2. Simulate Strip Attack (Signature exists but doesn't match keys)
    # If we have a PQC PUBLIC KEY but the signature is MISSING it.
    signer_with_pqc = HybridSigner(
        mldsa65_pk=b"P" * 1312, # Dummy ML-DSA-65 Public Key
        hmac_key=b"test-key"
    )
    
    # This verification should FAIL because we have a PQC PK but the sig is HMAC-only
    # (Wait, actually HybridSigner.verify L124 requires PQC SK to trigger the "Strip Attack Detected - SK present" error)
    # But I added L115-118 in Step 1402:
    # if self._pqc_public_key and not has_pqc:
    #     if any(p.startswith("mldsa65:") for p in parts): ...
    
    # Let's test the PQC_STRICT mode
    os.environ["TACHYON_PQC_STRICT"] = "1"
    try:
        with pytest.raises(RuntimeError, match="PQC Signature component MISSING"):
            signer_with_pqc.verify(content, sig)
    finally:
        os.environ.pop("TACHYON_PQC_STRICT", None)

def test_malicious_pqc_component_mismatch():
    """
    Verifies detection of a PQC component that is present but fails verification.
    """
    signer = HybridSigner(
        mldsa65_pk=b"P" * 1312,
        hmac_key=b"test-key"
    )
    content = b"Data"
    # A packet with a fake PQC component
    malicious_sig = "hmac:xxxx|mldsa65:aaaa" 
    
    # Mocking the HMAC so it passes that part
    import hmac; import hashlib
    valid_hmac = hmac.new(b"test-key", content, hashlib.sha256).hexdigest()
        
    malicious_sig = f"hmac:{valid_hmac}|mldsa65:aaaa"
    
    # Should raise "PQC Signature component found but verification FAILED"
    # (Requires liboqs for the verification attempt, otherwise it skips L89)
    # In our test environment, liboqs might be missing.
    
    # If liboqs is missing, has_pqc stays False.
    # Then L115 kicks in because "mldsa65:" is in parts.
    with pytest.raises(RuntimeError, match="PQC Signature component found but verification FAILED or BYPASSED"):
        signer.verify(content, malicious_sig)
