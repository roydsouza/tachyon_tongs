import os
import warnings
from typing import Optional, Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519

# Constants from signing.py
KEY_LABEL = "Tachyon Root Key"
KEY_APPLICATION_TAG = "com.tachyon.substrate.root.v1"
PQC_KEY_LABEL = "Tachyon PQC Root"
PQC_KEY_APPLICATION_TAG = "com.tachyon.substrate.pqc.v1"

class KeychainProvider:
    """
    Abstracts direct access to the macOS secure enclave / Keychain.
    Separates OS-level credential storage from cryptographic signing logic.
    """
    def __init__(self, use_hardware: bool = True):
        self.use_hardware = use_hardware
        self.root_public_key_hex = self._load_pinned_root()

    def _load_pinned_root(self) -> Optional[str]:
        """Retrieve the pinned Root Public Key from ROOT_MANIFEST.json."""
        import json
        # Resolve project root (tachyon/core/keys/provider.py -> root)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
        manifest_path = os.path.join(project_root, "ROOT_MANIFEST.json")
        
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    data = json.load(f)
                    return data.get("root_public_key")
            except Exception:
                pass
        return None

    def load_ed25519_key(self) -> Tuple[Optional[ed25519.Ed25519PrivateKey], Optional[ed25519.Ed25519PublicKey]]:
        """Load Ed25519 root key from macOS Keychain."""
        if not self.use_hardware:
            return None, None

        try:
            import Security
            query = {
                Security.kSecClass: Security.kSecClassGenericPassword,
                Security.kSecAttrLabel: KEY_LABEL,
                Security.kSecAttrAccount: KEY_APPLICATION_TAG,
                Security.kSecReturnData: True,
                Security.kSecMatchLimit: Security.kSecMatchLimitOne,
            }
            
            status, result = Security.SecItemCopyMatching(query, None)
            if status == Security.errSecSuccess:
                priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes(result))
                pub_key = priv_key.public_key()
                
                # Verify against pinned root
                if self.root_public_key_hex:
                    current_pub = pub_key.public_bytes_raw().hex()
                    if current_pub != self.root_public_key_hex:
                        raise RuntimeError("TRUST BREACH: Loaded Root Key does NOT match pinned Root Manifest!")
                
                return priv_key, pub_key
            else:
                warnings.warn("[KeychainProvider] No Ed25519 root key found in Keychain.")
                return None, None
        except Exception as e:
            # Phase 25.2: Headless Fallback
            root_key_path = os.environ.get("TACHYON_ROOT_KEY_PATH")
            if root_key_path and os.path.exists(root_key_path):
                try:
                    with open(root_key_path, 'rb') as f:
                        seed = f.read()
                    priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
                    return priv_key, priv_key.public_key()
                except Exception:
                    pass
            
            warnings.warn(f"[KeychainProvider] Ed25519 Key loading failed: {e}")
            return None, None

    def load_mldsa65_keys(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Load ML-DSA-65 expanded secret key (SK) and public key (PK) from macOS Keychain.
        Returns: Tuple of (sk_bytes, pk_bytes)
        """
        if not self.use_hardware:
            return None, None
            
        try:
            import Security
            # Load the expanded secret key
            sk_query = {
                Security.kSecClass: Security.kSecClassGenericPassword,
                Security.kSecAttrLabel: PQC_KEY_LABEL,
                Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG,
                Security.kSecReturnData: True,
                Security.kSecMatchLimit: Security.kSecMatchLimitOne,
            }
            sk_status, sk_result = Security.SecItemCopyMatching(sk_query, None)
            sk_bytes = bytes(sk_result) if sk_status == Security.errSecSuccess else None
            
            if sk_bytes is None:
                return None, None

            # Load the public key
            pk_query = {
                Security.kSecClass: Security.kSecClassGenericPassword,
                Security.kSecAttrLabel: PQC_KEY_LABEL + " PK",
                Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG + ".pk",
                Security.kSecReturnData: True,
                Security.kSecMatchLimit: Security.kSecMatchLimitOne,
            }
            pk_status, pk_result = Security.SecItemCopyMatching(pk_query, None)
            pk_bytes = bytes(pk_result) if pk_status == Security.errSecSuccess else None
            
            if pk_bytes is None:
                warnings.warn("[KeychainProvider] PQC public key missing. Validation disabled.")
                # We need the PK, so if it's not anchored, we fail the entire PQC load
                return None, None
                
            return sk_bytes, pk_bytes
            
        except Exception as e:
            # Phase 25.4: Headless PQC Fallback
            sk_path = os.environ.get("TACHYON_PQC_SK_PATH")
            pk_path = os.environ.get("TACHYON_PQC_PK_PATH")
            
            if sk_path and os.path.exists(sk_path) and pk_path and os.path.exists(pk_path):
                try:
                    with open(sk_path, 'rb') as f:
                        sk_bytes = f.read()
                    with open(pk_path, 'rb') as f:
                        pk_bytes = f.read()
                    return sk_bytes, pk_bytes
                except Exception:
                    pass
            
            warnings.warn(f"[KeychainProvider] PQC key loading failed: {e}")
            return None, None
