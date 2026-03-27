import sys
import os
from tachyon.core.state import StateManager

def sign_file(state, path):
    root_dir = os.getcwd()
    # Normalize path if it's absolute
    if not os.path.isabs(path):
        path = os.path.join(root_dir, path)
        
    if not os.path.exists(path):
        print(f"[!] {path} not found, skipping.")
        return
    
    # Use relative path for display if possible
    display_path = os.path.relpath(path, root_dir)
    print(f"[*] Re-signing {display_path}...")
    try:
        # Check if it's a signed file or needs initialization
        # The IntegrityManager handles this internally
        state.integrity.sign_document(path)
        if state.integrity.verify_integrity(path):
            print(f"[+] {display_path} verified.")
        else:
            print(f"[!] {display_path} verification FAILED.")
    except Exception as e:
        print(f"[!] Error signing {display_path}: {e}")

def re_sign_all():
    root_dir = os.getcwd()
    state = StateManager()
    
    # Support CLI arguments for specific files
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            sign_file(state, arg)
        return

    docs = [
        "README.md",
        "TASKS_CLEANUP.md",
        "TASKS_INTERFACES.md",
        "docs/ARCHITECTURE.md",
        "docs/WHITEPAPER.md",
        "docs/THREAT_MODEL.md"
    ]
    
    # Phase 43: Dynamically include all ADRs
    adr_dir = os.path.join(root_dir, "docs", "adr")
    if os.path.exists(adr_dir):
        for f in os.listdir(adr_dir):
            if f.endswith(".md"):
                docs.append(os.path.join("docs", "adr", f))
    
    for doc in docs:
        sign_file(state, doc)

if __name__ == "__main__":
    re_sign_all()
