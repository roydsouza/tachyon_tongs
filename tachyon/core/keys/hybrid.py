import os
import hmac
import hashlib
import warnings
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# Local substrate constants
PQC_ALGORITHM = "ML-DSA-65"

class HybridSigner:
    """
    Performs purely cryptographic operations (Ed25519 + ML-DSA-65 + HMAC signatures).
    Contains no Keychain or storage logic, ensuring it can be unit tested in isolation.
    """
    def __init__(
        self, 
        ed25519_sk: Optional[ed25519.Ed25519PrivateKey] = None,
        ed25519_pk: Optional[ed25519.Ed25519PublicKey] = None,
        mldsa65_sk: Optional[bytes] = None,
        mldsa65_pk: Optional[bytes] = None,
        hmac_key: Optional[bytes] = None
    ):
        self._private_key = ed25519_sk
        self._public_key = ed25519_pk
        self._pqc_private_key_bytes = mldsa65_sk
        self._pqc_public_key = mldsa65_pk
        self.hmac_key = hmac_key or b"DEVELOPMENT_INSECURE_FALLBACK"

    def sign(self, content: bytes) -> str:
        """
        Signs the content using all available cryptographic algorithms.
        Returns a formatted signature digest string (e.g., `ed25519:xxxx|mldsa65:xxxx|hmac:xxxx`).
        """
        signatures = []

        # 1. Ed25519 (Classical Tier)
        if self._private_key:
            ed_sig = self._private_key.sign(content).hex()
            signatures.append(f"ed25519:{ed_sig}")

        # 2. ML-DSA-65 (Quantum Tier)
        if self._pqc_private_key_bytes:
            try:
                import oqs
                with oqs.Signature(PQC_ALGORITHM, self._pqc_private_key_bytes) as signer:
                    pqc_sig = signer.sign(content).hex()
                    signatures.append(f"mldsa65:{pqc_sig}")
            except ImportError:
                 warnings.warn("[HybridSigner] liboqs not installed. PQC signing skipped.")

        # 3. Legacy HMAC Fallback
        if not self._private_key and not self._pqc_private_key_bytes:
            sig = hmac.new(self.hmac_key, content, hashlib.sha256).hexdigest()
            signatures.append(f"hmac:{sig}")

        return "|".join(signatures)

    def verify(self, content: bytes, detached_signature: str) -> bool:
        """
        Verifies the content against the detached signature string.
        Enforces Dual-Signature mandate if PQC Keys are loaded.
        """
        parts = detached_signature.strip().split("|")
        
        has_ed = False
        has_pqc = False
        has_hmac = False
        
        for part in parts:
            if ":" not in part:
                 continue
                 
            alg, sig_hex = part.split(":", 1)
            sig_bytes = bytes.fromhex(sig_hex)
            
            if alg == "ed25519":
                if not self._public_key:
                    raise RuntimeError("Verification failed: Signature contains Ed25519, but no Root Public Key is loaded.")
                try:
                    self._public_key.verify(sig_bytes, content)
                    has_ed = True
                except InvalidSignature:
                    raise RuntimeError("INTEGRITY COMPROMISED: Ed25519 Signature mismatch!")
                    
            elif alg == "mldsa65":
                if not self._pqc_public_key:
                     warnings.warn("Signature contains PQC component, but no PQC Public Key loaded to verify.")
                     continue
                try:
                    import oqs
                    with oqs.Signature(PQC_ALGORITHM) as verifier:
                        is_valid = verifier.verify(content, sig_bytes, self._pqc_public_key)
                        if not is_valid:
                            raise RuntimeError("INTEGRITY COMPROMISED: PQC Signature mismatch!")
                        has_pqc = True
                except ImportError:
                    warnings.warn("Signature contains PQC component, but liboqs is not installed.")
                    
            elif alg == "hmac":
                expected = hmac.new(self.hmac_key, content, hashlib.sha256).hexdigest()
                if sig_hex != expected:
                    raise RuntimeError("INTEGRITY COMPROMISED: HMAC mismatch!")
                has_hmac = True

        # Threat Mitigation: Strip Detection
        if self._pqc_private_key_bytes and not has_pqc:
            if has_ed:
                raise RuntimeError("INTEGRITY COMPROMISED: PQC Signature MISSING (Strip Attack Detected).")
                
        if self._private_key and not has_ed:
             raise RuntimeError("INTEGRITY COMPROMISED: Ed25519 Signature MISSING.")

        if not has_ed and not has_pqc and not has_hmac:
            raise RuntimeError("No recognized signature algorithms found in manifest.")
            
        return True
