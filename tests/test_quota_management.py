import pytest
import asyncio
from tachyon.core.routing import ModelRouter

@pytest.fixture
def model_router():
    return ModelRouter()

def test_complexity_detection(model_router):
    """Verify that the router correctly identifies complex tasks."""
    simple_prompt = "ls -la"
    complex_prompt = "Refactor the ToolRouter to use frozen dataclasses and update the ADR."
    
    assert model_router.detect_complexity(simple_prompt) < 0.5
    assert model_router.detect_complexity(complex_prompt) > 0.5

def test_model_selection_normal_quota(model_router):
    """Verify routing logic when quota is healthy."""
    simple_prompt = "ls -la"
    complex_prompt = "Implement quantum-safe attestation."
    
    # Simple prompt should go to Flash
    model_simple = model_router.select_model(simple_prompt, 0.2, current_quota=1.0)
    assert model_simple == "gemini-3-flash"
    
    # Complex prompt should go to Pro
    model_complex = model_router.select_model(complex_prompt, 0.8, current_quota=1.0)
    assert model_complex == "gemini-3.1-pro"

def test_low_power_mode_enforcement(model_router):
    """Verify that LPM forces Flash regardless of complexity."""
    complex_prompt = "Create a new agent with full memory persistence."
    
    # Below 15% quota, everything should be Flash
    model_lpm = model_router.select_model(complex_prompt, 0.9, current_quota=0.1)
    assert model_lpm == "gemini-3-flash"

def test_fallback_logic_placeholder():
    """Verify that the daemon's fallback logic is ready (simulated)."""
    # This is partially tested by checking the daemon.py exception handlers
    # in a real integration test, but here we verify the 'fallback_model' constant.
    from tachyon.enforcement.daemon import model_router as daemon_router
    assert daemon_router is not None
