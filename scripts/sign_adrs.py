import os
from tachyon.core.signing import IntegrityManager

def sign_all_adrs():
    im = IntegrityManager()
    adr_dir = "docs/adr"
    for filename in os.listdir(adr_dir):
        if filename.endswith(".md"):
            path = os.path.join(adr_dir, filename)
            print(f"Signing ADR: {filename}")
            im.sign_document(path)

if __name__ == "__main__":
    sign_all_adrs()
