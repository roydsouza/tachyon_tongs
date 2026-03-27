import os
import time
import threading
import pytest
from tachyon.core.signing import IntegrityManager

def test_pqc_race_condition_resiliency():
    """
    Simulates a race condition where verification happens 
    IMMEDIATELY after a change, before the .sig is written.
    """
    im = IntegrityManager()
    target_file = "tests/race_target.txt"
    sig_file = target_file + ".sig"
    
    # Clean state
    if os.path.exists(target_file): os.remove(target_file)
    if os.path.exists(sig_file): os.remove(sig_file)
    
    # We'll use a thread to sign the file with a artificial delay
    # to simulate a slow filesystem/controller.
    
    def delayed_signer():
        # First create the file
        with open(target_file, "w") as f:
            f.write("Race Subject Content")
            f.flush()
            os.fsync(f.fileno())
            
        # WAIT 30ms before signing (this is the "race window")
        time.sleep(0.03)
        im.sign_document(target_file)
        
    signer_thread = threading.Thread(target=delayed_signer)
    
    # Start the signer
    signer_thread.start()
    
    # IMMEDIATELY try to verify (the file might exist but not the .sig)
    # We wait a tiny bit to ensure the file is at least created
    time.sleep(0.01) 
    
    try:
        # Without retries, this would fail immediately
        # With retries (~150ms buffer), it should wait for the 30ms delay and pass
        is_valid = im.verify_integrity(target_file, enforce=False)
        assert is_valid is True, "Verification failed despite the race window being smaller than the retry buffer."
    finally:
        signer_thread.join()
        if os.path.exists(target_file): os.remove(target_file)
        if os.path.exists(sig_file): os.remove(sig_file)

def test_pqc_strict_mode_race_resiliency():
    """
    Verifies that enforce=True (strict verification) also waits and doesn't raise immediately.
    """
    im = IntegrityManager()
    target_file = "tests/race_strict_target.txt"
    sig_file = target_file + ".sig"
    
    if os.path.exists(target_file): os.remove(target_file)
    if os.path.exists(sig_file): os.remove(sig_file)

    def delayed_signer():
        with open(target_file, "w") as f:
            f.write("Strict Race Subject Content")
            f.flush()
            os.fsync(f.fileno())
        time.sleep(0.08) # 80ms delay (Stage 2 retry should catch this)
        im.sign_document(target_file)

    signer_thread = threading.Thread(target=delayed_signer)
    signer_thread.start()
    
    time.sleep(0.01)
    
    try:
        # Should NOT raise RuntimeError because it waits for the .sig to appear
        is_valid = im.verify_integrity(target_file, enforce=True)
        assert is_valid is True
    finally:
        signer_thread.join()
        if os.path.exists(target_file): os.remove(target_file)
        if os.path.exists(sig_file): os.remove(sig_file)
