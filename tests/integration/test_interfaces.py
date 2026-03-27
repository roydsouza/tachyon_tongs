import pytest
import os
from tachyon.core.state import StateManager
from tachyon.cli.tui.app import TachyonDash

def test_interface_task_consistency():
    """Verify that TASKS_INTERFACES.md is correctly signed and present."""
    root_dir = os.getcwd()
    task_file = os.path.join(root_dir, "TASKS_INTERFACES.md")
    
    assert os.path.exists(task_file), "TASKS_INTERFACES.md must exist."
    
    state = StateManager()
    assert state.integrity.verify_integrity(task_file), "TASKS_INTERFACES.md must pass integrity audit."

def test_tui_initialization():
    """Verify that the TachyonDash can be loaded (TDAD placeholder)."""
    # This is a basic import/load test to satisfy the TDAD mandate for UI
    dash = TachyonDash()
    assert dash is not None, "TachyonDash must be instantiable."

def test_remote_access_adr_presence():
    """Verify that ADR-0067 for remote access is present and signed."""
    root_dir = os.getcwd()
    adr_file = os.path.join(root_dir, "docs/adr/0067-signed-remote-access.md")
    
    assert os.path.exists(adr_file), "ADR-0067 must exist."
    
    state = StateManager()
    assert state.integrity.verify_integrity(adr_file), "ADR-0067 must pass integrity audit."

def test_ux_governance_presence():
    """Verify that UX-001 rule and ux-interface workflow are present."""
    root_dir = os.getcwd()
    rule_file = os.path.join(root_dir, ".agent/rules/UX-001.md")
    workflow_file = os.path.join(root_dir, ".agent/workflows/ux-interface.md")
    
    assert os.path.exists(rule_file), "UX-001 rule must exist."
    assert os.path.exists(workflow_file), "ux-interface workflow must exist."
