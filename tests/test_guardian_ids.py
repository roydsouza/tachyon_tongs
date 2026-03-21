"""
Test Suite: Guardian IDS (Merkle Root Integrity)
Tests the GuardianIDS substrate verification, Merkle root computation,
and ADR tamper detection.
"""
import os
import json
import hashlib
import pytest
import tempfile
import shutil
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="oqs")


@pytest.fixture
def mock_adr_dir(tmp_path):
    """Create a temporary ADR directory with test files."""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    
    # Create two mock ADR files
    (adr_dir / "0001-test.md").write_text("# ADR-0001\nTest content.\n")
    (adr_dir / "0002-test.md").write_text("# ADR-0002\nAnother test.\n")
    
    # Compute expected Merkle root
    hashes = {}
    for f in sorted(os.listdir(adr_dir)):
        if f.endswith(".md"):
            sha = hashlib.sha256((adr_dir / f).read_bytes()).hexdigest()
            hashes[f] = sha
    
    all_hashes_str = "".join(sorted(hashes.values()))
    merkle_root = hashlib.sha256(all_hashes_str.encode()).hexdigest()
    
    manifest = {
        "merkle_root": merkle_root,
        "algorithm": "sha256",
        "files": hashes
    }
    (adr_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    
    return str(adr_dir), merkle_root


class TestGuardianIDS:
    """Tests for the Guardian IDS Merkle integrity verification."""
    
    def test_merkle_root_integrity(self, mock_adr_dir):
        """Verify Merkle root computation matches manifest."""
        adr_dir, expected_root = mock_adr_dir
        from tachyon.agents.guardian_ids import GuardianIDS
        
        guardian = GuardianIDS(
            adr_dir=adr_dir,
            manifest_path=os.path.join(adr_dir, "MANIFEST.json")
        )
        report = guardian.verify_substrate()
        assert report["merkle_verification"] == "PASSED", f"Expected PASSED, got: {report}"
    
    def test_adr_tamper_detection(self, mock_adr_dir):
        """Modifying an ADR should cause Merkle root mismatch."""
        adr_dir, _ = mock_adr_dir
        from tachyon.agents.guardian_ids import GuardianIDS
        
        # Tamper with an ADR
        tampered = os.path.join(adr_dir, "0001-test.md")
        with open(tampered, 'a') as f:
            f.write("\n## INJECTED MALICIOUS CONTENT\n")
        
        guardian = GuardianIDS(
            adr_dir=adr_dir,
            manifest_path=os.path.join(adr_dir, "MANIFEST.json")
        )
        report = guardian.verify_substrate()
        assert report["merkle_verification"] == "FAILED"
        assert report["status"] == "COMPROMISED"
    
    def test_missing_manifest_vulnerable(self, tmp_path):
        """Missing MANIFEST.json should report VULNERABLE."""
        adr_dir = tmp_path / "empty_adr"
        adr_dir.mkdir()
        from tachyon.agents.guardian_ids import GuardianIDS
        
        guardian = GuardianIDS(
            adr_dir=str(adr_dir),
            manifest_path=str(adr_dir / "MANIFEST.json")
        )
        report = guardian.verify_substrate()
        assert report["status"] == "VULNERABLE"
