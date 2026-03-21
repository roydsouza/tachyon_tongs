import oqs
import sys

def test_mldsa_slicing():
    alg = "ML-DSA-65"
    print(f"[*] Testing {alg} Key Slicing...")
    
    try:
        with oqs.Signature(alg) as sig:
            # 1. Generate a real keypair
            pub_gen = sig.generate_keypair()
            # 2. Get the secret key (which contains the public key)
            priv_gen = sig.export_secret_key()
            
            pub_len = sig.details['length_public_key']
            print(f"[✓] Pub Len: {pub_len}, Priv Len: {len(priv_gen)}")
            
            # 3. Manually slice out the public key from the secret key
            pub_sliced = priv_gen[:pub_len]
            
            if pub_sliced == pub_gen:
                print("[✓] SUCCESS: Public key is the prefix of the Secret Key.")
            else:
                print("[!] FAILURE: Public key is NOT the prefix.")
                # We need to find where it is
                if pub_gen in priv_gen:
                    idx = priv_gen.find(pub_gen)
                    print(f"[!] Public key found at offset: {idx}")
                else:
                    print("[!] Public key NOT FOUND in secret key.")

            # 4. Test Verification with the sliced key
            msg = b"verify me"
            signature = sig.sign(msg)
            is_valid = sig.verify(msg, signature, pub_sliced)
            print(f"[✓] Verification with Sliced Key: {is_valid}")
            
    except Exception as e:
        print(f"[!] Slicing Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_mldsa_slicing()
