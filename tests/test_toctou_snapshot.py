import pytest
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from tachyon.enforcement.router import ToolRouter
from tachyon.policy.engines.rego_engine import RegoPolicyEngine
from tachyon.policy.engine import Verdict

@pytest.mark.asyncio
async def test_toctou_policy_drift_detection(tmp_path):
    """
    Assert that ToolRouter detects when a policy file is modified 
    between the snapshot and evaluation phases (C-07).
    """
    # 1. Setup a real RegoPolicyEngine with a temp directory
    policy_dir = tmp_path / "policies"
    policy_dir.mkdir()
    rego_file = policy_dir / "test.rego"
    rego_file.write_text("package test\nallow := true")
    
    # Mock the integrity manager to return a specific hash
    with patch("tachyon.policy.engines.rego_engine.IntegrityManager") as MockIntegrity:
        mock_im = MockIntegrity.return_value
        mock_im.get_file_hash.side_effect = lambda p: "hash_v1" if "v1" in str(p) else "hash_v2"
        mock_im.verify_integrity.return_value = True
        
        engine = RegoPolicyEngine(policy_dir=str(policy_dir), enforce_signatures=False)
        
        # 2. Setup Router
        router = ToolRouter(
            orchestrator=MagicMock(),
            sandbox=MagicMock(),
            policy_engine=engine,
            cot_monitor=MagicMock(),
            syscall_monitor=MagicMock()
        )
        
        # 3. Snapshot the state
        snapshot = engine.get_state_snapshot()
        
        # 4. Simulate malicious drift by changing what get_file_hash returns for the same path
        # In a real race, the file content changes; here we mock the hash change.
        mock_im.get_file_hash.side_effect = lambda p: "hash_v2_drifted"
        
        # 5. Evaluate with the stale snapshot
        verdict = await engine.evaluate("test_agent", "test_action", {}, snapshot=snapshot)
        
        assert verdict.verdict == Verdict.DENY
        assert "TOCTOU VIOLATION" in verdict.reason

@pytest.mark.asyncio
async def test_router_integration_snapshot_pass():
    """Verify that ToolRouter successfully passes the snapshot to the engine."""
    mock_engine = MagicMock(spec=RegoPolicyEngine)
    mock_engine.get_state_snapshot.return_value = {"key": "val"}
    mock_engine.evaluate = AsyncMock()
    
    router = ToolRouter(
        orchestrator=MagicMock(),
        sandbox=MagicMock(),
        policy_engine=mock_engine,
        cot_monitor=MagicMock(),
        syscall_monitor=MagicMock()
    )
    
    await router.route("agent", "action", {"p": 1})
    
    # Ensure evaluate was called with the snapshot from get_state_snapshot
    args, kwargs = mock_engine.evaluate.call_args
    assert kwargs["snapshot"] == {"key": "val"}
