import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from src.auto_patcher import AutoPatcher

@patch('subprocess.run')
def test_autopatcher_success_creates_branch_and_patch(mock_run):
    # Mock subprocess.run to always return success (0)
    mock_run.return_value = MagicMock(returncode=0, stdout="test passed")
    
    patcher = AutoPatcher()
    
    # We pass it dummy patch files and test files
    cve_id = "CVE-TEST-999"
    patch_files = {"test_target.py": "print('patched')"}
    test_content = "def test_dummy(): assert True"
    
    res = patcher.apply_and_test(
        patch_files=patch_files,
        test_file_path="tests/test_dummy.py",
        test_content=test_content,
        cve_id=cve_id
    )
    
    # 1. Did it return pending review?
    assert res["status"] == "pending_human_approval"
    
    # 2. Did it call git checkout -b? (This is the critical branching test)
    calls = mock_run.call_args_list
    checkout_b_called = False
    git_diff_called = False
    
    for call in calls:
        if isinstance(call[0][0], list) and "checkout" in call[0][0] and "-b" in call[0][0]:
            checkout_b_called = True
            assert f"auto-patch/{cve_id}" in call[0][0][3]
        if isinstance(call[0][0], str) and "git diff main" in call[0][0]:
            git_diff_called = True
            
    assert checkout_b_called is True
    assert git_diff_called is True
    
    # 3. Did it write the pending merge doc?
    assert os.path.exists("PENDING_MERGE.md")
    
    # Clean up what we legally can
    if os.path.exists("test_target.py"): os.remove("test_target.py")
    if os.path.exists("tests/test_dummy.py"): os.remove("tests/test_dummy.py")

@patch('subprocess.run')
def test_autopatcher_failure_triggers_revert(mock_run):
    # First call is checkout -b (Success)
    # Second call is pytest (Fail)
    # Third call is git checkout main (Revert)
    # Fourth call is git branch -D (Revert)
    
    def side_effect(*args, **kwargs):
        cmd = args[0]
        if isinstance(cmd, list) and "pytest" in cmd[0]:
            return MagicMock(returncode=1, stdout="test failed")
        return MagicMock(returncode=0)
        
    mock_run.side_effect = side_effect
    
    patcher = AutoPatcher()
    
    cve_id = "CVE-TEST-FAIL"
    res = patcher.apply_and_test(
        patch_files={"test_target2.py": "print('patched')"},
        test_file_path="tests/test_dummy2.py",
        test_content="def test_fail(): assert False",
        cve_id=cve_id
    )
    
    assert res["status"] == "failure"
    
    # Check if revert was called
    calls = mock_run.call_args_list
    revert_called = False
    delete_branch_called = False
    
    for call in calls:
        if isinstance(call[0][0], list) and "checkout" in call[0][0] and "main" in call[0][0]:
            revert_called = True
        if isinstance(call[0][0], list) and "branch" in call[0][0] and "-D" in call[0][0]:
            delete_branch_called = True
            
    assert revert_called is True
    assert delete_branch_called is True
    
    if os.path.exists("test_target2.py"): os.remove("test_target2.py")
    if os.path.exists("tests/test_dummy2.py"): os.remove("tests/test_dummy2.py")
