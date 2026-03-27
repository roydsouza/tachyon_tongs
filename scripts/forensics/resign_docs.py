import sys
import os
from tachyon.core.state import StateManager

def re_sign_all():
    root_dir = os.getcwd()
    docs = [
        "README.md",
        "TASKS_CLEANUP.md",
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
    
    state = StateManager()
    for doc in docs:
        path = os.path.join(root_dir, doc)
        if not os.path.exists(path):
            print(f"[!] {doc} not found, skipping.")
            continue
            
        print(f"[*] Re-signing {doc}...")
        try:
            state.integrity.sign_document(path)
            if state.integrity.verify_integrity(path):
                print(f"[+] {doc} verified.")
            else:
                print(f"[!] {doc} verification FAILED.")
        except Exception as e:
            print(f"[!] Error signing {doc}: {e}")

if __name__ == "__main__":
    re_sign_all()
