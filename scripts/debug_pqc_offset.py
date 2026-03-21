import oqs
from tachyon.core.keys.operations import get_pqc_root_key

def debug_keys():
    # 1. Get key from Keychain
    sk_expanded = get_pqc_root_key()
    if not sk_expanded:
        print("FAIL: No PQC key in Keychain")
        return
    
    print(f"SK Expanded Length: {len(sk_expanded)}")
    
    # 2. Derive PK
    sig = oqs.Signature("ML-DSA-65")
    # In OQS, we can't easily extract PK from SK without a 'keypair' call or a specific C-offset.
    # But we can sign and then verify.
    
    # 3. Test Cycle
    msg = b"test"
    signature = sig.sign(msg, sk_expanded)
    
    # The 'IntegrityManager' loads the key and extracts PK if missing.
    # Let's see if a NEW signature instance can verify it using the SAME sk (which includes pk in some OQS impls, 
    # but ML-DSA-65 expanded SK is 4032 bytes which is (PK + SK_internal)).
    
    pk_derived = sig.details['length_public_key']
    # For ML-DSA-65: PK=1952, SK=4032. 
    # The 4032 bytes IS usually the full keypair.
    
    pk = sk_expanded[:1952] # Common OQS offset: PK is often at the start
    
    verifier = oqs.Signature("ML-DSA-65")
    try:
        is_valid = verifier.verify(msg, signature, pk)
        print(f"Verification with offset[:1952]: {is_valid}")
    except Exception as e:
        print(f"Verification Error: {e}")

if __name__ == "__main__":
    debug_keys()
