import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.horizon_scout import HorizonScout
from src.metal_accelerator import MetalAccelerator

@patch('src.horizon_scout.safe_fetch')
def test_horizon_scout_fetch(mock_fetch):
    mock_fetch.return_value = {
        "status": "SUCCESS",
        "result": {"content": "Sample arXiv paper about agentic firewalls."}
    }
    scout = HorizonScout()
    # reduce sources to 1 for this test
    scout.sources = ["https://arxiv.org/example"]
    
    intel = scout.scour_web()
    assert "Sample arXiv paper" in intel

@patch('src.metal_accelerator.MetalAccelerator.analyze_competitive_intel')
def test_horizon_scout_analysis_persistence(mock_analyze):
    mock_analyze.return_value = {
        "competitive_analysis": "Top 10 Update Mock",
        "actionable_plan": "- [ ] Implement mock feature."
    }
    
    scout = HorizonScout()
    scout.analyze_and_persist("Some raw data from the web")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docs_path = os.path.join(base_dir, '..', 'docs', 'COMPETITIVE_ANALYSIS.md')
    strategy_path = os.path.join(base_dir, '..', 'PENDING_STRATEGY_MERGE.md')
    
    assert os.path.exists(docs_path)
    assert os.path.exists(strategy_path)
    
    with open(docs_path, 'r') as f:
        assert "Top 10 Update Mock" in f.read()
        
    with open(strategy_path, 'r') as f:
        content = f.read()
        assert "Implement mock feature" in content
        assert "[PENDING REVIEW]" in content
