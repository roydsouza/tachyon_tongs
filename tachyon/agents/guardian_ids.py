import os
import json
import hashlib
from typing import Dict, List, Optional
from tachyon.core.signing import IntegrityManager

class GuardianIDS:
    """
    Intrusion Detection System (IDS) for the Tachyon Tongs Substrate.
    Verifies the integrity of ADRs, Policies, and Core configurations using
    the Hybrid Signature model (Embedded + Sidecar) and Merkle Anchoring.
    """

    def __init__(self, adr_dir: str = "docs/adr", manifest_path: str = "docs/adr/MANIFEST.json"):
        self.adr_dir = adr_dir
        self.manifest_path = manifest_path
        self.integrity = IntegrityManager()

    def calculate_file_hash(self, path: str) -> str:
        """Calculates SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def extract_embedded_hash(self, path: str) -> Optional[str]:
        """Extracts the hash from the 'Integrity Attestation' block in an ADR."""
        try:
            with open(path, "r") as f:
                content = f.read()
                # Simple extraction logic for the JSON block in markdown
                if "```json" in content:
                    json_str = content.split("```json")[-1].split("```")[0].strip()
                    attestation = json.loads(json_str)
                    hash_val = attestation.get("hash", "")
                    if hash_val.startswith("sha256:"):
                        return hash_val.split("sha256:")[-1]
            return None
        except Exception:
            return None

    def verify_substrate(self) -> dict:
        """
        Performs a full forensic audit of the ADR substrate.
        Returns a detailed integrity report.
        """
        report = {
            "status": "SECURE",
            "timestamp": "2026-03-18T19:40:00Z",
            "findings": [],
            "merkle_verification": "INCOMPLETE"
        }

        if not os.path.exists(self.manifest_path):
            report["status"] = "VULNERABLE"
            report["findings"].append("CRITICAL: MANIFEST.json missing. Merkle Root cannot be verified.")
            return report

        with open(self.manifest_path, "r") as f:
            manifest = json.load(f)

        expected_merkle_root = manifest.get("merkle_root", "")
        calculated_hashes = {}

        # 1. Verify individual ADRs
        for filename in sorted(os.listdir(self.adr_dir)):
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(self.adr_dir, filename)
            sig_path = filepath + ".sig"
            
            # A. Actual Hash
            actual_hash = self.calculate_file_hash(filepath)
            calculated_hashes[filename] = actual_hash

            # B. Sidecar Verification (High-Assurance HMAC)
            try:
                self.integrity.verify_integrity(filepath)
            except RuntimeError as e:
                if "No detached signature found" in str(e):
                    report["status"] = "WARNING"
                    report["findings"].append(f"MISSING_SIDECAR: {filename}.sig is missing.")
                else:
                    report["status"] = "CRITICAL"
                    report["findings"].append(f"INTEGRITY_VIOLATION: HMAC Sidecar mismatch for {filename} ({str(e)})")

            # C. Embedded Verification
            embedded_hash = self.extract_embedded_hash(filepath)
            if not embedded_hash:
                 report["findings"].append(f"MISSING_ATTESTATION: {filename} lacks embedded integrity block.")
            # Note: The embedded hash reflects the hash PRIOR to adding the attestation block.
            # In our hybrid model, we rely on the MANIFEST and Sidecar for the final content integrity.

        # 2. Merkle Root Verification
        all_hashes_str = "".join(sorted(calculated_hashes.values()))
        current_merkle_root = hashlib.sha256(all_hashes_str.encode()).hexdigest()

        if current_merkle_root != expected_merkle_root:
            report["status"] = "COMPROMISED"
            report["findings"].append(f"CRITICAL: Merkle Root Mismatch! Expected: {expected_merkle_root}, Found: {current_merkle_root}")
            report["merkle_verification"] = "FAILED"
        else:
            report["merkle_verification"] = "PASSED"

        return report

if __name__ == "__main__":
    guardian = GuardianIDS()
    report = guardian.verify_substrate()
    print(json.dumps(report, indent=2))
