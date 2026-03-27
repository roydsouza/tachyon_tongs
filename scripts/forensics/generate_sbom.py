import os
import json
import hashlib
import sqlite3
from datetime import datetime
from tachyon.core.state import StateManager

def generate_sbom():
    """Generates a simplified CycloneDX-style SBOM for Tachyon Tongs."""
    state = StateManager()
    root_dir = os.getcwd()
    sbom_path = os.path.join(root_dir, "forensics", "SBOM.json")
    
    # Ensure forensics directory exists
    os.makedirs(os.path.dirname(sbom_path), exist_ok=True)
    
    # 1. Gather dependencies from the whitelist table
    with sqlite3.connect(state.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM package_whitelist")
        packages = [dict(row) for row in cursor.fetchall()]

    # 2. Build the SBOM structure
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now().isoformat() + "Z",
            "component": {
                "name": "Tachyon Tongs Substrate",
                "version": "1.0.0",
                "type": "application"
            }
        },
        "components": []
    }

    for pkg in packages:
        sbom["components"].append({
            "name": pkg["package_name"],
            "version": pkg.get("version", "unknown"),
            "externalReferences": [
                {
                    "url": f"https://pypi.org/project/{pkg['package_name']}/",
                    "type": "distribution"
                }
            ]
        })

    # 3. Write to file
    with open(sbom_path, "w") as f:
        json.dump(sbom, f, indent=2)
    
    print(f"[+] SBOM generated at {sbom_path}")
    
    # 4. Sign the SBOM
    state.integrity.sign_document(sbom_path)
    print("[+] SBOM signed with PQC.")

if __name__ == "__main__":
    generate_sbom()
