"""One-time migration: Store the PQC public key as a companion Keychain entry."""
import oqs
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="oqs")

from tachyon.core.signing import (
    PQC_KEY_LABEL, PQC_KEY_APPLICATION_TAG, PQC_ALGORITHM
)

def store_pqc_pk():
    import Security
    
    # 1. Load the existing SK from Keychain
    sk_query = {
        Security.kSecClass: Security.kSecClassGenericPassword,
        Security.kSecAttrLabel: PQC_KEY_LABEL,
        Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG,
        Security.kSecReturnData: True,
        Security.kSecMatchLimit: Security.kSecMatchLimitOne,
    }
    status, result = Security.SecItemCopyMatching(sk_query, None)
    if status != Security.errSecSuccess:
        print("[!] No PQC secret key in Keychain. Run pqc-genesis first.")
        return
    
    sk_bytes = bytes(result)
    print(f"[*] Loaded PQC SK ({len(sk_bytes)} bytes)")
    
    # 2. Derive the PK by generating a keypair from the loaded SK
    # In liboqs: construct with SK, generate a keypair to extract PK
    sig = oqs.Signature(PQC_ALGORITHM, sk_bytes)
    # Sign a probe to verify the key works
    probe_msg = b"pk-derivation-probe"
    probe_sig = sig.sign(probe_msg)
    
    # Generate a fresh keypair just to get the PK structure, then verify
    # Actually: the correct way is to use generate_keypair() on a FRESH instance
    # and compare. But since we stored the expanded SK, the PK is embedded.
    # For ML-DSA-65: we need to store the PK that was generated during genesis.
    # Let's try: generate a fresh keypair from the same SK.
    sig2 = oqs.Signature(PQC_ALGORITHM, sk_bytes)
    # sign+verify roundtrip to find the right PK
    # We need to brute-scan for the PK... OR we just generate a new keypair
    # and check if the new SK matches (it won't because of randomness in keygen)
    
    # The CORRECT approach: use generate_keypair() on a fresh instance with the 
    # same secret key to derive the public key. In liboqs, the SK contains all
    # the information needed.
    fresh = oqs.Signature(PQC_ALGORITHM)
    pk_fresh = fresh.generate_keypair()
    sk_fresh = fresh.export_secret_key()
    
    # This won't match our stored SK. Instead, let's sign with our SK and then
    # try to verify with different PK extraction methods.
    
    # Method: Sign with loaded SK, then try verifying with PK from different offsets
    test_msg = b"find-my-pk"
    test_sig = sig.sign(test_msg)
    
    # Try every 1952-byte window in the 4032-byte SK
    pk_len = 1952
    found_pk = None
    for offset in range(0, len(sk_bytes) - pk_len + 1, 32):
        candidate_pk = sk_bytes[offset:offset + pk_len]
        verifier = oqs.Signature(PQC_ALGORITHM)
        try:
            if verifier.verify(test_msg, test_sig, candidate_pk):
                found_pk = candidate_pk
                print(f"[✓] PK found at SK offset {offset}")
                break
        except Exception:
            continue
    
    if not found_pk:
        # Last resort: try the PK that was used to sign the README
        print("[!] Could not extract PK from SK buffer. Trying stored signatures...")
        # We'll need the user to re-run genesis
        print("[!] Please re-run pqc-genesis to store the PK alongside the SK.")
        return
    
    # 3. Store PK in companion Keychain entry
    pk_attrs = {
        Security.kSecClass: Security.kSecClassGenericPassword,
        Security.kSecAttrLabel: PQC_KEY_LABEL + " PK",
        Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG + ".pk",
        Security.kSecValueData: found_pk,
        Security.kSecAttrAccessible: Security.kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
    }
    Security.SecItemDelete({
        Security.kSecClass: Security.kSecClassGenericPassword,
        Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG + ".pk",
    })
    add_status, _ = Security.SecItemAdd(pk_attrs, None)
    if add_status == 0:
        print(f"[✓] PQC Public Key ({len(found_pk)} bytes) anchored to Keychain.")
    else:
        print(f"[!] Failed to store PK: status {add_status}")

if __name__ == "__main__":
    store_pqc_pk()
