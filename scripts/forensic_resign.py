import hashlib
import os
import json
import sys

# Ensure tachyon is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tachyon.core.signing import IntegrityManager

def resign_substrate():
    integrity = IntegrityManager()
    adr_dir = 'docs/adr'
    manifest_path = 'docs/adr/MANIFEST.json'
    
    adr_files_dict = {}
    
    # 1. Sign individual ADRs and Decision Ledgers
    files = sorted([f for f in os.listdir(adr_dir) if f.endswith('.md')])
    for filename in files:
        path = os.path.join(adr_dir, filename)
        
        # Use the canonical IntegrityManager to sign
        sig = integrity.sign_document(path)
        
        # Store in manifest dict (standard sha256 of the content)
        with open(path, 'rb') as f:
            adr_hash = hashlib.sha256(f.read()).hexdigest()
        
        adr_files_dict[filename] = f"sha256:{adr_hash}"
        print(f"Signed: {filename} -> {sig[:8]}...")

    # 2. Recalculate Merkle Root (Concantenated hashes of all MD files)
    all_hashes = []
    for filename in files:
        path = os.path.join(adr_dir, filename)
        with open(path, 'rb') as f:
            all_hashes.append(hashlib.sha256(f.read()).hexdigest())
    
    sorted_hashes = "".join(sorted(all_hashes))
    merkle_root = hashlib.sha256(sorted_hashes.encode()).hexdigest()
    
    # 3. Update Manifest
    manifest = {
        "adr_files": adr_files_dict,
        "merkle_root": merkle_root
    }
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nSubstrate Synchronized. Merkle Root: {merkle_root}")

if __name__ == "__main__":
    resign_substrate()
