"""
Test Suite: Hybrid Signing Pipeline (Ed25519 + ML-DSA-65)
Tests the IntegrityManager sign/verify roundtrip, dual-signature mandate,
legacy HMAC fallback, and signature strip detection.
"""
import os
import json
import pytest
import tempfile
import warnings

# Suppress liboqs version warning
warnings.filterwarnings("ignore", category=UserWarning, module="oqs")


class TestHybridSigningEd25519Only:
    """Tests for the Ed25519-only signing path (no PQC key loaded)."""
    
    def test_sign_verify_roundtrip_ed25519(self):
        """Ed25519 sign+verify roundtrip should pass when hardware key is loaded."""
        from tachyon.core.signing import IntegrityManager
        im = IntegrityManager(use_hardware=True)
        if not im._private_key:
            pytest.skip("No Ed25519 key in Keychain (non-macOS or unconfigured)")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\nHello World\n")
            f.flush()
            path = f.name
        try:
            digest = im.sign_document(path)
            assert digest, "sign_document should return a non-empty digest"
            assert "ed25519:" in digest, "Digest should contain Ed25519 signature"
            # Verify
            result = im.verify_integrity(path)
            assert result is True, "verify_integrity should return True"
        finally:
            os.unlink(path)
            sig_path = path + ".sig"
            if os.path.exists(sig_path):
                os.unlink(sig_path)
    
    def test_missing_sig_file_raises(self):
        """Verification without a .sig file should raise RuntimeError."""
        from tachyon.core.signing import IntegrityManager
        im = IntegrityManager(use_hardware=True)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Unsigned Document\n")
            f.flush()
            path = f.name
        try:
            with pytest.raises(RuntimeError, match="No detached signature found"):
                im.verify_integrity(path)
        finally:
            os.unlink(path)
    
    def test_stale_signature_detection(self):
        """Modifying a file after signing should cause verification failure."""
        from tachyon.core.signing import IntegrityManager
        im = IntegrityManager(use_hardware=True)
        if not im._private_key:
            pytest.skip("No Ed25519 key in Keychain")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Original Content\n")
            f.flush()
            path = f.name
        try:
            im.sign_document(path)
            # Tamper with the file
            with open(path, 'w') as f:
                f.write("# TAMPERED Content\n")
            with pytest.raises(RuntimeError, match="INTEGRITY COMPROMISED"):
                im.verify_integrity(path)
        finally:
            os.unlink(path)
            sig_path = path + ".sig"
            if os.path.exists(sig_path):
                os.unlink(sig_path)


class TestHybridSigningPQC:
    """Tests for the Hybrid (Ed25519 + ML-DSA-65) signing path."""
    
    def test_sign_verify_roundtrip_hybrid(self):
        """Hybrid sign+verify should produce both ed25519: and mldsa65: layers."""
        from tachyon.core.signing import IntegrityManager
        im = IntegrityManager(use_hardware=True)
        if not im._private_key:
            pytest.skip("No Ed25519 key in Keychain")
        if not im._pqc_private_key_bytes:
            pytest.skip("No PQC key in Keychain")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Hybrid Test Document\nQuantum Ready.\n")
            f.flush()
            path = f.name
        try:
            digest = im.sign_document(path)
            assert "ed25519:" in digest, "Should contain Ed25519 layer"
            assert "mldsa65:" in digest, "Should contain ML-DSA-65 layer"
            # Verify
            result = im.verify_integrity(path)
            assert result is True
        finally:
            os.unlink(path)
            sig_path = path + ".sig"
            if os.path.exists(sig_path):
                os.unlink(sig_path)
    
    def test_pqc_signature_strip_detection(self):
        """Removing the PQC layer from a .sig file should be detected."""
        from tachyon.core.signing import IntegrityManager
        im = IntegrityManager(use_hardware=True)
        if not im._private_key:
            pytest.skip("No Ed25519 key in Keychain")
        if not im._pqc_private_key_bytes:
            pytest.skip("No PQC key in Keychain")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Strip Test Document\n")
            f.flush()
            path = f.name
        try:
            im.sign_document(path)
            # Strip the PQC layer
            sig_path = path + ".sig"
            with open(sig_path, 'r') as sf:
                raw = sf.read()
            stripped = "|".join(p for p in raw.split("|") if not p.startswith("mldsa65:"))
            with open(sig_path, 'w') as sf:
                sf.write(stripped)
            # Verification should detect the missing PQC layer
            with pytest.raises(RuntimeError, match="PQC Signature MISSING"):
                im.verify_integrity(path)
        finally:
            os.unlink(path)
            sig_path = path + ".sig"
            if os.path.exists(sig_path):
                os.unlink(sig_path)


class TestHMACFallback:
    """Tests for the legacy HMAC fallback path."""
    
    def test_hmac_fallback_when_no_keys(self):
        """When no hardware keys are loaded, signing should use HMAC."""
        from tachyon.core.signing import IntegrityManager
        im = IntegrityManager(use_hardware=False)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# HMAC Test Document\n")
            f.flush()
            path = f.name
        try:
            digest = im.sign_document(path)
            assert "hmac:" in digest, "Should fall back to HMAC"
            assert "ed25519:" not in digest, "Should NOT contain Ed25519"
            assert "mldsa65:" not in digest, "Should NOT contain ML-DSA-65"
            # Verify
            result = im.verify_integrity(path)
            assert result is True
        finally:
            os.unlink(path)
            sig_path = path + ".sig"
            if os.path.exists(sig_path):
                os.unlink(sig_path)
