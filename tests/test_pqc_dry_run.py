import sys
import os
import secrets
from tachyon.core.sss import split_secret, reconstruct_secret

def test_pqc_shamir_dry_run():
    print("[*] Starting PQC Shamir Dry-Run (ML-DSA-65 compatible)...")
    
    # Simulate a 64-byte PQC seed
    pqc_seed = secrets.token_bytes(64)
    print(f"[*] Generated 64-byte seed: {pqc_seed.hex()[:16]}...")
    
    # Split 3-of-5
    try:
        shares = split_secret(pqc_seed, threshold=3, total_shares=5)
        print(f"[✓] Successfully split into 5 shares.")
    except Exception as e:
        print(f"[!] Split Failure: {e}")
        sys.exit(1)
        
    # Reconstruct from 3 shares
    try:
        subset = shares[:3]
        reconstructed = reconstruct_secret(subset)
        print(f"[*] Reconstructed seed: {reconstructed.hex()[:16]}...")
        
        if reconstructed == pqc_seed:
            print("[✓] INTEGRITY VERIFIED: Original and Reconstructed seeds match.")
        else:
            print("[!] INTEGRITY FAILURE: Seeds do not match!")
            sys.exit(1)
    except Exception as e:
        print(f"[!] Reconstruction Failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_pqc_shamir_dry_run()
