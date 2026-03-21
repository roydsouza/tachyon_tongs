import pytest
from tachyon.agents.base import BaseTachyonAgent
from typing import Dict, Any
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="oqs")

class DummyAgent(BaseTachyonAgent):
    def execute_role_logic(self, action: str, parameters: Dict[str, Any]) -> Any:
        return "dummy_result"

@pytest.mark.asyncio
async def test_agent_heartbeat_valid():
    """Agent heartbeat should succeed with a valid certificate."""
    from tachyon.core.signing import IntegrityManager
    
    # We only test if a root key is loadable
    im = IntegrityManager(use_hardware=True)
    if not im._private_key:
        pytest.skip("No Ed25519 Root Key in Keychain")
        
    agent = DummyAgent("dummy_01", "sentinel")
    
    assert agent.agent_key is not None
    assert agent.agent_cert is not None
    
    heartbeat_result = await agent.heartbeat()
    
    assert heartbeat_result["status"] == "SUCCESS"
    assert heartbeat_result["agent_id"] == "dummy_01"

@pytest.mark.asyncio
async def test_agent_heartbeat_revoked(monkeypatch, tmp_path):
    """Agent heartbeat should fail if the certificate is revoked."""
    from tachyon.core.signing import IntegrityManager
    from tachyon.core.keys.certificates import DelegationCertificateAuthority
    
    # Mock CRL logic
    mem_dir = tmp_path / "memory" / "operational"
    mem_dir.mkdir(parents=True)
    crl_path = mem_dir / "revocation_list.json"
    
    original_init = DelegationCertificateAuthority.__init__
    def mock_init(self, im):
        self.im = im
        self.crl_path = str(crl_path)
        self._ensure_crl_exists()
        
    monkeypatch.setattr(DelegationCertificateAuthority, "__init__", mock_init)
    
    im = IntegrityManager(use_hardware=True)
    if not im._private_key:
        pytest.skip("No Ed25519 Root Key in Keychain")
        
    # Instantiate agent
    agent = DummyAgent("dummy_02", "engineer")
    
    # Revoke its certificate manually
    ca = DelegationCertificateAuthority(im)
    fingerprint = agent.agent_cert["payload"]["subject"]["fingerprint"]
    ca.revoke_key(fingerprint, reason="Test Revocation")
    
    heartbeat_result = await agent.heartbeat()
    assert heartbeat_result["status"] == "REVOKED"
    assert "Key revoked" in heartbeat_result["message"]

@pytest.mark.asyncio
async def test_agent_heartbeat_no_cert():
    """Verify that heartbeat returns WARNING if the agent has no certificate."""
    # Create an agent but manually strip its cert (simulating derivation failure)
    agent = DummyAgent("dummy_03", "pathogen")
    agent.agent_cert = None
    
    heartbeat_result = await agent.heartbeat()
    assert heartbeat_result["status"] == "WARNING"
    assert "No delegation certificate" in heartbeat_result["message"]
