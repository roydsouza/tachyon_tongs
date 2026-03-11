import pytest
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.substrate_daemon import app

client = TestClient(app)

def test_intent_mapping_research():
    # Test that 'RESEARCH' intent allows arxiv.org
    payload = {
        "agent_id": "TestAgent",
        "action": "safe_fetch",
        "parameters": {
            "url": "https://arxiv.org/pdf/2401.00001.pdf",
            "intent": "RESEARCH"
        }
    }
    
    # Mock the supervisor so we don't need a real OPA/MLX stack
    with patch('src.substrate_daemon.run_supervisor') as mock_supervisor:
        mock_supervisor.return_value = {
            "analysis": {"status": "success", "threats_found": []},
            "sanitized_content": "Mock Content"
        }
        
        response = client.post("/action", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS", f"Expected SUCCESS, got {data.get('status')}: {data.get('error')}"
        assert data["result"]["intent_gated"] == "RESEARCH"
        
        # Verify allowed_domains was populated by RESEARCH intent
        _, kwargs = mock_supervisor.call_args
        assert "arxiv.org" in kwargs["allowed_domains"]

def test_intent_mapping_security():
    payload = {
        "agent_id": "TestAgent",
        "action": "safe_fetch",
        "parameters": {
            "url": "https://cisa.gov/known-exploits",
            "intent": "SECURITY"
        }
    }
    
    with patch('src.substrate_daemon.run_supervisor') as mock_supervisor:
        mock_supervisor.return_value = {
            "analysis": {"status": "success", "threats_found": []},
            "sanitized_content": "Mock Content"
        }
        
        response = client.post("/action", json=payload)
        assert response.status_code == 200
        _, kwargs = mock_supervisor.call_args
        assert "cisa.gov" in kwargs["allowed_domains"]

def test_denylist_propagation():
    payload = {
        "agent_id": "TestAgent",
        "action": "safe_fetch",
        "parameters": {
            "url": "https://pastebin.com/raw/malicious",
            "intent": "DEFAULT"
        }
    }
    
    with patch('src.substrate_daemon.run_supervisor') as mock_supervisor:
        mock_supervisor.return_value = {
            "analysis": {"status": "success", "threats_found": []},
            "sanitized_content": "Mock Content"
        }
        
        response = client.post("/action", json=payload)
        assert response.status_code == 200
        _, kwargs = mock_supervisor.call_args
        assert "pastebin.com" in kwargs["denylist"]
