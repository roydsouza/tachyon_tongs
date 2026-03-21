import oqs
import sys

def probe_mldsa_offset():
    alg = "ML-DSA-65"
    print(f"[*] Probing {alg} Secret Key Buffer for Public Key...")
    
    try:
        with oqs.Signature(alg) as sig:
            pub = sig.generate_keypair()
            priv = sig.export_secret_key()
            
            print(f"[✓] Pub Len: {len(pub)}")
            print(f"[✓] Priv Len: {len(priv)}")
            
            # Search for pub in priv
            if pub in priv:
                idx = priv.find(pub)
                print(f"[✓] Public Key found at offset: {idx}")
            else:
                # Some implementations store it at the end, or parts of it
                print("[!] Public Key NOT physically present as a contiguous block in the Secret Key buffer.")
                # Let's try to verify with an empty instance using the loaded priv
                with oqs.Signature(alg, priv) as sig2:
                    # Does generate_keypair() on a loaded instance return the original pub?
                    pub_gen = sig2.generate_keypair()
                    if pub_gen == pub:
                        print(f"[✓] Success: generate_keypair() on loaded instance RECONSTRUCTS the original pub key.")
                    else:
                        print(f"[!] Failure: generate_keypair() on loaded instance returns DIFFERENT pub key!")
                        print(f"    Original Pub Prefix: {pub[:16].hex()}...")
                        print(f"    Generated Pub Prefix: {pub_gen[:16].hex()}...")

    except Exception as e:
        print(f"[!] Probe Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    probe_mldsa_offset()
