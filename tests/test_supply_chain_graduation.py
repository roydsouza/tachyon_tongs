import os
import sqlite3
import pytest
from tachyon.enforcement.safe_fetch import SafeFetch, SecurityViolationError
from tachyon.core.state import StateManager

def reset_state_manager():
    """Forces the StateManager singleton to re-initialize."""
    StateManager._instance = None
    # We also need to unfreeze it if it was previously frozen
    if hasattr(StateManager, "__setattr__"):
        try:
            del StateManager.__setattr__
        except AttributeError:
            pass

def test_supply_chain_db_enforcement():
    """
    Verifies that SafeFetch correctly enforces the DB-backed whitelist.
    """
    reset_state_manager()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_db = os.path.join(root_dir, "tests", "tmp", "test_supply_graduation.db")
    if os.path.exists(test_db): os.remove(test_db)
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    alert_path = os.path.join(root_dir, "ALERT.md")
    
    # Backup ALERT.md
    original_alert = ""
    if os.path.exists(alert_path):
        with open(alert_path, "r") as f:
            original_alert = f.read()

    try:
        # Mock requests.post to simulate OPA allowing the request after the whitelist check passes
        import unittest.mock as mock
        with mock.patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"result": True}
            
            # 1. Setup StateManager with test DB
            os.environ["TACHYON_TEST_MODE"] = "1"
            sm = StateManager(db_path=test_db)
            
            # 2. Add 'google.com' to the whitelist
            with sqlite3.connect(test_db) as conn:
                conn.execute(
                    "INSERT INTO package_whitelist (package_name, version, added_at) VALUES (?, ?, ?)",
                    ("google.com", "v1", "now")
                )
                conn.commit()
                
            # 3. Setup SafeFetch (rego_mock=False is now default)
            fetcher = SafeFetch(agent_id="test-graduation-agent")
            
            # 4. Attempt authorized fetch (Should pass the whitelist check AND the OPA mock)
            assert fetcher._evaluate_intent("https://google.com/search") is True
            
            # 5. Attempt unauthorized fetch (Should fail and alert)
            assert fetcher._evaluate_intent("https://malicious-site.net/payload") is False
        
        # 6. Verify ALERT.md
        with open(alert_path, "r") as f:
            content = f.read()
            assert "[SUPPLY_CHAIN_VIOLATION]" in content
            assert "malicious-site.net" in content
            assert "test-graduation-agent" in content
            
    finally:
        # Cleanup
        if os.path.exists(test_db): os.remove(test_db)
        with open(alert_path, "w") as f:
            f.write(original_alert)
        os.environ.pop("TACHYON_TEST_MODE", None)

def test_whitelist_sync_logic():
    """
    Verifies that StateManager can sync from a manifest-like dictionary.
    """
    reset_state_manager()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_db = os.path.join(root_dir, "tests", "tmp", "test_sync.db")
    if os.path.exists(test_db): os.remove(test_db)
    
    try:
        sm = StateManager(db_path=test_db)
        
        # Manually trigger a pseudo-manifest check
        # (Assuming we have a manifest or can mock the file)
        manifest_data = {
            "supply_chain_whitelist": {
                "trusted-api.org": {"version": "2.0", "checksum": "sha256:123"}
            }
        }
        
        import json
        manifest_path = os.path.join(root_dir, "tests", "tmp", "test_manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f)
            
        sm.sync_whitelist_from_manifest(manifest_path)
        
        assert sm.is_package_whitelisted("trusted-api.org")
        assert not sm.is_package_whitelisted("untrusted.org")
        
    finally:
        if os.path.exists(test_db): os.remove(test_db)
        if os.path.exists("test_manifest.json"): os.remove("test_manifest.json")
