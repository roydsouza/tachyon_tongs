import os
import json
import sqlite3
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class TachyonEventBus:
    """
    SQLite-WAL based Event Broker for Tachyon Tongs Agents.
    Provides persistent, concurrent pub/sub for the Immune Collective.
    Phase 33: Core Infrastructure Implementation.
    """
    
    def __init__(self, db_path: Optional[str] = None, integrity_manager: Optional[Any] = None):
        if not db_path:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            mem_dir = os.path.join(root_dir, "memory", "operational")
            os.makedirs(mem_dir, exist_ok=True)
            db_path = os.path.join(mem_dir, "bus.db")
        
        self.db_path = db_path
        self._init_db()
        self.im = integrity_manager
        
        # S-04 Loop Guard: Sliding-window event tracking
        # Key: hash(topic:payload), Value: list of timestamps
        self._event_cache: Dict[str, List[float]] = {}
        self.LOOP_WINDOW_SEC = 300
        self.LOOP_THRESHOLD = 3

    def _get_connection(self):
        """Returns a SQLite connection with WAL mode enabled."""
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        """Initialize the event_bus table and indexes."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS event_bus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT UNIQUE,
                    timestamp TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    signature TEXT,
                    certificate_json TEXT,
                    status TEXT DEFAULT 'PENDING'
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_topic ON event_bus(topic);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON event_bus(status);")
            conn.commit()

    def emit_event(
        self, 
        topic: str, 
        agent_id: str, 
        payload: Dict[str, Any], 
        signature: Optional[str] = None,
        certificate: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ) -> int:
        """
        Publish an event to the bus.
        
        Args:
            topic: The event channel (e.g., 'CVE_DISCOVERED', 'PATCH_PROPOSED')
            agent_id: The role/ID of the publisher
            payload: JSON-serializable event data
            signature: Hybrid PQC signature of the event data
            certificate: The agent's delegation certificate (JSON)
        """
        timestamp = timestamp or datetime.now().isoformat()
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        
        # 1. S-04 Loop Guard Check
        event_key = hashlib.sha256(f"{topic}:{payload_json}".encode('utf-8')).hexdigest()
        now = time.time()
        
        # Clean stale events from cache
        if event_key in self._event_cache:
            self._event_cache[event_key] = [t for t in self._event_cache[event_key] if now - t < self.LOOP_WINDOW_SEC]
            
            if len(self._event_cache[event_key]) >= self.LOOP_THRESHOLD:
                # Trigger circuit breaker
                from tachyon.core.state import StateManager
                msg = f"LOOP DETECTED: Suppressing identical event flood on topic '{topic}' from Agent '{agent_id}'."
                StateManager().emit_alert("SECURITY_ALERT_LOOP", msg)
                return -1 # Event suppressed
            
            self._event_cache[event_key].append(now)
        else:
            self._event_cache[event_key] = [now]

        # 2. Persistence
        certificate_json = json.dumps(certificate) if certificate else None
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO event_bus (timestamp, topic, agent_id, payload_json, signature, certificate_json) VALUES (?, ?, ?, ?, ?, ?)",
                (timestamp, topic, agent_id, payload_json, signature, certificate_json)
            )
            event_id = cursor.lastrowid
            conn.commit()
            return event_id

    def fetch_events(self, topic: str, after_id: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve events for a specific topic after a certain ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM event_bus WHERE topic = ? AND id > ? ORDER BY id ASC LIMIT ?",
                (topic, after_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def mark_processed(self, event_id: int, status: str = 'PROCESSED'):
        """Update the status of an event."""
        with self._get_connection() as conn:
            conn.execute("UPDATE event_bus SET status = ? WHERE id = ?", (status, event_id))
            conn.commit()

    def verify_event(self, event_id: int) -> bool:
        """
        Verify the PQC signature of an event using IntegrityManager and certificates.
        """
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM event_bus WHERE id = ?", (event_id,)).fetchone()
            if not row or not row['signature'] or not row['certificate_json']:
                return False
            
            # 1. Reconstruct signed content
            # Pattern: topic + payload_json + timestamp
            content = f"{row['topic']}:{row['payload_json']}:{row['timestamp']}".encode('utf-8')
            signature = row['signature']
            certificate = json.loads(row['certificate_json'])
            
            # 2. Lazy load Integrity and Certification layers
            from tachyon.core.signing import IntegrityManager
            from tachyon.core.keys.certificates import DelegationCertificateAuthority
            from tachyon.core.keys.hybrid import HybridSigner
            import base64
            from cryptography.hazmat.primitives.asymmetric import ed25519
            
            im = self.im or IntegrityManager(use_hardware=False) # Local verify
            ca = DelegationCertificateAuthority(im)
            
            # 3. Validate Certificate
            is_cert_valid, reason = ca.validate_certificate(certificate)
            if not is_cert_valid:
                print(f"[EventBus] Certificate validation failed: {reason}")
                return False
            
            # 4. Extract Agent Public Key from Certificate
            pub_bytes = base64.b64decode(certificate['payload']['subject']['public_key_b64'])
            agent_pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            
            # 5. Verify Signature against agent key 
            # (HybridSigner can take only public keys for verification)
            signer = HybridSigner(ed25519_pk=agent_pub_key)
            try:
                return signer.verify(content, signature)
            except Exception as e:
                print(f"[EventBus] Signature verification failed: {e}")
                return False
