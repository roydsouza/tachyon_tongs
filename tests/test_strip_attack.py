import os
import sys
import json

import importlib.util

# Add root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

# Import Guardian via importlib since 'code-only' has a hyphen
guardian_path = os.path.join(root_dir, "agents", "code-only", "guardian", "agent.py")
spec = importlib.util.spec_from_file_location("guardian_agent", guardian_path)
guardian_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guardian_module)
GuardianPlugin = guardian_module.GuardianPlugin

from tachyon.core.signing import IntegrityManager
from tachyon.core.state_manager import StateManager

def test_strip_attack():
    print("--- [Security] Starting Strip Attack Canary Test ---")
    
    # 1. Setup - Create a signed file
    target_file = "tmp/canary_file.txt"
    os.makedirs("tmp", exist_ok=True)
    with open(target_file, "w") as f:
        f.write("Sensitive Substrate Content")
    
    im = IntegrityManager(use_hardware=False)
    # Generate mock keys for the session if not present
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from tachyon.core.keys.hybrid import HybridSigner
    root_private = ed25519.Ed25519PrivateKey.generate()
    root_public = root_private.public_key()
    im._private_key = root_private
    im._public_key = root_public
    im.signer = HybridSigner(ed25519_sk=root_private, ed25519_pk=root_public)
    
    print("[Test] Signing canary file...")
    im.sign_document(target_file)
    
    # Verify it works normally
    if not im.verify_integrity(target_file):
        print("[Error] Initial signature verification failed.")
        return
    
    # 2. PERFORM STRIP ATTACK (Delete the signature)
    sig_path = target_file + ".sig"
    print(f"[Test] Performing Strip Attack deleting {sig_path}...")
    os.remove(sig_path)
    
    # 3. RUN GUARDIAN VERIFICATION
    print("[Test] Running Guardian verification...")
    guardian = GuardianPlugin(agent_id="g-001", config={"quarantine_mode": False})
    # Inject our im with mock keys to the guardian so it doesn't fail on key load
    guardian.integrity_manager = im
    
    result = guardian.execute_action("verify_file", {"filepath": target_file})
    print(f"[Test] Guardian Result: {result['status']} - {result.get('message', 'No message')}")
    
    # 4. VERIFY ALERT EMISSION
    # StateManager should have received an INTEGRITY_VIOLATION if we were in strict mode,
    # but Guardian returns FAILURE/ERROR status.
    
    if result["status"] == "FAILURE":
        print("[SUCCESS] Guardian caught the Strip Attack!")
    else:
        print(f"[FAILURE] Guardian failed to catch the Strip Attack. Status: {result['status']}")
        sys.exit(1)

if __name__ == "__main__":
    test_strip_attack()
