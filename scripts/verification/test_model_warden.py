import os
import sys
import time

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tachyon.core.warden import ModelIntegrityWarden

def test_warden():
    print("[*] Phase 43: Testing ModelIntegrityWarden...")
    
    # 1. Setup dummy model dir
    model_dir = "scripts/verification/mock_model"
    os.makedirs(model_dir, exist_ok=True)
    weight_file = os.path.join(model_dir, "adapter_model.bin")
    with open(weight_file, "wb") as f:
        f.write(b"REAL_WEIGHTS_DATA_001")
        
    warden = ModelIntegrityWarden(model_root=model_dir)
    
    # 2. Generate Manifest
    print("[*] Generating signed weight manifest...")
    warden.generate_manifest()
    
    # 3. Initial Verification
    if warden.verify_weights():
        print("[+] Initial model integrity VERIFIED.")
    else:
        print("[!] Initial verification FAILED.")
        sys.exit(1)
        
    # 4. Simulate Poisoning: Modify weights
    print("[*] Simulating out-of-band weight poisoning...")
    with open(weight_file, "wb") as f:
        f.write(b"MALICIOUS_WEIGHTS_DATA_666")
        
    # 5. Detect Poisoning
    if not warden.verify_weights():
        print("[+] SUCCESS: Model poisoning DETECTED by Warden.")
    else:
        print("[!] FAILURE: Poisoned weights were NOT detected!")
        sys.exit(1)
        
    # Clean up
    import shutil
    shutil.rmtree(model_dir)

if __name__ == "__main__":
    test_warden()
