import oqs
import sys

def debug_mldsa_sign_verify_loop():
    alg = "ML-DSA-65"
    print(f"[*] Starting {alg} Sign-Verify Loop Debug...")
    
    try:
        # 1. Generate keypair
        with oqs.Signature(alg) as sig:
            pub = sig.generate_keypair()
            priv = sig.export_secret_key()
            print(f"[✓] Initial Keypair Generated. Pub Len: {len(pub)}, Priv Len: {len(priv)}")
            
            msg = b"tachyon-substrate-integrity-test"
            signature = sig.sign(msg)
            print(f"[✓] Message Signed. Sig Len: {len(signature)}")
            
            # 2. Verify with same instance
            v1 = sig.verify(msg, signature, pub)
            print(f"[✓] Same-instance verify: {v1}")
            
        # 3. Verify with NEW instance (loading secret key)
        with oqs.Signature(alg, priv) as sig2:
            # We must pass the public key to verify()
            v2 = sig2.verify(msg, signature, pub)
            print(f"[✓] New-instance (secret-loaded) verify: {v2}")
            
            # 4. Verify with NEW instance (no key loaded)
            with oqs.Signature(alg) as sig3:
                v3 = sig3.verify(msg, signature, pub)
                print(f"[✓] New-instance (empty) verify: {v3}")

    except Exception as e:
        print(f"[!] DEBUG ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    debug_mldsa_sign_verify_loop()
