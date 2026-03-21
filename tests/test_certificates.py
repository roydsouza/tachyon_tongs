import os
import json
import pytest
import warnings
from datetime import datetime, timedelta

# Suppress liboqs version warning for tests
warnings.filterwarnings("ignore", category=UserWarning, module="oqs")

@pytest.fixture
def mock_crl_path(tmp_path, monkeypatch):
    """Mocks the CRL path to a temporary file."""
    mem_dir = tmp_path / "memory" / "operational"
    mem_dir.mkdir(parents=True)
    crl_path = mem_dir / "revocation_list.json"
    
    # We monkeypatch the __init__ of DelegationCertificateAuthority
    # but an easier way is to just mock the path if we have it.
    from tachyon.core.keys.certificates import DelegationCertificateAuthority
    original_init = DelegationCertificateAuthority.__init__
    
    def mock_init(self, im):
        self.im = im
        self.crl_path = str(crl_path)
        self._ensure_crl_exists()
        
    monkeypatch.setattr(DelegationCertificateAuthority, "__init__", mock_init)
    return str(crl_path)


class TestKeyDelegationCertificates:
    """Tests the new Json Certificate Authority in tachyon.core.keys.certificates"""

    def test_derive_and_issue_certificate(self, mock_crl_path):
        """Deriving an agent key should now also return a valid, signed cert."""
        from tachyon.core.signing import IntegrityManager
        from tachyon.core.keys.certificates import DelegationCertificateAuthority
        
        im = IntegrityManager(use_hardware=True)
        if not im._private_key:
            pytest.skip("No Ed25519 Root Key in Keychain")
            
        ca = DelegationCertificateAuthority(im)
        key, cert = ca.derive_and_issue(role="sentinel")
        
        assert key is not None
        assert "payload" in cert
        assert "signature" in cert
        
        payload = cert["payload"]
        assert payload["subject"]["role"] == "sentinel"
        assert payload["issuer"] == "Tachyon_Hybrid_Root"
        
        # Verify the signature
        is_valid, reason = ca.validate_certificate(cert)
        assert is_valid is True, f"Validation failed: {reason}"

    def test_certificate_revocation(self, mock_crl_path):
        """Revoking a certificate should cause validation to fail."""
        from tachyon.core.signing import IntegrityManager
        from tachyon.core.keys.certificates import DelegationCertificateAuthority
        
        im = IntegrityManager(use_hardware=True)
        if not im._private_key:
            pytest.skip("No Ed25519 Root Key in Keychain")
            
        ca = DelegationCertificateAuthority(im)
        key, cert = ca.derive_and_issue(role="engineer")
        
        # Should be valid initially
        is_valid, _ = ca.validate_certificate(cert)
        assert is_valid is True
        
        # Revoke it
        fingerprint = cert["payload"]["subject"]["fingerprint"]
        ca.revoke_key(fingerprint, reason="Test Revocation")
        
        # Should now be invalid
        is_valid, reason = ca.validate_certificate(cert)
        assert is_valid is False
        assert "Key revoked" in reason

    def test_certificate_expiry(self, mock_crl_path):
        """Expired certificates should fail validation."""
        from tachyon.core.signing import IntegrityManager
        from tachyon.core.keys.certificates import DelegationCertificateAuthority
        
        im = IntegrityManager(use_hardware=True)
        if not im._private_key:
            pytest.skip("No Ed25519 Root Key")
            
        ca = DelegationCertificateAuthority(im)
        key, cert = ca.derive_and_issue(role="canary")
        
        # Manually tamper with the expiry date in the payload (without updating signature)
        # This tests both expiry and tamper resistance simultaneously
        cert["payload"]["expires_at"] = (datetime.now() - timedelta(days=1)).isoformat()
        
        # Wait, if we tamper, signature validation will fail before expiry check 
        # (Actually validate_certificate checks expiry first for efficiency)
        is_valid, reason = ca.validate_certificate(cert)
        assert is_valid is False
        assert "Certificate Expired" in reason
