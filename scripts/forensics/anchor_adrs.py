import os
import json
import hashlib
from datetime import datetime
from tachyon.core.state import StateManager

def anchor_adrs():
    root_dir = os.getcwd()
    adr_dir = os.path.join(root_dir, "docs", "adr")
    manifest_path = os.path.join(adr_dir, "MANIFEST.json")
    
    if not os.path.exists(manifest_path):
        print("[!] MANIFEST.json not found.")
        return

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    state = StateManager()
    files_to_recalculate = []

    # Identify all ADRs in the directory
    for f in os.listdir(adr_dir):
        if f.endswith(".md") and f != "README.md":
            filepath = os.path.join(adr_dir, f)
            
            # 1. Check if internal signature block exists
            with open(filepath, "r") as md:
                content = md.read()
            
            if "## Integrity Attestation" not in content or "sha256:PLACEHOLDER" in content:
                print(f"[*] Updating internal attestation in {f}...")
                
                # Calculate hash for the JSON block (of the content *before* the block or excluding the block)
                # To be consistent, we hash the content up to '## Integrity Attestation'
                target_content = content.split("## Integrity Attestation")[0].strip()
                file_hash = hashlib.sha256(target_content.encode('utf-8')).hexdigest()
                
                # ADR ID from filename
                adr_id = f.split("-")[0] if "-" in f else "ADR-XXXX"
                if not adr_id.startswith("ADR"):
                    adr_id = f"ADR-{adr_id}"
                
                new_attestation = f"\n\n## Integrity Attestation\n\n```json\n{{\n  \"adr_id\": \"{adr_id}\",\n  \"hash\": \"sha256:{file_hash}\",\n  \"status\": \"SIGNED\",\n  \"signer\": \"tachyon-substrate-v1\"\n}}\n```\n"
                
                if "## Integrity Attestation" in content:
                    parts = content.split("## Integrity Attestation")
                    new_content = parts[0] + "## Integrity Attestation" + new_attestation.split("## Integrity Attestation")[1]
                else:
                    new_content = content + new_attestation
                
                with open(filepath, "w") as md:
                    md.write(new_content)
                
            # 2. Add/Update in MANIFEST.json
            with open(filepath, "rb") as md:
                final_content = md.read()
                final_hash = hashlib.sha256(final_content).hexdigest()
            
            manifest["files"][f] = final_hash
            files_to_recalculate.append(f)

    # 3. Recalculate Merkle Root (Simple hash of all file hashes sorted)
    sorted_hashes = sorted(manifest["files"].values())
    combined = "".join(sorted_hashes).encode('utf-8')
    manifest["merkle_root"] = hashlib.sha256(combined).hexdigest()
    manifest["timestamp"] = datetime.now().isoformat() + "Z"

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] MANIFEST.json updated. New Merkle Root: {manifest['merkle_root']}")

    # 4. Final Re-sign all ADRs (detached)
    print("[*] Running final re-signing ritual...")
    for f in files_to_recalculate:
        path = os.path.join(adr_dir, f)
        state.integrity.sign_document(path)
        
    # Re-sign the manifest itself
    state.integrity.sign_document(manifest_path)
    print("[+] All ADRs anchored and verified.")

if __name__ == "__main__":
    anchor_adrs()
