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
        """Load Ed25519 root key. Prefers macOS Keychain, falls back to files."""
        if self.use_hardware:
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
            except Exception:
                pass # Proceed to fallback

        return self._load_from_files()

    def _load_from_files(self, error: Optional[Exception] = None) -> Tuple[Optional[ed25519.Ed25519PrivateKey], Optional[ed25519.Ed25519PublicKey]]:
        """Headless Fallback: Load from OS Environment or memory/keys/."""
        try:
            root_key_path = os.environ.get("TACHYON_ROOT_KEY_PATH")
            if not root_key_path:
                this_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
                root_key_path = os.path.join(project_root, "memory", "keys", "root_sk.bin")

            if os.path.exists(root_key_path):
                with open(root_key_path, 'rb') as f:
                    seed = f.read()
                priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
                return priv_key, priv_key.public_key()
        except Exception:
            pass

        headless = os.environ.get("TACHYON_HEADLESS") == "1" or os.environ.get("TACHYON_TEST_MODE") == "1"
        is_strict = os.environ.get("TACHYON_STRICT_MODE") == "1"
        
        if not is_strict and headless:
             return None, None
             
        if error:
            warnings.warn(f"[KeychainProvider] Ed25519 Key loading failed: {error}")
        return None, None

    def load_mldsa65_keys(self) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Load ML-DSA-65 keys. Prefers macOS Keychain, falls back to files.
        """
        if self.use_hardware:
            try:
                import Security
                sk_query = {
                    Security.kSecClass: Security.kSecClassGenericPassword,
                    Security.kSecAttrLabel: PQC_KEY_LABEL,
                    Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG,
                    Security.kSecReturnData: True,
                    Security.kSecMatchLimit: Security.kSecMatchLimitOne,
                }
                sk_status, sk_result = Security.SecItemCopyMatching(sk_query, None)
                if sk_status == Security.errSecSuccess:
                    sk_bytes = bytes(sk_result)
                    
                    pk_query = {
                        Security.kSecClass: Security.kSecClassGenericPassword,
                        Security.kSecAttrLabel: PQC_KEY_LABEL + " PK",
                        Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG + ".pk",
                        Security.kSecReturnData: True,
                        Security.kSecMatchLimit: Security.kSecMatchLimitOne,
                    }
                    pk_status, pk_result = Security.SecItemCopyMatching(pk_query, None)
                    if pk_status == Security.errSecSuccess:
                        pk_bytes = bytes(pk_result)
                        return sk_bytes, pk_bytes
            except Exception:
                pass # Proceed to fallback

        return self._load_pqc_from_files()

    def _load_pqc_from_files(self, error: Optional[Exception] = None) -> Tuple[Optional[bytes], Optional[bytes]]:
        """Headless PQC Fallback: Load from OS Environment or memory/keys/."""
        try:
            sk_path = os.environ.get("TACHYON_PQC_SK_PATH")
            pk_path = os.environ.get("TACHYON_PQC_PK_PATH")
            
            if not sk_path:
                this_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
                sk_path = os.path.join(project_root, "memory", "keys", "pqc_sk.bin")
                pk_path = os.path.join(project_root, "memory", "keys", "pqc_pk.bin")

            if sk_path and os.path.exists(sk_path) and pk_path and os.path.exists(pk_path):
                with open(sk_path, 'rb') as f:
                    sk_bytes = f.read()
                with open(pk_path, 'rb') as f:
                    pk_bytes = f.read()
                return sk_bytes, pk_bytes
        except Exception:
            pass
        
        headless = os.environ.get("TACHYON_HEADLESS") == "1" or os.environ.get("TACHYON_TEST_MODE") == "1"
        is_strict = os.environ.get("TACHYON_STRICT_MODE") == "1"
        
        if not is_strict and headless:
             return None, None

        if error:
            warnings.warn(f"[KeychainProvider] PQC key loading failed: {error}")
        return None, None
