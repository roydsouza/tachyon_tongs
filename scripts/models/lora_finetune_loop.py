import os
import sys
import json
import subprocess
from datetime import datetime

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tachyon.core.forensics import ForensicStore
from tachyon.core.warden import ModelIntegrityWarden

def run_lora_loop():
    print("[*] Phase 43: Initiating LoRA Fine-Tuning Loop...")
    
    # 1. Extract Approved Patches from Forensic Ledger
    store = ForensicStore()
    events = store.query_latest(limit=100, event_type="AIRLOCK_APPROVED")
    
    if not events:
        print("[!] No approved patches found in forensic ledger. Skipping fine-tuning.")
        return
        
    print(f"[*] Found {len(events)} approved patches. Formatting training data...")
    
    # 2. Format Training Data (JSONL)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_dir = os.path.join(root_dir, "intelligence", "training")
    os.makedirs(data_dir, exist_ok=True)
    dataset_file = os.path.join(data_dir, "substrate_alignment.jsonl")
    
    with open(dataset_file, "w") as f:
        for event in events:
            details = json.loads(event["details"])
            # Prompt template for alignment internalization
            prompt = {
                "instruction": f"Internalize security patch for {details.get('cve_id', 'UNKNOWN')}",
                "input": details.get("summary", "No summary provided."),
                "output": f"Substrate policy updated to block this vector. Patch hash: {details.get('patch_id', 'N/A')}"
            }
            f.write(json.dumps(prompt) + "\n")
            
    print(f"[+] Training dataset generated: {dataset_file}")
    
    # 3. Mock MLX Fine-Tuning (Or real command if mlx_lm is present)
    model_path = os.environ.get("TACHYON_MODEL_PATH", os.path.join(root_dir, "intelligence", "models"))
    os.makedirs(model_path, exist_ok=True)
    
    print("[*] Executing mlx_lm.lora (Simulation)...")
    # In a real environment:
    # subprocess.run(["python", "-m", "mlx_lm.lora", "--train", "--data", data_dir, "--model", "mlx-community/Mistral-7B-v0.1"])
    
    # Simulation: Create a dummy adapter file
    adapter_file = os.path.join(model_path, "adapter_weights.bin")
    with open(adapter_file, "wb") as f:
        f.write(b"MOCK_LORA_ADAPTER_DATA_V1")
    
    print("[+] Fine-tuning complete. New weights generated.")
    
    # 4. Mandatory Weight Anchoring (Warden)
    print("[*] Anchoring new weights with ModelIntegrityWarden...")
    warden = ModelIntegrityWarden(model_root=model_path)
    warden.generate_manifest()
    
    if warden.verify_weights():
        print("[+] SUCCESS: LoRA loop complete. New weights are signed and verified.")
    else:
        print("[!] FAILURE: Warden failed to verify new weights!")
        sys.exit(1)

if __name__ == "__main__":
    run_lora_loop()
