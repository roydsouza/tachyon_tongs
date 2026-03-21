"""PQC Rekey Ceremony: Generate a fresh ML-DSA-65 keypair and anchor both SK+PK."""
import oqs
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="oqs")

from tachyon.core.signing import PQC_KEY_LABEL, PQC_KEY_APPLICATION_TAG, PQC_ALGORITHM

def pqc_rekey():
    import Security
    
    print("="*60)
    print("TACHYON TONGS: PQC REKEY CEREMONY (ML-DSA-65)")
    print("="*60)
    print("This will generate a FRESH ML-DSA-65 keypair.")
    print("Both SK and PK will be anchored to the Keychain.")
    print("-" * 30)
    
    # 1. Generate fresh keypair
    with oqs.Signature(PQC_ALGORITHM) as sig:
        pk = sig.generate_keypair()
        sk = sig.export_secret_key()
        print(f"[*] Fresh ML-DSA-65 keypair generated.")
        print(f"    PK: {len(pk)} bytes, SK: {len(sk)} bytes")
        print(f"    PK fingerprint: {pk[:16].hex()}...")
    
    # 2. Anchor SK to Keychain
    sk_attrs = {
        Security.kSecClass: Security.kSecClassGenericPassword,
        Security.kSecAttrLabel: PQC_KEY_LABEL,
        Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG,
        Security.kSecValueData: sk,
        Security.kSecAttrAccessible: Security.kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
    }
    Security.SecItemDelete({Security.kSecClass: Security.kSecClassGenericPassword, Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG})
    status, _ = Security.SecItemAdd(sk_attrs, None)
    if status == 0:
        print("[✓] PQC Root SK anchored to macOS Keychain.")
    else:
        print(f"[!] SK Keychain Error: {status}")
        return
    
    # 3. Anchor PK to Keychain (companion entry)
    pk_attrs = {
        Security.kSecClass: Security.kSecClassGenericPassword,
        Security.kSecAttrLabel: PQC_KEY_LABEL + " PK",
        Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG + ".pk",
        Security.kSecValueData: pk,
        Security.kSecAttrAccessible: Security.kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
    }
    Security.SecItemDelete({Security.kSecClass: Security.kSecClassGenericPassword, Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG + ".pk"})
    pk_status, _ = Security.SecItemAdd(pk_attrs, None)
    if pk_status == 0:
        print(f"[✓] PQC Root PK ({len(pk)} bytes) anchored to macOS Keychain.")
    else:
        print(f"[!] PK Keychain Error: {pk_status}")
        return
    
    # 4. Verify roundtrip
    print("[*] Verifying signing roundtrip...")
    with oqs.Signature(PQC_ALGORITHM, sk) as signer:
        test_msg = b"pqc-rekey-verify"
        test_sig = signer.sign(test_msg)
    
    with oqs.Signature(PQC_ALGORITHM) as verifier:
        result = verifier.verify(test_msg, test_sig, pk)
        if result:
            print("[✓] PQC signing/verification roundtrip PASSED.")
        else:
            print("[!] ROUNDTRIP FAILED. Aborting.")
            return
    
    print("="*60)
    print("[✓] PQC REKEY COMPLETE. Run re-signing ceremony now.")
    print("="*60)

if __name__ == "__main__":
    pqc_rekey()
