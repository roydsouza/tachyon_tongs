import os
import hmac
import hashlib
import warnings
from datetime import datetime
from typing import Optional, Union, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# Phase 25.3: Suppress liboqs version mismatch (Using 0.15.0-dev on M5)
warnings.filterwarnings("ignore", category=UserWarning, module="oqs")

# Local substrate constants
KEY_LABEL = "Tachyon Root Key"
KEY_APPLICATION_TAG = "com.tachyon.substrate.root.v1"
PQC_KEY_LABEL = "Tachyon PQC Root"
PQC_KEY_APPLICATION_TAG = "com.tachyon.substrate.pqc.v1"
PQC_ALGORITHM = "ML-DSA-65"

class IntegrityManager:
    """
    Manages cryptographic signatures and integrity verification for Tachyon Tongs.
    Phase 25.1: Migrated from HMAC-SHA256 to hardware-backed Ed25519 signatures.
    """
    
    def __init__(self, use_hardware: bool = True):
        self.use_hardware = use_hardware
        self.hmac_key = os.environ.get("TACHYON_SECRET_KEY", "DEVELOPMENT_INSECURE_FALLBACK").encode('utf-8')
        self._private_key: Optional[ed25519.Ed25519PrivateKey] = None
        self._public_key: Optional[ed25519.Ed25519PublicKey] = None
        self._pqc_private_key_bytes: Optional[bytes] = None  # ML-DSA-65 expanded SK (4032 bytes)
        self._pqc_public_key: Optional[bytes] = None          # ML-DSA-65 public key
        
        self.root_public_key = self._load_pinned_root()
        
        # In Phase 25.2, we attempt to load the hardware-backed key.
        try:
            self._load_keys()
        except Exception as e:
            if os.environ.get("TACHYON_STRICT_MODE"):
                raise RuntimeError(f"Cryptographic failure in STRICT_MODE: {e}. Halt.")

    def _load_pinned_root(self) -> Optional[str]:
        """Retrieve the pinned Root Public Key from ROOT_MANIFEST.json."""
        import json
        manifest_path = "ROOT_MANIFEST.json"
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                data = json.load(f)
                return data.get("root_public_key")
        return None

    def _load_keys(self):
        """Load Ed25519 root key from macOS Keychain."""
        if not self.use_hardware:
            return

        try:
            import Security
            # Query for the private key in the Keychain
            query = {
                Security.kSecClass: Security.kSecClassGenericPassword,
                Security.kSecAttrLabel: KEY_LABEL,
                Security.kSecAttrAccount: KEY_APPLICATION_TAG,
                Security.kSecReturnData: True,
                Security.kSecMatchLimit: Security.kSecMatchLimitOne,
            }
            
            status, result = Security.SecItemCopyMatching(query, None)
            if status == Security.errSecSuccess:
                # Root key found in Keychain
                self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes(result))
                self._public_key = self._private_key.public_key()
                
                # Verify against pinned root (if exists)
                if self.root_public_key:
                    current_pub = self._public_key.public_bytes_raw().hex()
                    if current_pub != self.root_public_key:
                        raise RuntimeError("TRUST BREACH: Loaded Root Key does NOT match pinned Root Manifest!")
                
                # PHASE 25.3: Load PQC Key if available
                self._load_pqc_keys()
            else:
                # No key in Keychain - fallback to HMAC or raise if strict
                warnings.warn("[IntegrityManager] No Ed25519 root key found in Keychain. Falling back to HMAC.")
        except ImportError:
            # Expected on non-macOS systems
            pass
        except Exception as e:
            warnings.warn(f"[IntegrityManager] Key loading failed: {e}. Falling back to HMAC.")

    def _load_pqc_keys(self):
        """Load ML-DSA-65 expanded secret key from macOS Keychain."""
        if not self.use_hardware:
            return
            
        try:
            import Security
            import oqs
            # Load the expanded secret key (4032 bytes)
            sk_query = {
                Security.kSecClass: Security.kSecClassGenericPassword,
                Security.kSecAttrLabel: PQC_KEY_LABEL,
                Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG,
                Security.kSecReturnData: True,
                Security.kSecMatchLimit: Security.kSecMatchLimitOne,
            }
            status, result = Security.SecItemCopyMatching(sk_query, None)
            if status == Security.errSecSuccess:
                self._pqc_private_key_bytes = bytes(result)
                
                # Load the public key from a companion Keychain entry
                pk_query = {
                    Security.kSecClass: Security.kSecClassGenericPassword,
                    Security.kSecAttrLabel: PQC_KEY_LABEL + " PK",
                    Security.kSecAttrAccount: PQC_KEY_APPLICATION_TAG + ".pk",
                    Security.kSecReturnData: True,
                    Security.kSecMatchLimit: Security.kSecMatchLimitOne,
                }
                pk_status, pk_result = Security.SecItemCopyMatching(pk_query, None)
                if pk_status == Security.errSecSuccess:
                    self._pqc_public_key = bytes(pk_result)
                else:
                    # PK not stored yet — derive it by sign+verify probe
                    # This is a one-time migration path
                    warnings.warn("[IntegrityManager] PQC public key not in Keychain. Running derivation probe.")
                    with oqs.Signature(PQC_ALGORITHM, self._pqc_private_key_bytes) as sig:
                        probe_msg = b"tachyon-pk-probe"
                        probe_sig = sig.sign(probe_msg)
                        # The PK was generated during genesis and stored separately
                        # Without it, we cannot verify. Mark PQC as unavailable.
                        self._pqc_private_key_bytes = None
                        warnings.warn("[IntegrityManager] PQC public key missing. Run `tt keys pqc-store-pk` to anchor it.")
        except ImportError:
            pass  # Expected on non-macOS or if oqs not installed
        except Exception as e:
            warnings.warn(f"[IntegrityManager] PQC key loading failed: {e}")

    def derive_agent_key(self, role: str) -> ed25519.Ed25519PrivateKey:
        """Derive a per-agent Ed25519 key from the Root Key using HKDF."""
        if not self._private_key:
            raise RuntimeError("Cannot derive agent key without a loaded Root Key.")
            
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        
        # Use the root private bytes as the base for derivation
        root_bytes = self._private_key.private_bytes_raw()
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=f"tachyon-agent-{role}".encode(),
        )
        
        agent_seed = hkdf.derive(root_bytes)
        return ed25519.Ed25519PrivateKey.from_private_bytes(agent_seed)

    def sign_document(self, filepath: str, identity: str = "tachyon-substrate-v1") -> str:
        """
        Sign a file and return the hex digest.
        Phase 25.4: Implements Hybrid Signing (Ed25519 + ML-DSA-65).
        """
        if not os.path.exists(filepath):
            return ""
        with open(filepath, 'rb') as f:
            content = f.read()

        signatures = []

        # 1. Ed25519 (ECC) - Hardware Tier
        if self._private_key:
            ecc_sig = self._private_key.sign(content).hex()
            signatures.append(f"ed25519:{ecc_sig}")

        # 2. ML-DSA-65 (PQC) - Quantum Tier
        if self._pqc_private_key_bytes:
            import oqs
            with oqs.Signature(PQC_ALGORITHM, self._pqc_private_key_bytes) as signer:
                pqc_sig = signer.sign(content).hex()
                signatures.append(f"mldsa65:{pqc_sig}")

        # 3. Legacy HMAC Fallback
        if not signatures:
            hmac_sig = hmac.new(self.hmac_key, content, hashlib.sha256).hexdigest()
            signatures.append(f"hmac:{hmac_sig}")

        # Combined Signature Container
        digest = "|".join(signatures)
        sig_path = f"{filepath}.sig"
        with open(sig_path, 'w') as sf:
            sf.write(digest)
            sf.flush()
            os.fsync(sf.fileno())

        return digest

    def verify_integrity(self, filepath: str) -> bool:
        """
        Verify the Hybrid signature of a file.
        Enforces Dual-Signature mandate if PQC is established.
        """
        if not os.path.exists(filepath):
            return True

        sig_path = f"{filepath}.sig"
        if not os.path.exists(sig_path):
            raise RuntimeError(f"No detached signature found for {filepath}. Access Denied.")

        with open(sig_path, 'r') as sf:
            raw_sig = sf.read().strip()

        with open(filepath, 'rb') as f:
            content = f.read()

        sig_parts = raw_sig.split("|")
        verified_count = 0
        pqc_checked = False

        for part in sig_parts:
            if part.startswith("ed25519:"):
                # ECC Verification
                if not self._public_key:
                    raise RuntimeError("Ed25519 signature detected but no public key available.")
                sig_bytes = bytes.fromhex(part.split(":")[1])
                try:
                    self._public_key.verify(sig_bytes, content)
                    verified_count += 1
                except InvalidSignature:
                    raise RuntimeError(f"INTEGRITY COMPROMISED: Ed25519 mismatch for {filepath}!")

            elif part.startswith("mldsa65:"):
                # PQC Verification (Phase 25.3)
                pqc_checked = True
                if not self._pqc_public_key: 
                    # Skip if key not loaded (PQC is an optional integrity overlay)
                    continue
                sig_bytes = bytes.fromhex(part.split(":")[1])
                
                # NIST PQC verify: (message, signature, public_key)
                import oqs
                # Always use a fresh instance for verification to avoid state issues
                with oqs.Signature(PQC_ALGORITHM) as verifier:
                    if verifier.verify(content, sig_bytes, self._pqc_public_key):
                        verified_count += 1
                    else:
                        raise RuntimeError(f"INTEGRITY COMPROMISED: ML-DSA-65 mismatch for {filepath}!")

            elif part.startswith("hmac:"):
                # Legacy HMAC
                actual_sig = hmac.new(self.hmac_key, content, hashlib.sha256).hexdigest()
                if hmac.compare_digest(part.split(":")[1], actual_sig):
                    verified_count += 1
                else:
                    raise RuntimeError(f"INTEGRITY COMPROMISED: HMAC mismatch for {filepath}!")

        # Dual-Signature Mandate: If PQC is active, we MUST have verified both
        # This prevents a 'Strip Attack' where an attacker removes the PQC layer.
        if self._pqc_private_key_bytes and not pqc_checked:
             raise RuntimeError(f"SECURITY BREACH: PQC Signature MISSING for {filepath} in Hybrid Mode!")
        
        if verified_count == 0:
            raise RuntimeError(f"INTEGRITY FAILURE: No valid signatures for {filepath}.")
            
        return True
