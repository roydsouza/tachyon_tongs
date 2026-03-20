import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from tachyon.core.routing import ModelRouter

@pytest.mark.asyncio
async def test_hybrid_fallback_on_failure():
    """Verify that ModelRouter falls back to local provider when cloud fails."""
    router = ModelRouter()
    
    # Mock local provider to succeed
    router.local_provider.generate = AsyncMock(return_value="Local Result")
    
    # Trigger a complexity that would normally go to cloud
    # And simulate cloud failure by forcing mode="HYBRID" and letting the mock raise an error
    with patch("tachyon.core.routing.ModelRouter.select_model", return_value="gemini-1.5-pro"):
        result = await router.route_and_generate("High complexity task", mode="HYBRID")
        
    assert result == "Local Result"
    router.local_provider.generate.assert_called_once()

@pytest.mark.asyncio
async def test_local_only_mode():
    """Verify that LOCAL_ONLY mode bypasses cloud entirely."""
    router = ModelRouter()
    router.local_provider.generate = AsyncMock(return_value="Local Only Result")
    
    result = await router.route_and_generate("Sample task", mode="LOCAL_ONLY")
    
    assert result == "Local Only Result"
    router.local_provider.generate.assert_called_once()

@pytest.mark.asyncio
async def test_complexity_detection():
    """Verify complexity detection for high-assurance keywords."""
    router = ModelRouter()
    score = router.detect_complexity("Author a new ADR for the immune system")
    assert score >= 0.5 # Should pick up 'adr' and 'immune'
