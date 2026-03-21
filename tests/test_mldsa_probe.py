import oqs
import sys

def probe_mldsa_structure():
    alg = "ML-DSA-65"
    print(f"[*] Probing {alg} Internal Structure...")
    
    try:
        with oqs.Signature(alg) as sig:
            pub = sig.generate_keypair()
            priv = sig.export_secret_key()
            
            print(f"[✓] Pub Len: {len(pub)}")
            print(f"[✓] Priv Len: {len(priv)}")
            
            if pub in priv:
                idx = priv.find(pub)
                print(f"[✓] Public Key found at offset: {idx}")
            else:
                print("[!] Public Key NOT physically present in Secret Key buffer.")
                # Some implementations (like Dilithium/ML-DSA) reconstruct it or store as hash.
                # However, FIPS 204 usually includes it for performance.
                
    except Exception as e:
        print(f"[!] Probe Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    probe_mldsa_structure()
