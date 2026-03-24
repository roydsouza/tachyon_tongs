import os
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

class ModelIntegrityWarden:
    """
    Guards the integrity of local model weights (mlx_lm / LoRA).
    Generates and verifies PQC-signed manifests of weight volumes.
    """
    def __init__(self, model_root: Optional[str] = None):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.model_root = model_root or os.environ.get("TACHYON_MODEL_PATH", os.path.join(root_dir, "intelligence", "models"))
        self.manifest_path = os.path.join(self.model_root, "weights.json")
        
        from .signing import IntegrityManager
        self.integrity = IntegrityManager()

    def generate_manifest(self) -> str:
        """Scan models and generate a PQC-signed manifest of hashes."""
        if not os.path.exists(self.model_root):
             os.makedirs(self.model_root, exist_ok=True)
             
        manifest = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "weights": {}
        }
        
        for root, dirs, files in os.walk(self.model_root):
            for file in files:
                if file.endswith((".safetensors", ".bin", ".pt", ".json")) and file != "weights.json":
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, self.model_root)
                    manifest["weights"][rel_path] = self._hash_file(path)
        
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            
        # PQC-Sign the manifest itself
        return self.integrity.sign_document(self.manifest_path)

    def verify_weights(self) -> bool:
        """Verify all model weights against the PQC-signed manifest."""
        if not os.path.exists(self.manifest_path):
            print(f"[Warden] ALERT: No model weight manifest found at {self.manifest_path}!")
            return False
            
        # 1. Verify manifest signature first
        try:
            self.integrity.verify_integrity(self.manifest_path, enforce=True)
        except RuntimeError as e:
            from .state import StateManager
            StateManager().emit_alert("MODEL_COMPROMISED", f"Weight manifest signature failed: {e}")
            return False
            
        # 2. Verify individual file hashes
        with open(self.manifest_path, "r") as f:
            manifest = json.load(f)
            
        for rel_path, expected_hash in manifest.get("weights", {}).items():
            full_path = os.path.join(self.model_root, rel_path)
            if not os.path.exists(full_path):
                 print(f"[Warden] ALERT: Missing weight file: {rel_path}")
                 return False
            
            actual_hash = self._hash_file(full_path)
            if actual_hash != expected_hash:
                from .state import StateManager
                StateManager().emit_alert("MODEL_POISONED", f"Weight mismatch detected: {rel_path}")
                return False
                
        return True

    def _hash_file(self, path: str) -> str:
        """Generate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4000), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
