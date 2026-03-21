import os
import json
import hashlib
from tachyon.core.signing import IntegrityManager

def update_manifest():
    adr_dir = "docs/adr"
    manifest_path = "docs/adr/MANIFEST.json"
    im = IntegrityManager()
    
    calculated_hashes = {}
    for filename in sorted(os.listdir(adr_dir)):
        if filename.endswith(".md"):
            filepath = os.path.join(adr_dir, filename)
            sha256 = hashlib.sha256()
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            calculated_hashes[filename] = sha256.hexdigest()
            print(f"Hashed: {filename}")

    # Calculate Merkle Root (Simple sorted concatenation)
    all_hashes_str = "".join(sorted(calculated_hashes.values()))
    merkle_root = hashlib.sha256(all_hashes_str.encode()).hexdigest()
    
    manifest_data = {
        "merkle_root": merkle_root,
        "algorithm": "sha256",
        "timestamp": "2026-03-21T01:10:00Z",
        "files": calculated_hashes
    }
    
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)
    
    print(f"Manifest Updated. New Merkle Root: {merkle_root}")
    
    # SEAL THE MANIFEST
    print("Sealing Manifest with Hybrid Root...")
    im.sign_document(manifest_path)
    print("Manifest Sealed.")

if __name__ == "__main__":
    update_manifest()
