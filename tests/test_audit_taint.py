import pytest
import sqlite3
import hashlib
import os
import tempfile

# Force test mode to bypass identity checks in BaseAgentPlugin
os.environ["TACHYON_TEST_MODE"] = "1"

from tachyon.core.state import StateManager
from tachyon.enforcement.taint import TaintPolicy
from agents.herald.agent import HeraldPlugin
from scripts.forensics.verify_chain import verify_audit_chain

# --- S-05: Merkle Audit Trail Tests ---

def test_audit_chain_integrity():
    """Verify that the Merkle chain successfully links records and detects tampering."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_audit.db")
        sm = StateManager(db_path=db_path)
        
        # 1. Log multiple events to form a chain
        sm.log_forensic_event("agent-001", "BOOT", "Substrate initialization.")
        sm.log_forensic_event("agent-001", "SCAN", "Performing security audit.")
        sm.log_forensic_event("agent-001", "ALERT", "Malicious activity detected.")
        
        # 2. Verify legitimate chain passes
        assert verify_audit_chain(db_path) is True
        
        # 3. Manually tamper with a historic record
        with sqlite3.connect(db_path) as conn:
            # Change the details of the second record
            conn.execute("UPDATE forensic_events SET details = 'REDACTED_BY_ATTACKER' WHERE id = 2")
            conn.commit()
            
        # 4. Verify tampering is detected
        assert verify_audit_chain(db_path) is False

def test_audit_chain_empty():
    """Verify empty chain is considered healthy."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "empty_audit.db")
        assert verify_audit_chain(db_path) is True

# --- S-06: Semantic Taint Tracking Tests ---

def test_taint_detection_and_redaction():
    """Verify that sensitive patterns (API keys) are redacted."""
    policy = TaintPolicy()
    
    # 1. OpenAI Key
    key = "sk-aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZ"
    payload = f"The secret key is {key}."
    assert policy.is_tainted(payload) is True
    assert "[REDACTED_SECRET]" in policy.redact_taint(payload)
    assert key not in policy.redact_taint(payload)
    
    # 2. Gemini Key
    gemini_key = "AIzaSyB-cDeFgHiJkLmNoPqRsTuVwXyZaBcDeFg"
    assert policy.is_tainted(gemini_key) is True
    assert policy.redact_taint(gemini_key) == "[REDACTED_SECRET]"

def test_herald_exfiltration_block():
    """Verify that the Herald redacts secrets before dispatching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_herald.db")
        # Initialize StateManager singleton with temp DB
        sm = StateManager(db_path=db_path)
        
        config = {"id": "herald-001"}
        herald = HeraldPlugin("herald-001", config)
        
        # Mock an event containing a secret
        secret_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef"
        event = {
            "id": "event-999",
            "topic": "STATUS_UPDATE",
            "summary": f"Relaying key: {secret_key}"
        }
        
        # Sanitize the event
        sanitized = herald._sanitize_event(event)
        
        # Assert redaction
        assert "[REDACTED_SECRET]" in sanitized["summary"]
        assert secret_key not in sanitized["summary"]
