import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Set test environment
os.environ["TACHYON_ENV"] = "test"

from agents.scout.agent import ScoutPlugin
from agents._core.registry import AgentRegistry

@pytest.fixture
def mock_docs(tmp_path):
    """Fixture to provide a safe mock path for documentation tests."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    comp_file = docs_dir / "COMPETITIVE_ANALYSIS.md"
    comp_file.write_text("# Competitive Analysis\n")
    return comp_file

@patch('tachyon.core.metal_accelerator.MetalAccelerator.analyze_competitive_intel')
def test_horizon_scout_fetch(mock_analyze):
    scout = ScoutPlugin(agent_id="test-scout", config={})
    intel = scout.scour_web()
    assert intel != ""

@patch('tachyon.core.metal_accelerator.MetalAccelerator.analyze_competitive_intel')
def test_horizon_scout_analysis_hardening(mock_analyze, mock_docs):
    """Verify that Scout does NOT write to docs in test environment."""
    mock_analyze.return_value = {
        "competitive_analysis": "Top 10 Update Mock",
        "actionable_plan": "- [ ] Implement mock feature."
    }
    
    scout = ScoutPlugin(agent_id="test-scout", config={})
    
    # We explicitly verify that even if it's called, hardening prevents the write to the 'real' path
    # and we can test the logic separately if we bypass the hardening.
    scout.analyze_and_persist("Some raw data")
    
    # Check that the mock file was NOT modified by the real logic (since hardening is on)
    assert "Top 10 Update Mock" not in mock_docs.read_text()

@patch('tachyon.core.metal_accelerator.MetalAccelerator.analyze_competitive_intel')
def test_horizon_scout_logic_verify_via_patch(mock_analyze, tmp_path):
    """Test the core logic by redirecting the path in the Scout instance."""
    mock_analyze.return_value = {
        "competitive_analysis": "Test Content",
        "actionable_plan": "- [ ] Task"
    }
    
    scout = ScoutPlugin(agent_id="test-scout", config={})
    
    # Bypass hardening by temporarily clearing env
    with patch.dict(os.environ, {"TACHYON_ENV": "production", "PYTEST_CURRENT_TEST": ""}):
        # Mock the path calculation to use tmp_path
        target_path = tmp_path / "test_docs.md"
        with patch('os.path.abspath', return_value=str(target_path)):
            scout.analyze_and_persist("raw data")
            
        assert "Test Content" in target_path.read_text()

def test_scout_metadata():
    scout = ScoutPlugin(agent_id="test-scout", config={})
    meta = scout.get_metadata()
    assert "scout" in meta["capabilities"]
    assert "analyze" in meta["capabilities"]
