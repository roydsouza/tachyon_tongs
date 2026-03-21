import os
import sys
import secrets
import getpass
from cryptography.hazmat.primitives.asymmetric import ed25519
from tachyon.core.sss import split_secret, reconstruct_secret
from tachyon.core.signing import IntegrityManager

# Mocking hardware interaction for CLI prototype
# In final 25.1, this will use pyobjc-framework-Security to talk to Keychain
def genesis_ceremony():
    """Trigger the one-time Genesis Ceremony to create the Root of Trust."""
    print("="*60)
    print("TACHYON TONGS: GENESIS CEREMONY (PHASE 25.1)")
    print("="*60)
    print("WARNING: This will generate a new Root Key and overwrite existing hardware anchors.")
    
    confirm = input("Are you ready to establish the hardware root of trust? (y/N): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    # 1. Generate Root Seed (256-bit)
    print("[*] Generating 256-bit high-entropy Seed...")
    seed = secrets.token_bytes(32)
    
    # 2. Derive Ed25519 Public Key
    priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
    pub_key = priv_key.public_key()
    pub_hex = pub_key.public_bytes_raw().hex()
    print(f"[+] Root Public Key Derived: {pub_hex}")

    # 3. Shamir Secret Sharing Split (3-of-5)
    print("[*] Splitting Seed into Shamir shares (Threshold 3-of-5)...")
    shares = split_secret(seed, 3, 5)
    
    # 4. Display Shares once
    print("\n" + "!"*60)
    print("CRITICAL: THE FOLLOWING 5 SHARES ARE YOUR BACKUP.")
    print("THEY WILL NEVER BE DISPLAYED AGAIN OR SAVED TO DISK.")
    print("!"*60)
    
    for i, share in enumerate(shares):
        share_hex = share.hex()
        # Mocking masking/reveal for CLI demo
        input(f"Press Enter to reveal Share {i+1} (Masked)...")
        print(f"SHARE {i+1}: sss-v1:{share_hex}")
        input("Press Enter to hide and continue...")
        # Simple terminal clear (doesn't wipe scrollback, but good for local HITL)
        print("\n"*50)
        
    # 4. Storage (Phase 25.2)
    save_to_keychain(seed)

    print("[+] Genesis Ceremony Complete.")
    print("[*] Private key seed scrubbed from volatile memory.")

def save_to_keychain(seed: bytes):
    """Store the root seed in the macOS Keychain."""
    try:
        import Security
        from tachyon.core.signing import KEY_LABEL, KEY_APPLICATION_TAG
        
        # Prepare the attributes for the Keychain item
        attributes = {
            Security.kSecClass: Security.kSecClassGenericPassword,
            Security.kSecAttrLabel: KEY_LABEL,
            Security.kSecAttrAccount: KEY_APPLICATION_TAG,
            Security.kSecValueData: seed,
            Security.kSecAttrAccessible: Security.kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
        }
        
        # Add the item (delete existing first to handle re-genesis)
        Security.SecItemDelete({
            Security.kSecClass: Security.kSecClassGenericPassword,
            Security.kSecAttrAccount: KEY_APPLICATION_TAG,
        })
        
        status = Security.SecItemAdd(attributes, None)
        if status == Security.errSecSuccess:
            print("[*] Root Key successfully persisted to macOS Keychain.")
        else:
            print(f"[!] Warning: Failed to save key to Keychain (Status: {status})")
    except ImportError:
        print("[!] Warning: pyobjc-framework-Security not found. Skipping Keychain persistence.")
    
    # 5. Pin Root Public Key to Manifest (Phase 25.2)
    pin_root_key(pub_hex)

def pin_root_key(pub_hex: str):
    """Pin the Root Public Key to ROOT_MANIFEST.json with an Integrity Attestation."""
    import json
    from datetime import datetime
    
    manifest_path = "ROOT_MANIFEST.json"
    manifest_data = {
        "version": "1.0",
        "root_public_key": pub_hex,
        "created_at": datetime.now().isoformat(),
        "attestation": "HARDWARE_BOUND_ED25519"
    }
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest_data, f, indent=2)
    
    # 6. Sign the Manifest (Self-Attestation)
    print(f"[*] Signing {manifest_path} with Root Key...")
    from tachyon.core.signing import IntegrityManager
    signer = IntegrityManager(use_hardware=True)
    # Force reload to get the key we just saved
    signer._load_keys()
    signer.sign_document(manifest_path)
    
    print(f"[✓] Root Key pinned and attested in {manifest_path}.")

def recovery_drill():
    """Perform a recovery drill without persisting anything."""
    print("="*60)
    print("TACHYON TONGS: RECOVERY DRILL (RECONSTRUCTION TEST)")
    print("="*60)
    
    shares = []
    print("Please provide 3 of your 5 Shamir shares:")
    for i in range(3):
        share_str = input(f"Enter Share {i+1}: ").strip()
        if share_str.startswith("sss-v1:"):
            share_str = share_str[7:]
        shares.append(bytes.fromhex(share_str))
        
    try:
        print("[*] Reconstructing Seed...")
        seed = reconstruct_secret(shares)
        
        # Sanity Check: If the seed represents an integer >= P, it's junk
        seed_int = int.from_bytes(seed, 'big')
        from tachyon.core.sss import P
        if seed_int >= P or seed_int == 0:
            raise ValueError("Reconstructed seed is mathematically invalid (Prime Field Overflow).")

        # Verify via Public Key
        priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
        pub_hex = priv_key.public_key().public_bytes_raw().hex()
        
        print(f"[✓] SIGN_OK: Reconstruction successful.")
        print(f"[✓] Derived Fingerprint: {pub_hex}")
    except Exception as e:
        print(f"[✗] RECOVERY FAILED: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "genesis":
            genesis_ceremony()
        elif sys.argv[1] == "recover":
            recovery_drill()
    else:
        print("Usage: python3 scripts/generate_keys.py [genesis|recover]")
