import pytest
from tachyon.enforcement import safe_fetch

def test_safe_fetch_signature_regression():
    """
    Verifies that safe_fetch accepts agent_id and returns a standardized dict.
    This prevents the TypeError regression in test_client.py.
    """
    # Use en.wikipedia.org which is NOT in mock_allowed but we can pass allowed_domains
    # to trigger the evaluation logic.
    url = "https://en.wikipedia.org/wiki/Main_Page"
    
    # Test with agent_id (the previously failing argument)
    response = safe_fetch(url, agent_id="TestAgent", allowed_domains=["en.wikipedia.org"])
    
    assert isinstance(response, dict)
    assert "status" in response
    # It might be BLOCKED if OPA isn't running, but it shouldn't raise TypeError
    assert response["status"] in ["SUCCESS", "BLOCKED", "ERROR"]

def test_safe_fetch_multi_agent_isolation():
    """
    Verifies that different agents can have different allowed_domains.
    """
    url = "https://github.com/google"
    
    # Agent 1 allows github
    res1 = safe_fetch(url, agent_id="Agent1", allowed_domains=["github.com"])
    assert res1["status"] == "SUCCESS"
    
    # Agent 2 does NOT allow github (using mock logic)
    res2 = safe_fetch(url, agent_id="Agent2", allowed_domains=["only-wikipedia.org"])
    assert res2["status"] == "BLOCKED"
