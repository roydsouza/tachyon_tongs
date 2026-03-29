#!/usr/bin/env python3
"""
Tachyon Tongs: SBOM Auto-Calibration Script
Permanently fixes the SBOM Hash Drift recurring issue.

Usage:
    python3 scripts/calibrate_sbom.py           # Calibrate and update metadata/agent_hashes.json
    python3 scripts/calibrate_sbom.py --verify   # Verify current hashes without updating

This script MUST be run after ANY modification to agents/*/agent.py files.
It should be integrated into pre-commit hooks and the AC/DC workflow.
"""
import hashlib
import json
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SBOM_FILE = os.path.join(ROOT_DIR, "metadata", "agent_hashes.json")
AGENTS_DIR = os.path.join(ROOT_DIR, "agents")
SKIP_DIRS = {"_core", "__pycache__"}


def compute_hash(filepath: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def scan_agents() -> dict:
    """Scan all agent directories and compute hashes."""
    hashes = {}
    for entry in sorted(os.listdir(AGENTS_DIR)):
        if entry in SKIP_DIRS:
            continue
        agent_file = os.path.join(AGENTS_DIR, entry, "agent.py")
        if os.path.isfile(agent_file):
            relative_path = f"agents/{entry}/agent.py"
            hashes[relative_path] = compute_hash(agent_file)
    return hashes


def verify_mode():
    """Verify current hashes against SBOM without modifying."""
    if not os.path.exists(SBOM_FILE):
        print(f"[SBOM] ERROR: SBOM file not found at {SBOM_FILE}")
        sys.exit(1)

    with open(SBOM_FILE) as f:
        expected = json.load(f)

    current = scan_agents()
    violations = 0

    print(f"[SBOM] Verifying {len(current)} agents against {SBOM_FILE}...")
    for path, current_hash in sorted(current.items()):
        expected_hash = expected.get(path)
        if expected_hash is None:
            print(f"[SBOM] ✗ MISSING: {path} is not in SBOM")
            violations += 1
        elif current_hash != expected_hash:
            print(f"[SBOM] ✗ MISMATCH: {path}")
            print(f"        Expected: {expected_hash}")
            print(f"        Actual:   {current_hash}")
            violations += 1
        else:
            print(f"[SBOM] ✓ {path}")

    # Check for agents in SBOM that no longer exist
    for path in sorted(expected.keys()):
        if path not in current:
            print(f"[SBOM] ✗ STALE: {path} is in SBOM but no longer exists on disk")
            violations += 1

    if violations > 0:
        print(f"\n[SBOM] FAILED: {violations} violation(s) detected.")
        print("[SBOM] Run 'python3 scripts/calibrate_sbom.py' to recalibrate.")
        sys.exit(1)
    else:
        print(f"\n[SBOM] PASSED: All {len(current)} agent hashes verified.")
        sys.exit(0)


def calibrate_mode():
    """Regenerate SBOM from current agent files."""
    current = scan_agents()
    print(f"[SBOM] Scanning {AGENTS_DIR}...")
    
    os.makedirs(os.path.dirname(SBOM_FILE), exist_ok=True)
    with open(SBOM_FILE, "w") as f:
        json.dump(current, f, indent=2)
        f.write("\n")

    print(f"[SBOM] Written {len(current)} agent hashes to {SBOM_FILE}")
    for path, h in sorted(current.items()):
        print(f"  {path}: {h[:16]}...")
    print("[SBOM] Calibration complete. Don't forget to commit metadata/agent_hashes.json.")


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify_mode()
    else:
        calibrate_mode()
