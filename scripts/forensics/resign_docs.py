import sys
import os
import glob
from tachyon.core.state import StateManager

def migrate_and_sign(state, path):
    root_dir = os.getcwd()
    if not os.path.isabs(path):
        path = os.path.join(root_dir, path)
        
    if not os.path.exists(path):
        return
    
    display_path = os.path.relpath(path, root_dir)
    
    # 1. Clean up legacy V1 signatures
    legacy_sig = path + ".sig"
    if os.path.exists(legacy_sig):
        os.remove(legacy_sig)
        
    # 2. Re-sign with V2 Structured Metadata
    print(f"[*] Migrating {display_path} to V2...")
    try:
        state.integrity.sign_document(path)
        if state.integrity.verify_integrity(path):
            print(f"[+] {display_path} verified (V2).")
        else:
            print(f"[!] {display_path} verification FAILED.")
    except Exception as e:
        print(f"[!] Error signing {display_path}: {e}")

def run_global_migration():
    root_dir = os.getcwd()
    state = StateManager()
    
    # 1. Manual over-ride via CLI
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            migrate_and_sign(state, arg)
        return

    # 2. Comprehensive recursive scan (Excluding venv and .git)
    patterns = ["**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"]
    exclude_dirs = [".git", "venv", ".venv", "__pycache__", "node_modules", ".gemini"]

    print("[*] Starting Global Forensic Migration (V1 -> V2)...")
    
    for pattern in patterns:
        for fpath in glob.iglob(os.path.join(root_dir, pattern), recursive=True):
            # Skip excluded dirs
            skip = False
            for d in exclude_dirs:
                if d in fpath:
                    skip = True
                    break
            if skip: continue
            
            # Skip the manifest itself and root manifest
            if fpath.endswith("ROOT_MANIFEST.json") or fpath.endswith("manifest.json"):
                continue
                
            migrate_and_sign(state, fpath)

if __name__ == "__main__":
    run_global_migration()
