#!/usr/bin/env python3
import os
import json
import hashlib
from tachyon.core.signing import IntegrityManager

def migrate():
    """
    Migrates legacy .sig (raw hex) signatures to v2.0 .sig.json format.
    Ensures backward compatibility during the substrate hardening transition.
    """
    im = IntegrityManager()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    print(f"🚀 Starting Signature Migration: {root_dir}")
    
    migrated_count = 0
    error_count = 0
    
    for root, _, files in os.walk(root_dir):
        # Skip certain directories
        if any(x in root for x in [".git", "__pycache__", ".pytest_cache", "venv"]):
            continue
            
        for file in files:
            if file.endswith(".sig"):
                legacy_sig_path = os.path.join(root, file)
                target_file = legacy_sig_path[:-4] # Remove .sig
                json_sig_path = target_file + ".sig.json"
                
                if os.path.exists(json_sig_path):
                    continue # Already migrated
                
                print(f"  [MIGRATE] {os.path.relpath(target_file, root_dir)}")
                
                try:
                    # 1. Read legacy signature
                    with open(legacy_sig_path, 'r') as f:
                        legacy_sig = f.read().strip()
                    
                    # 2. Read content to generate hash
                    with open(target_file, 'rb') as f:
                        content = f.read()
                    
                    file_hash = hashlib.sha256(content).hexdigest()
                    
                    # 3. Verify legacy signature first to ensure we aren't migrating a compromise
                    if not im.signer.verify(content, legacy_sig):
                        print(f"    [!] FAILURE: Legacy signature mismatch for {file}. Migration aborted for this file.")
                        error_count += 1
                        continue
                        
                    # 4. Generate V2 JSON
                    # Note: We use the existing signature to preserve the original PQC anchor!
                    sig_data = {
                        "version": "2.0",
                        "hash": f"sha256:{file_hash}",
                        "signature": legacy_sig,
                        "timestamp": "2026-03-27T16:00:00Z", # Migration timestamp
                        "algorithm": "hybrid-pqc",
                        "metadata": {
                            "migration": "v1_to_v2",
                            "original_sig": legacy_sig_path
                        }
                    }
                    
                    with open(json_sig_path, 'w') as f:
                        json.dump(sig_data, f, indent=2)
                    
                    # 5. KEEP legacy .sig for now (for transitional compatibility), 
                    # but we could delete it if we wanted to be clean.
                    # os.remove(legacy_sig_path)
                    
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"    [!] ERROR: {e}")
                    error_count += 1

    print(f"\n✅ Migration Complete.")
    print(f"  - Total Migrated: {migrated_count}")
    print(f"  - Total Errors:   {error_count}")

if __name__ == "__main__":
    migrate()
