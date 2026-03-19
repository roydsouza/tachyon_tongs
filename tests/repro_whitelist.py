import pytest
import sqlite3
import os
from tachyon.core.state import StateManager

def test_is_package_whitelisted_blocks_unknown():
    # Ensure a clean state for testing or use a temporary DB
    sm = StateManager(db_path="test_whitelist.db")
    
    # Should block unknown package
    assert not sm.is_package_whitelisted("malicious-pkg")
    
    # Add an approved package to the catalog
    with sqlite3.connect("test_whitelist.db") as conn:
        conn.execute(
            "INSERT OR REPLACE INTO exploitation_catalog (cve_id, relevance_class) VALUES (?, ?)",
            ("safe-pkg", "APPROVED")
        )
        conn.commit()
    
    # Should allow approved package
    assert sm.is_package_whitelisted("safe-pkg")
    
    # Cleanup
    if os.path.exists("test_whitelist.db"):
        os.remove("test_whitelist.db")
        if os.path.exists("test_whitelist.db-wal"):
            os.remove("test_whitelist.db-wal")
        if os.path.exists("test_whitelist.db-shm"):
            os.remove("test_whitelist.db-shm")
