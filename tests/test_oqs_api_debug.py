import oqs
import sys

def test_oqs_api():
    alg = "ML-DSA-65"
    print(f"[*] Testing {alg} API...")
    
    try:
        with oqs.Signature(alg) as sig:
            print(f"[✓] Instance created.")
            print(f"[✓] Details: {sig.details}")
            
            # Generate a new keypair to see how it works
            pub = sig.generate_keypair()
            print(f"[✓] Keypair generated. Public key len: {len(pub)}")
            
            msg = b"test message"
            signature = sig.sign(msg)
            print(f"[✓] Signed. Sig len: {len(signature)}")
            
            # Test verification
            is_valid = sig.verify(msg, signature, pub)
            print(f"[✓] Verification result: {is_valid}")
            
            # Test export
            exported_pub = sig.export_public_key()
            print(f"[✓] Exported public key len: {len(exported_pub) if exported_pub else 'NONE'}")
            
    except Exception as e:
        print(f"[!] OQS Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_oqs_api()
