import pytest
import os
import json
import datetime
import unittest.mock as mock
from src.state_manager import StateManager
from src.agents.engineer_agent import engineer_action_node
from scripts.sentinel import check_temporal_fallback

def test_skeptic_integration():
    """Verify that the Engineer runs the Skeptic and stages the output."""
    state = {
        "analysis": {
            "id": "CVE-TEST-001",
            "description": "Test vulnerability",
            "threats_found": [{"id": "CVE-TEST-001", "description": "High risk"}]
        },
        "scraped_threats": [{"id": "CVE-TEST-001", "source": "Unit Test"}],
        "airlock_mode": True
    }
    
    # Mocking MetalAccelerator to avoid LLM calls
    import unittest.mock as mock
    with mock.patch("src.metal_accelerator.MetalAccelerator.generate_remediation_patch") as mock_patch:
        mock_patch.return_value = {
            "patch_files": {"src/dummy.py": "print('fixed')"},
            "test_file_path": "tests/test_dummy.py",
            "test_content": "def test_pass(): assert True"
        }
        
        # We need a logger mock
        logger = mock.Mock()
        state["logger"] = logger
        
        result = engineer_action_node(state)
        
        assert result["final_output"]["status"] == "staged"
        proposal_path = result["final_output"]["proposal_path"]
        assert os.path.exists(proposal_path)
        
        with open(proposal_path, "r") as f:
            data = json.load(f)
            assert "critique" in data
            assert data["cve_id"] == "CVE-TEST-001"

def test_temporal_fallback_trigger():
    """Verify that check_temporal_fallback picks up aged files."""
    staging_dir = "/tmp/tachyon_airlock"
    os.makedirs(staging_dir, exist_ok=True)
    
    # Create an 'old' proposal (13 hours ago)
    old_time = (datetime.datetime.now() - datetime.timedelta(hours=13)).isoformat()
    proposal = {
        "cve_id": "CVE-OLD-999",
        "staged_at": old_time,
        "patch_files": {"src/old_fix.py": "pass"},
        "test_file_path": "tests/test_old.py",
        "test_content": "pass"
    }
    
    path = os.path.join(staging_dir, "CVE-OLD-999.json")
    with open(path, "w") as f:
        json.dump(proposal, f)
        
    with mock.patch("src.auto_patcher.AutoPatcher.apply_and_test") as mock_apply:
        check_temporal_fallback()
        assert mock_apply.called
        assert not os.path.exists(path) # Cleanup check
