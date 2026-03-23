import os
import sys
import shutil
import time

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tachyon.core.state_manager import StateManager
import importlib
guardian_mod = importlib.import_module("agents.code-only.guardian.agent")
GuardianPlugin = guardian_mod.GuardianPlugin

def test_immune_end_to_end_bypass():
    print("--- [Security] Testing End-to-End Integrity Bypass Detection ---")
    
    # 1. Setup - Use a tracked file for tampering
    target_file = "EXPLOITATION_CATALOG.md"
    # Backup original for restoration
    backup_file = target_file + ".bak"
    shutil.copy(target_file, backup_file)
    print(f"[Test] Using {target_file} for integrity test.")
    
    # 2. Sign the file initially (to establish baseline)
    state = StateManager()
    state.integrity.sign_document(target_file)
    print(f"[Test] Signed {target_file}")
    
    # 3. Simulate MANIPULATION (Tamper without updating signature)
    with open(target_file, "a") as f:
        f.write("# MALICIOUS_BYPASS_INJECTION\n")
    print(f"[Test] Tampered with {target_file}")
    
    # 4. Run Guardian check
    guardian = GuardianPlugin("test-guardian", {})
    # Need to verify if the alert is emitted. 
    # Guardian's verify_substrate doesn't return True/False easily, it emits alerts via StateManager.
    print("[Test] Running Guardian integrity check...")
    guardian.execute_action("verify_substrate", {})
    
    # 5. Check ALERT.md for STATE_COMPROMISED
    time.sleep(1) # Wait for I/O
    if os.path.exists("ALERT.md"):
        with open("ALERT.md", "r") as f:
            content = f.read()
            if "STATE_COMPROMISED" in content:
                print("[SUCCESS] Guardian detected the TAMPER and alerted!")
                # RESTORE
                shutil.move(backup_file, target_file)
                state.integrity.sign_document(target_file)
            else:
                print("[FAILURE] Guardian failed to detect the bypass in ALERT.md")
                shutil.move(backup_file, target_file)
                sys.exit(1)
    else:
        print("[FAILURE] ALERT.md not found after tamper!")
        sys.exit(1)

if __name__ == "__main__":
    test_immune_end_to_end_bypass()
