#!/usr/bin/env python3
import os
import sys

# Ensure project root is in path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

# Force LIBOQS to find our manual dylib if needed
os.environ["OQS_LIB_DIR"] = root_dir

from tachyon.core.signing import PQC_ALGORITHM

def headless_pqc_genesis():
    print("--- 🌌 Tachyon Headless PQC Genesis (ML-DSA-65) ---")
    mem_dir = os.path.join(root_dir, "memory", "operational")
    os.makedirs(mem_dir, exist_ok=True)
    
    sk_path = os.path.join(mem_dir, "root_pqc.key")
    pk_path = os.path.join(mem_dir, "root_pqc.pk")
    
    if os.path.exists(sk_path) and os.path.exists(pk_path):
        print("[!] PQC Root Key already exists. Skipping.")
        return
        
    print(f"[*] Generating {PQC_ALGORITHM} Keypair (NIST Level 3)...")
    import oqs
    with oqs.Signature(PQC_ALGORITHM) as sig:
        pqc_pub = sig.generate_keypair()
        pqc_priv = sig.export_secret_key()
        
    with open(sk_path, "wb") as f:
        f.write(pqc_priv)
    with open(pk_path, "wb") as f:
        f.write(pqc_pub)
        
    print(f"[+] PQC Root PK Hex: {pqc_pub.hex()[:32]}...")
    print(f"[+] PQC Secret Key saved to: {sk_path}")
    print(f"[+] PQC Public Key saved to: {pk_path}")
    
    # Update manifest (we should probably add PQC PK to manifest in 25.4)
    manifest_path = os.path.join(root_dir, "ROOT_MANIFEST.json")
    if os.path.exists(manifest_path):
        import json
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        data["pqc_root_public_key"] = pqc_pub.hex()
        with open(manifest_path, 'w') as f:
            json.dump(data, f, indent=2)
        print("[✓] PQC Public Key pinned to ROOT_MANIFEST.json.")
    
    print("[✓] Headless PQC Genesis Complete.")

if __name__ == "__main__":
    headless_pqc_genesis()
