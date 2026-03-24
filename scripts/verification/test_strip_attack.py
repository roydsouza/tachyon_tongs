import os
import sys
import subprocess
import time

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tachyon.core.signing import IntegrityManager

def test_strip_attack():
    print("[*] Phase 43: Testing Strip-Attack Detection (STRICT MODE)...")
    
    test_file = "scripts/verification/strip_test.txt"
    with open(test_file, "w") as f:
        f.write("Sensitive Substrate Configuration")
    
    # 1. Sign normally
    im = IntegrityManager()
    im.sign_document(test_file)
    
    # 2. Simulate Strip Attack: Remove the mldsa65 layer from the .sig
    sig_path = test_file + ".sig"
    with open(sig_path, "r") as f:
        original_sig = f.read()
    
    # Signature looks like: ed25519:xxx|mldsa65:xxx
    stripped_sig = original_sig.split("|")[0] # keep only ed25519
    with open(sig_path, "w") as f:
        f.write(stripped_sig)
    
    print(f"[*] Stripped signature: {stripped_sig[:30]}...")
    
    # 3. Verify in STRICT mode
    print("[*] Running verification with TACHYON_PQC_STRICT=1...")
    env = os.environ.copy()
    env["TACHYON_PQC_STRICT"] = "1"
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    try:
        # Run a small helper script to perform the verification
        verify_script = "scripts/verification/helper_verify.py"
        with open(verify_script, "w") as f:
            f.write(f"from tachyon.core.signing import IntegrityManager\n")
            f.write(f"im = IntegrityManager()\n")
            f.write(f"im.verify_integrity('{test_file}', enforce=True)\n")
        
        output = subprocess.check_output(["python3", verify_script], env=env, stderr=subprocess.STDOUT).decode()
        print("[!] FAILURE: Strip attack was NOT detected!")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        error_msg = e.output.decode()
        if "Strip Attack Detected in STRICT MODE" in error_msg:
            print("[+] SUCCESS: Strip attack DETECTED and substrate HALTED.")
        else:
            print(f"[!] FAILURE: Unexpected error: {error_msg}")
            sys.exit(1)
    finally:
        if os.path.exists(test_file): os.remove(test_file)
        if os.path.exists(sig_path): os.remove(sig_path)
        if os.path.exists("scripts/verification/helper_verify.py"): os.remove("scripts/verification/helper_verify.py")

if __name__ == "__main__":
    test_strip_attack()
