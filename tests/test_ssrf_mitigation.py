import pytest
from unittest.mock import MagicMock
from tachyon.enforcement.safe_fetch import SafeFetch, SecurityViolationError
from tachyon.enforcement.network import NetworkPolicy

def test_localhost_block():
    """Verify that localhost/loopback is blocked (S-01)."""
    fetcher = SafeFetch(agent_id="test-agent", rego_mock=True)
    
    # Test IPv4 loopback
    result = fetcher.fetch("http://127.0.0.1:9181")
    assert result.status == "BLOCKED"
    assert "private host" in result.error
    
    # Test IPv6 loopback
    result = fetcher.fetch("http://[::1]:9181")
    assert result.status == "BLOCKED"
    assert "private host" in result.error

def test_private_range_block():
    """Verify that RFC 1918 private ranges are blocked (S-01)."""
    fetcher = SafeFetch(agent_id="test-agent", rego_mock=True)
    
    # Test 10.x.x.x
    result = fetcher.fetch("http://10.0.0.1/api")
    assert result.status == "BLOCKED"
    
    # Test 192.168.x.x
    result = fetcher.fetch("http://192.168.1.100/status")
    assert result.status == "BLOCKED"

def test_cloud_metadata_block():
    """Verify that Cloud Metadata service (169.254.169.254) is blocked (S-01)."""
    fetcher = SafeFetch(agent_id="test-agent", rego_mock=True)
    
    result = fetcher.fetch("http://169.254.169.254/computeMetadata/v1/")
    assert result.status == "BLOCKED"
    assert "private host" in result.error

def test_dns_rebinding_simulation(monkeypatch):
    """
    Simulates a DNS rebinding scenario where a hostname resolves to both 
    a public and a private IP. The policy must block if ANY IP is private.
    """
    fetcher = SafeFetch(agent_id="test-agent", rego_mock=True)
    
    # Mock NetworkPolicy.resolve_safe to return a public and a private IP
    def mock_resolve(hostname):
        if hostname == "rebind.com":
            return ["93.184.216.34", "127.0.0.1"] # example.com and localhost
        return []
    
    monkeypatch.setattr(NetworkPolicy, "resolve_safe", mock_resolve)
    
    result = fetcher.fetch("http://rebind.com/data")
    assert result.status == "BLOCKED"
    assert "private host" in result.error

def test_redirect_to_private_block(monkeypatch):
    """Verify that a redirect to a private IP is blocked (S-01)."""
    fetcher = SafeFetch(agent_id="test-agent", rego_mock=True)
    
    # We need to mock the actual network call to return a 302 redirect
    from unittest.mock import MagicMock
    
    mock_response = MagicMock()
    mock_response.getcode.side_effect = [302, 200]
    mock_response.headers = {'Location': 'http://127.0.0.1/secret'}
    mock_response.__enter__.return_value = mock_response
    
    # Mock original evaluate_intent to return True for the first hop
    # but the second hop (127.0.0.1) will be blocked by the real evaluate_intent
    original_evaluate = fetcher._evaluate_intent
    def mock_evaluate(url):
        if "127.0.0.1" in url:
            return original_evaluate(url) # Should return False
        return True
    
    monkeypatch.setattr(fetcher, "_evaluate_intent", mock_evaluate)
    
    # Mock urllib.request.OpenerDirector.open
    import urllib.request
    monkeypatch.setattr("urllib.request.OpenerDirector.open", lambda self, req, timeout: mock_response)
    
    result = fetcher.fetch("http://public-site.com/redirect")
    assert result.status == "BLOCKED"
    assert "private host" in result.error

def test_max_redirects_exhaustion(monkeypatch):
    """Verify that infinite redirect loops are terminated (S-01)."""
    fetcher = SafeFetch(agent_id="test-agent", rego_mock=True)
    
    mock_response = MagicMock()
    mock_response.getcode.return_value = 302
    mock_response.headers = {'Location': 'http://public-site.com/loop'}
    mock_response.__enter__.return_value = mock_response
    
    monkeypatch.setattr(fetcher, "_evaluate_intent", lambda url: True)
    
    import urllib.request
    monkeypatch.setattr("urllib.request.OpenerDirector.open", lambda self, req, timeout: mock_response)
    
    result = fetcher.fetch("http://public-site.com/loop")
    assert result.status == "BLOCKED"
    assert "Maximum redirect hops" in result.error
