#!/usr/bin/env python3
import os
import sys
import secrets
from cryptography.hazmat.primitives.asymmetric import ed25519

# Ensure project root is in path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

def headless_genesis():
    print("--- 🎭 Tachyon Headless Genesis ---")
    mem_dir = os.path.join(root_dir, "memory", "keys")
    os.makedirs(mem_dir, exist_ok=True)
    
    root_key_path = os.path.join(mem_dir, "root_sk.bin")
    if os.path.exists(root_key_path):
        print("[!] Root Key already exists. Skipping.")
        return
        
    print("[*] Generating development Root Key...")
    seed = secrets.token_bytes(32)
    with open(root_key_path, "wb") as f:
        f.write(seed)
    
    priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
    pub_hex = priv_key.public_key().public_bytes_raw().hex()
    
    print(f"[+] Root Public Key: {pub_hex}")
    print(f"[+] Root Key saved to: {root_key_path}")
    
    # Update manifest
    from tachyon.core.keys.operations import pin_root_key
    pin_root_key(pub_hex)
    print("[✓] Headless Genesis Complete.")

if __name__ == "__main__":
    headless_genesis()
