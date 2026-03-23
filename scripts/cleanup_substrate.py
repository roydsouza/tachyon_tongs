import os
import shutil
import glob

def cleanup_substrate():
    """
    Automated sanitation for Tachyon Tongs.
    Purges root-level clutter and clears the tmp/ directory.
    """
    print("--- [Hygiene] Starting Substrate Sanitation ---")
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tmp_dir = os.path.join(root_dir, "tmp")
    
    # 1. Clean Root-Level Clutter
    patterns = [
        "test_*.db*", 
        "repro_*.db*", 
        "*.log", 
        "opa_logs.txt", 
        "*.pyc",
        "tachyon_state.db",
        "*.dylib"
    ]
    
    for pattern in patterns:
        for f in glob.glob(os.path.join(root_dir, pattern)):
            try:
                if os.path.isfile(f):
                    os.remove(f)
                    print(f"[Cleanup] Removed stale file: {os.path.basename(f)}")
                elif os.path.isdir(f):
                    shutil.rmtree(f)
                    print(f"[Cleanup] Removed stale dir: {os.path.basename(f)}")
            except Exception as e:
                print(f"[Warning] Failed to remove {f}: {e}")

    # 2. Clear tmp/ directory (preserving .gitkeep)
    if os.path.exists(tmp_dir):
        for item in os.listdir(tmp_dir):
            if item == ".gitkeep":
                continue
            path = os.path.join(tmp_dir, item)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                print(f"[Cleanup] Purged tmp item: {item}")
            except Exception as e:
                print(f"[Warning] Failed to purge {item}: {e}")

    print("--- [Hygiene] Sanitation Complete. Root is PURE. ---")

if __name__ == "__main__":
    cleanup_substrate()
