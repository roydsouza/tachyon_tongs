import sqlite3
import json
import os
import threading
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
        self._lock = threading.Lock()
        self._conn = None
        self.integrity_manager = IntegrityManager()
        self._init_db()

    def _init_db(self):
        """Initializes the forensic schema with WAL mode enabled."""
        with self._get_conn() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS forensic_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT DEFAULT 'internal',
                    details TEXT,
                    signature TEXT NOT NULL
                )
            """)
            # Migration: Add 'source' column if it doesn't exist
            try:
                conn.execute("ALTER TABLE forensic_log ADD COLUMN source TEXT DEFAULT 'internal'")
            except sqlite3.OperationalError:
                pass # Column already exists
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON forensic_log(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON forensic_log(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON forensic_log(agent_id)")

    def _get_conn(self):
        """Returns a thread-safe persistent connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def log_event(
        self, 
        agent_id: str, 
        event_type: str, 
        action: str, 
        status: str, 
        details: Dict[str, Any],
        source: str = "internal"
    ) -> int:
        """
        Signs and appends an event to the ledger.
        """
        timestamp = datetime.now().isoformat()
        details_json = json.dumps(details)
        
        # Prepare content for signing
        # We sign a canonical string representation of the core fields
        content_to_sign = f"{timestamp}|{agent_id}|{event_type}|{action}|{status}|{source}|{details_json}"
        
        # In a real environment, we'd sign the hash of this content
        # For our substrate, we leverage the IntegrityManager's hybrid signing capability
        # NOTE: Since we are signing a string instead of a file, we use a helper or mock logic
        # For Phase 42, we store the signature as 'ed25519:...' or 'mldsa65:...'
        signature = self.integrity_manager.sign_text(content_to_sign)
        
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(
                "INSERT INTO forensic_log (timestamp, agent_id, event_type, action, status, source, details, signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (timestamp, agent_id, event_type, action, status, source, details_json, signature)
            )
            conn.commit()
            return cursor.lastrowid

    def verify_ledger_integrity(self) -> List[int]:
        """
        Audit the entire ledger, verifying every PQC signature.
        Returns a list of IDs that failed verification.
        """
        invalid_ids = []
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute("SELECT id, timestamp, agent_id, event_type, action, status, source, details, signature FROM forensic_log")
            for row in cursor:
                id, ts, agent, e_type, act, stat, src, det, sig = row
                content = f"{ts}|{agent}|{e_type}|{act}|{stat}|{src}|{det}"
                if not self.integrity_manager.verify_text_signature(content, sig):
                    invalid_ids.append(id)
        return invalid_ids

    def query_latest(self, limit: int = 10, event_type: Optional[str] = None, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query recent events with optional filtering."""
        query = "SELECT * FROM forensic_log"
        conditions = []
        params = []
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        if agent_id:
            conditions.append("agent_id = ?")
            params.append(agent_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(query, params)
            results = []
            for row in cursor:
                d = dict(row)
                if d.get("details"):
                    try:
                        d["details"] = json.loads(d["details"])
                    except Exception:
                        pass
                results.append(d)
            return results

    def query_after(self, last_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Query events with ID > last_id."""
        query = "SELECT * FROM forensic_log WHERE id > ? ORDER BY id ASC LIMIT ?"
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(query, (last_id, limit))
            results = []
            for row in cursor:
                d = dict(row)
                if d.get("details"):
                    try:
                        d["details"] = json.loads(d["details"])
                    except Exception:
                        pass
                results.append(d)
            return results
