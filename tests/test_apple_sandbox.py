import pytest
import os
from src.apple_sandbox import AppleSandbox

@pytest.fixture
def sandbox():
    # Use a specific test workspace
    return AppleSandbox(workspace_dir="/tmp/tachyon_test_tier0")

def test_sandbox_allows_safe_compute(sandbox):
    """Test that a basic compute command like echo works."""
    result = sandbox.execute(["echo", "Hello from Tier 0"])
    
    assert result["status"] == "success"
    assert "Hello from Tier 0" in result["stdout"]
    assert result["exit_code"] == 0

def test_sandbox_blocks_network(sandbox):
    """Test that the sandbox strictly denies network access."""
    # Attempting to curl a reliable host. It should fail instantly due to Seatbelt profile.
    result = sandbox.execute(["curl", "-I", "--max-time", "2", "https://1.1.1.1"])
    
    assert result["status"] == "error"
    assert result["exit_code"] != 0
    # The exact error depends on macOS version, but usually it involves permission denied or could not resolve host
    # Or specifically "Operation not permitted"
    assert "Operation not permitted" in result["stderr"] or "Could not resolve" in result["stderr"] or "Failed to connect" in result["stderr"] or "curl: (6)" in result["stderr"] or "curl: (7)" in result["stderr"]

def test_sandbox_allows_writing_to_workspace(sandbox):
    """Test that the sandbox allows writing to its designated workspace_dir."""
    test_file = os.path.join(sandbox.workspace_dir, "test_write.txt")
    
    result = sandbox.execute(["touch", test_file])
    
    assert result["status"] == "success"
    assert os.path.exists(test_file)
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

def test_sandbox_blocks_writing_outside_workspace(sandbox):
    """Test that writing to forbidden paths (like /System or user home) is blocked."""
    # Attempt to write to a forbidden path
    forbidden_file = "/tmp/forbidden_sandbox_write.txt"
    if os.path.exists(forbidden_file):
        os.remove(forbidden_file)
        
    result = sandbox.execute(["touch", forbidden_file])
    
    assert result["status"] == "error"
    assert result["exit_code"] != 0
    assert "Operation not permitted" in result["stderr"]
    assert not os.path.exists(forbidden_file)

def test_sandbox_dependency_scanner(sandbox):
    """Test that the DependencyScanner identifies poisoned libraries."""
    # Create a dummy malicious file
    malicious_path = os.path.join(sandbox.workspace_dir, "malicious_script.py")
    with open(malicious_path, "w") as f:
        f.write("import os\nimport malicious_crypto_miner\nprint('hacked')")
    
    result = sandbox.execute(["python3", malicious_path])
    assert result["status"] == "BLOCKED"
    assert "Supply Chain Attack Prevented" in result["error"]
    
    # Cleanup
    os.remove(malicious_path)

def test_sandbox_timeout(sandbox):
    """Test that the sandbox correctly handles runaway processes."""
    # Use a safe sleep that exceeds the 30s limit in AppleSandbox.execute
    # (We can mock the timeout or just use a short sleep if we customize the execute call, 
    # but the current execute has a hardcoded 30s. Let's mock subprocess.run to throw TimeoutExpired)
    from unittest.mock import patch
    import subprocess
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="sleep", timeout=30)
        result = sandbox.execute(["sleep", "60"])
        assert result["status"] == "timeout"
        assert "exceeded limits" in result["error"]

