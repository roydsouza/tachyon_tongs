"""
Tachyon Tongs: Forensic Audit Chain Verification Tool (S-05)
Traverses the forensic_events ledger and validates the Merkle linkage.
"""
import sqlite3
import hashlib
import sys
import os
from typing import Optional

def verify_audit_chain(db_path: str) -> bool:
    """
    Validates the cryptographic integrity of the forensic_events table.
    Ensures that for every record N, N.hash == H(data + N.previous_hash) 
    and N.previous_hash == (N-1).hash.
    """
    if not os.path.exists(db_path):
        print(f"[+] Database not found: {db_path} (Empty chain is healthy).")
        return True

    print(f"[*] Verifying Forensic Audit Chain: {db_path}")
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM forensic_events ORDER BY id ASC")
        rows = cursor.fetchall()
        
        if not rows:
            print("[+] Audit chain is empty (Healthy).")
            return True

        expected_previous_hash = "0" * 64
        violations = 0
        
        for i, row in enumerate(rows):
            # 1. Check Linkage
            if row['previous_hash'] != expected_previous_hash:
                print(f"[!] LINKAGE VIOLATION at ID {row['id']}: Expected prev={expected_previous_hash[:8]}, Found={row['previous_hash'][:8]}")
                violations += 1
            
            # 2. Check Data Integrity (Re-compute hash)
            raw_payload = f"{row['agent_id']}|{row['topic']}|{row['details']}|{row['timestamp']}|{row['previous_hash']}"
            computed_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()
            
            if row['hash'] != computed_hash:
                print(f"[!] DATA VIOLATION at ID {row['id']}: Computed={computed_hash[:8]}, Stored={row['hash'][:8]}")
                violations += 1
            
            # Prepare for next iteration
            expected_previous_hash = row['hash']

        if violations == 0:
            print(f"[+] Audit Chain Validated. Total Records: {len(rows)}")
            return True
        else:
            print(f"[-] Audit Chain COMPROMISED. Total Violations: {violations}")
            return False

if __name__ == "__main__":
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    default_db = os.path.join(root_dir, "intelligence", "tachyon_state.db")
    
    target_db = sys.argv[1] if len(sys.argv) > 1 else default_db
    
    success = verify_audit_chain(target_db)
    sys.exit(0 if success else 1)
