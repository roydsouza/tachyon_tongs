import os
import json
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

class DelegationCertificateAuthority:
    """
    Issues, validates, and revokes JSON-based Delegation Certificates.
    Certificates are signed by the Hybrid PQC Root Key.
    """
    def __init__(self, integrity_manager):
        """
        Takes an IntegrityManager instance to utilize the Root Key for signing.
        """
        # Phase 44: Standardize test mode hardware usage
        use_hardware = os.environ.get("TACHYON_TEST_MODE") != "1"
        self.im = integrity_manager
        
        # Determine paths
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.mem_dir = os.path.join(root_dir, "memory", "operational")
        os.makedirs(self.mem_dir, exist_ok=True)
        self.crl_path = os.path.join(self.mem_dir, "revocation_list.json")
        self._ensure_crl_exists()
        
    def _ensure_crl_exists(self):
        if not os.path.exists(self.crl_path):
            with open(self.crl_path, "w") as f:
                json.dump({"revoked_fingerprints": {}}, f)
                
    def _get_revoked(self) -> dict:
        try:
            with open(self.crl_path, "r") as f:
                data = json.load(f)
                return data.get("revoked_fingerprints", {})
        except Exception:
            return {}

    def is_revoked(self, fingerprint: str) -> bool:
        """Check if a key fingerprint has been revoked."""
        revoked = self._get_revoked()
        return fingerprint in revoked

    def revoke_key(self, fingerprint: str, reason: str = "Key Compromise"):
        """Revokes a key by adding its fingerprint to the CRL."""
        revoked = self._get_revoked()
        revoked[fingerprint] = {
            "revocation_date": datetime.now().isoformat(),
            "reason": reason
        }
        with open(self.crl_path, "w") as f:
            json.dump({"revoked_fingerprints": revoked}, f, indent=2)

    def derive_and_issue(self, role: str, expiry_days: int = 30, save_to_disk: bool = False, allowed_actions: Optional[List[str]] = None) -> Tuple[ed25519.Ed25519PrivateKey, Dict[str, Any]]:
        """
        Derives an agent-specific Ed25519 sub-key using HKDF and issues a 
        Hybrid-Signed JSON certificate proving its legitimacy.
        Now includes 'allowed_actions' for the Watcher ACV (S-07).
        """
        if not self.im._private_key:
            raise RuntimeError("Cannot issue certificate without a loaded Root Key.")
            
        # 1. Derive the Key
        root_bytes = self.im._private_key.private_bytes_raw()
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=f"tachyon-agent-{role.lower()}".encode(),
        )
        agent_seed = hkdf.derive(root_bytes)
        agent_key = ed25519.Ed25519PrivateKey.from_private_bytes(agent_seed)
        
        # 2. Compute Public Key Fingerprint
        pub_bytes = agent_key.public_key().public_bytes_raw()
        fingerprint = hashlib.sha256(pub_bytes).hexdigest()[:16]
        
        # 3. Create JSON payload
        issue_time = datetime.now()
        expiry_time = issue_time + timedelta(days=expiry_days)
        
        # S-07: Default actions if none provided
        if not allowed_actions:
            allowed_actions = ["RESEARCH", "STATUS_CHECK", "EMIT_SIGNAL"]

        payload = {
            "version": "1.1", # Updated for allowed_actions
            "subject": {
                "role": role,
                "fingerprint": fingerprint,
                "public_key_b64": base64.b64encode(pub_bytes).decode('ascii'),
                "allowed_actions": allowed_actions
            },
            "issuer": "Tachyon_Hybrid_Root",
            "issued_at": issue_time.isoformat(),
            "expires_at": expiry_time.isoformat(),
        }
        
        # 4. Sign the JSON payload using the IntegrityManager's Root Key
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        
        signatures = []
        # Classical 
        signatures.append(f"ed25519:{self.im._private_key.sign(payload_bytes).hex()}")
        # Quantum
        if self.im._pqc_private_key_bytes:
            try:
                import oqs
                from tachyon.core.signing import PQC_ALGORITHM
                with oqs.Signature(PQC_ALGORITHM, self.im._pqc_private_key_bytes) as signer:
                    signatures.append(f"mldsa65:{signer.sign(payload_bytes).hex()}")
            except (ImportError, ModuleNotFoundError):
                # Phase 33.2: Skip PQC if missing
                pass
        
        cert = {
            "payload": payload,
            "signature": "|".join(signatures)
        }
        
        # 5. Optional persistence (Phase 25.2)
        if save_to_disk:
            keys_dir = os.path.join(self.mem_dir, "..", "keys")
            os.makedirs(keys_dir, exist_ok=True)
            cert_path = os.path.join(keys_dir, f"agent_{role.lower()}.json")
            
            # Export everything: Private Key, Fingerprint, and Certificate
            identity = {
                "private_key_b64": base64.b64encode(agent_key.private_bytes_raw()).decode('ascii'),
                "certificate": cert
            }
            with open(cert_path, "w") as f:
                json.dump(identity, f, indent=2)
            print(f"[CertAuthority] Persisted delegated identity for {role} to {cert_path}")
        
        return agent_key, cert

    def validate_certificate(self, cert: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates the certificate signature, expiration, and CRL status.
        Returns: (is_valid, reason)
        """
        payload = cert.get("payload")
        signature = cert.get("signature")
        
        if not payload or not signature:
            return False, "Malformed certificate format"
            
        # 1. Expiry Check
        try:
            expires = datetime.fromisoformat(payload["expires_at"])
            if datetime.now() > expires:
                return False, "Certificate Expired"
        except Exception:
             return False, "Invalid expiry date format"
             
        # 2. Revocation Check
        fingerprint = payload.get("subject", {}).get("fingerprint")
        if self.is_revoked(fingerprint):
            return False, f"Key revoked: {fingerprint}"
            
        # 3. Cryptographic Signature Validation
        # Write to temp file to use standard IntegrityManager verify logic
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        import tempfile
        # Phase 25.2: Lazy load to break circularity
        from tachyon.core.signing import IntegrityManager
        try:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
                f.write(payload_bytes)
                f.flush()
                path = f.name
            with open(path + ".sig", 'w') as sf:
                sf.write(signature)
                
            # Use local verify without hardware loading (self-contained verification)
            im = IntegrityManager(use_hardware=True)
            im.verify_integrity(path, enforce=True)
            # Implies signature verification succeeded without raising RuntimeError
            return True, "Certificate Valid"
        except RuntimeError as e:
            return False, f"Signature Invalid: {e}"
        finally:
            if 'path' in locals() and os.path.exists(path):
                os.unlink(path)
                sig_path = path + ".sig"
                if os.path.exists(sig_path):
                    os.unlink(sig_path)
