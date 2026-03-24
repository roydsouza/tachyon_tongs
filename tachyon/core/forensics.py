import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from tachyon.core.signing import IntegrityManager

class ForensicStore:
    """
    Unified PQC-Signed Forensic Ledger for Tachyon Tongs.
    Consolidates alerts, telemetry, and evolution logs into an append-only SQLite DB.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.db_path = db_path or os.path.join(root_dir, "memory", "operational", "forensics.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.integrity_manager = IntegrityManager()
        self._init_db()

    def _init_db(self):
        """Initializes the forensic schema with WAL mode enabled."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS forensic_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    signature TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON forensic_log(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON forensic_log(timestamp)")

    def log_event(
        self, 
        agent_id: str, 
        event_type: str, 
        action: str, 
        status: str, 
        details: Dict[str, Any]
    ) -> int:
        """
        Signs and appends an event to the ledger.
        """
        timestamp = datetime.now().isoformat()
        details_json = json.dumps(details)
        
        # Prepare content for signing
        # We sign a canonical string representation of the core fields
        content_to_sign = f"{timestamp}|{agent_id}|{event_type}|{action}|{status}|{details_json}"
        
        # In a real environment, we'd sign the hash of this content
        # For our substrate, we leverage the IntegrityManager's hybrid signing capability
        # NOTE: Since we are signing a string instead of a file, we use a helper or mock logic
        # For Phase 42, we store the signature as 'ed25519:...' or 'mldsa65:...'
        signature = self.integrity_manager.sign_text(content_to_sign)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO forensic_log (timestamp, agent_id, event_type, action, status, details, signature) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (timestamp, agent_id, event_type, action, status, details_json, signature)
            )
            return cursor.lastrowid

    def verify_ledger_integrity(self) -> List[int]:
        """
        Audit the entire ledger, verifying every PQC signature.
        Returns a list of IDs that failed verification.
        """
        invalid_ids = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, timestamp, agent_id, event_type, action, status, details, signature FROM forensic_log")
            for row in cursor:
                id, ts, agent, e_type, act, stat, det, sig = row
                content = f"{ts}|{agent}|{e_type}|{act}|{stat}|{det}"
                if not self.integrity_manager.verify_text_signature(content, sig):
                    invalid_ids.append(id)
        return invalid_ids

    def query_latest(self, limit: int = 10, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query recent events for the Herald display."""
        query = "SELECT * FROM forensic_log"
        params = []
        if event_type:
            query += " WHERE event_type = ?"
            params.append(event_type)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor]
