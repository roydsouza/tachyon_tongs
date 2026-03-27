import os
import subprocess
import pytest
from pathlib import Path

def test_pathogen_crash_alert_persistence():
    """TDAD: Forces a crash in run_pathogen.py and verifies ALERT.md recording."""
    # This is an integration test that runs the script via subprocess
    alert_path = Path("ALERT.md")
    script_path = "scripts/run_pathogen.py"
    
    if not os.path.exists(script_path):
        pytest.skip("run_pathogen.py not found")
        
    # Read original
    with open(script_path, "r") as f:
        original_code = f.read()
    
    # Insert a raise early in execute_sweep for verification
    broken_code = original_code.replace("def execute_sweep(self):", "def execute_sweep(self):\n        raise RuntimeError('TDAD: Automated Regression Crash for GW-06')")
    
    with open(script_path, "w") as f:
        f.write(broken_code)
        
    try:
        # Run it (it should crash and write to ALERT.md)
        subprocess.run(["python3", script_path], capture_output=True, timeout=10)
    finally:
        # Restore original code immediately
        with open(script_path, "w") as f:
            f.write(original_code)
            
    # Verify ALERT.md
    assert alert_path.exists()
    content = alert_path.read_text()
    assert "[PATHOGEN_DAEMON_CRASH]" in content
    assert "TDAD: Automated Regression Crash for GW-06" in content
