import pytest
import os
import shutil
from agents._core.registry import AgentRegistry

def test_registry_load_failure_alert(tmp_path):
    """TDAD: This test verifies that AgentRegistry currently fails to write to ALERT.md on load error."""
    # Create a mock agents directory with a broken agent
    agents_dir = tmp_path / "agents"
    broken_agent_dir = agents_dir / "broken_agent"
    broken_agent_dir.mkdir(parents=True)
    
    # Create config.yaml
    (broken_agent_dir / "config.yaml").write_text("agent_id: broken\nname: Broken")
    
    # Create a broken agent.py (SyntaxError or similar)
    (broken_agent_dir / "agent.py").write_text("this is not valid python code!")
    
    # Ensure ALERT.md doesn't exist in the current test context or is clean
    alert_file = tmp_path / "ALERT.md"
    if alert_file.exists():
        os.remove(alert_file)
    
    # Patch the current working directory or the alert path in the registry logic
    # Since registry.py will use os.path.abspath("ALERT.md"), we should change CWD
    # or patch the helper if it exists. But it doesn't exist yet!
    
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        print(f"\n[Test] Running discovery on {agents_dir}...")
        AgentRegistry.discover_plugins(str(agents_dir))
        
        # Verify if ALERT.md was created and contains the error
        assert os.path.exists("ALERT.md"), "ALERT.md was not created on load failure"
        with open("ALERT.md", "r") as f:
            content = f.read()
            assert "## [AGENT_LOAD_FAILURE]" in content
            assert "Agent: broken_agent" in content
            assert "invalid syntax" in content or "SyntaxError" in content
    finally:
        os.chdir(cwd)
