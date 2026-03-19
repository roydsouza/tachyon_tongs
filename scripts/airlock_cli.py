#!/usr/bin/env python3
import os
import json
import sys
import argparse
import shutil
import datetime

# Ensure tachyon is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tachyon.core.state import StateManager

AIRLOCK_DIR = "/tmp/tachyon_airlock"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def list_patches():
    if not os.path.exists(AIRLOCK_DIR):
        print(f"[Airlock] Directory {AIRLOCK_DIR} does not exist. No pending patches.")
        return []
    
    patches = [f for f in os.listdir(AIRLOCK_DIR) if f.endswith(".json")]
    if not patches:
        print("[Airlock] No pending patches in staging.")
        return []
    
    print(f"\n--- 📦 Pending Patches in Airlock ({len(patches)}) ---")
    for p in patches:
        created = datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(AIRLOCK_DIR, p)))
        print(f"- {p.replace('.json', '')} (Staged: {created.strftime('%Y-%m-%d %H:%M:%S')})")
    print("-" * 40)
    return patches

def inspect_patch(patch_id):
    path = os.path.join(AIRLOCK_DIR, f"{patch_id}.json")
    if not os.path.exists(path):
        print(f"[Error] Patch {patch_id} not found.")
        return
    
    with open(path, "r") as f:
        data = json.load(f)
    
    print(f"\n--- 🔍 Inspecting: {patch_id} ---")
    print(f"CVE ID: {data.get('cve_id', 'N/A')}")
    print(f"Description: {data.get('description', 'N/A')}")
    # Proposed Changes
    patch_files = data.get("patch_files", [])
    if isinstance(patch_files, dict):
        # Convert dict to list of dicts for processing
        patch_files = [{"file": k, "content": v} for k, v in patch_files.items()]

    for file_patch in patch_files:
        print(f"\nTarget File: {file_patch.get('file')}")
        print("Proposed Content:")
        print("-" * 20)
        print(file_patch.get("content"))
        print("-" * 20)

def approve_patch(patch_id):
    path = os.path.join(AIRLOCK_DIR, f"{patch_id}.json")
    if not os.path.exists(path):
        print(f"[Error] Patch {patch_id} not found.")
        return
    
    with open(path, "r") as f:
        data = json.load(f)
    
    print(f"[Airlock] Approving and applying {patch_id}...")
    
    patch_files = data.get("patch_files", [])
    if isinstance(patch_files, dict):
        patch_files = [{"file": k, "content": v} for k, v in patch_files.items()]

    for file_patch in patch_files:
        target_path = os.path.join(ROOT_DIR, file_patch.get("file"))
        
        # Backup existing
        if os.path.exists(target_path):
            shutil.copy2(target_path, f"{target_path}.bak")
        
        # Write new content
        with open(target_path, "w") as f:
            f.write(file_patch.get("content"))
        print(f"[Approved] Applied changes to {file_patch.get('file')}")

    # Re-sign the state if necessary
    sm = StateManager()
    catalog_path = os.path.join(ROOT_DIR, "EXPLOITATION_CATALOG.md")
    sm.integrity.sign_document(catalog_path)
    print(f"[Approved] Re-signed {catalog_path}")

    # Cleanup
    os.remove(path)
    print(f"[Airlock] Purged {patch_id} from staging.")
    
    sm.emit_alert("PATCH_APPROVED", f"Human-in-the-loop approved and applied patch for {patch_id}.")

def deny_patch(patch_id):
    path = os.path.join(AIRLOCK_DIR, f"{patch_id}.json")
    if not os.path.exists(path):
        print(f"[Error] Patch {patch_id} not found.")
        return
    
    os.remove(path)
    print(f"[Airlock] Denied and purged {patch_id} from staging.")
    sm = StateManager()
    sm.emit_alert("PATCH_DENIED", f"Human-in-the-loop rejected patch for {patch_id}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tachyon Tongs Airlock Control CLI")
    parser.add_argument("--list", action="store_true", help="List all pending patches")
    parser.add_argument("--inspect", type=str, help="Inspect a specific patch by ID")
    parser.add_argument("--approve", type=str, help="Approve and apply a patch")
    parser.add_argument("--deny", type=str, help="Deny and discard a patch")
    
    args = parser.parse_args()
    
    if args.list:
        list_patches()
    elif args.inspect:
        inspect_patch(args.inspect)
    elif args.approve:
        approve_patch(args.approve)
    elif args.deny:
        deny_patch(args.deny)
    else:
        parser.print_help()
