import os
import time
import pytest
from tachyon.core.state import StateManager
from agents.guardian.agent import GuardianPlugin

def test_mutant_lock_alert_suppression():
    """
    Verifies that the Mutant Lock correctly suppresses alerts during an integrity violation.
    """
    state = StateManager()
    guardian = GuardianPlugin("guardian-test", {})
    
    # 1. Identify a tracked file to 'tamper' with
    # We'll use a temporary file for safety if possible, or just a known file with a fake .sig
    target_file = "README.md"
    sig_file = target_file + ".sig"
    
    # Backup real sig if exists
    sig_backup = None
    if os.path.exists(sig_file):
        with open(sig_file, "r") as f:
            sig_backup = f.read()
            
    try:
        # Create a mismatch by writing a fake signature
        with open(sig_file, "w") as f:
            f.write("INVALID_SIGNATURE_FOR_TESTING")
            
        # Verify that without a lock, it fails
        result_no_lock = guardian.execute_action("verify_file", {"filepath": target_file})
        assert result_no_lock["status"] == "FAILURE"
        
        # Verify that with a lock, it is suppressed (Status WARNING)
        lock_id = state.acquire_mutant_lock("guardian-test", "Testing Mutant Lock Suppression")
        assert lock_id != ""
        
        try:
            result_with_lock = guardian.execute_action("verify_file", {"filepath": target_file})
            assert result_with_lock["status"] == "WARNING"
            assert result_with_lock["authorized_mutation"] is True
            assert "Suppression engaged" in result_with_lock["message"]
        finally:
            state.release_mutant_lock(lock_id)
            
        # Verify that after release, it fails again
        result_after_release = guardian.execute_action("verify_file", {"filepath": target_file})
        assert result_after_release["status"] == "FAILURE"

    finally:
        # Restore original signature
        if sig_backup:
            with open(sig_file, "w") as f:
                f.write(sig_backup)
        else:
            if os.path.exists(sig_file):
                os.remove(sig_file)

def test_mutant_lock_substrate_sweep_suppression():
    """
    Verifies that verify_substrate respects the mutant lock.
    """
    state = StateManager()
    guardian = GuardianPlugin("guardian-test", {})
    
    # Create a mismatch in a tracked file
    target_file = "README.md"
    sig_file = target_file + ".sig"
    
    sig_backup = None
    if os.path.exists(sig_file):
        with open(sig_file, "r") as f:
            sig_backup = f.read()
            
    try:
        # Create a mismatch
        with open(sig_file, "w") as f:
            f.write("INVALID_SIGNATURE_FOR_TESTING")
            
        # Acquire lock
        lock_id = state.acquire_mutant_lock("guardian-test", "Testing Sweep Suppression")
        
        try:
            # Sweep should return WARNING instead of FAILURE
            result = guardian.execute_action("verify_substrate", {})
            assert result["status"] == "WARNING"
            assert result["authorized_mutation"] is True
            assert any("README.md" in v for v in result["violations"])
        finally:
            state.release_mutant_lock(lock_id)
            
    finally:
        if sig_backup:
            with open(sig_file, "w") as f:
                f.write(sig_backup)
        else:
            if os.path.exists(sig_file):
                os.remove(sig_file)
