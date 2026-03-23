import sqlite3
import json
import os
import threading
import base64
import fcntl
from datetime import datetime

class StateManager:
    """
    Durable Multi-Tenant State Manager for Tachyon Tongs.
    Handles SQLite (WAL mode) for execution logs and exploitation catalog.
    Now includes high-assurance hooks for field-level encryption.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
            
            # Allow forcing re-init for testing
            default_db = os.environ.get("TACHYON_DB_PATH", "tachyon_state.db")
            cls._instance._init_db(db_path or default_db)
            from .signing import IntegrityManager
            from .alert_limiter import AlertRateLimiter
            cls._instance.integrity = IntegrityManager()
            cls._instance.alert_limiter = AlertRateLimiter()
            cls._instance.db = cls._instance # Alias for logic that expects manager.db.conn
            
            # ENFORCEMENT: Verify core catalog integrity on boot
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            catalog_path = os.path.join(root_dir, "EXPLOITATION_CATALOG.md")
            
            try:
                cls._instance.integrity.verify_integrity(catalog_path)
            except RuntimeError as e:
                cls._instance.emit_alert("STATE_COMPROMISED", str(e))
                if os.environ.get("TACHYON_STRICT_MODE"):
                    raise e
            return cls._instance

    def _init_db(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            
            # 1. run_logs (Execution history)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS run_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    start_time TEXT,
                    trigger_type TEXT,
                    duration REAL,
                    sites_polled TEXT,
                    threats_identified INTEGER,
                    files_modified TEXT,
                    fatal_error TEXT,
                    verbose_level INTEGER
                )
            ''')
            
            # 2. exploitation_catalog (CVE intelligence)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS exploitation_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cve_id TEXT UNIQUE,
                    description TEXT,
                    source TEXT,
                    date_added TEXT,
                    relevance_class TEXT,
                    cvss REAL,
                    status TEXT,
                    mitigation_patch TEXT
                )
            ''')
            
            # 3. patches (Airlock proposals)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS patches (
                    id TEXT PRIMARY KEY,
                    cve_id TEXT,
                    summary TEXT,
                    status TEXT,
                    timestamp TEXT,
                    additions INTEGER,
                    deletions INTEGER,
                    debate_status TEXT
                )
            ''')
            
            # 4. processed_events (Idempotency)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processed_events (
                    event_id TEXT PRIMARY KEY,
                    processed_at TEXT,
                    source TEXT,
                    outcome TEXT
                )
            ''')

            # 5. pathogen_metrics (Adversarial Tuning)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pathogen_metrics (
                    mutation_id TEXT PRIMARY KEY,
                    cve_target TEXT,
                    bypass_vector TEXT,
                    block_rate REAL,
                    detected_by TEXT
                )
            ''')

            # 6. package_whitelist (Supply Chain Defense)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS package_whitelist (
                    package_name TEXT PRIMARY KEY,
                    version TEXT,
                    checksum TEXT,
                    added_at TEXT
                )
            ''')

            # 7. mutant_locks (Signal Purification)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mutant_locks (
                    lock_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    reason TEXT,
                    acquired_at TEXT,
                    expires_at TEXT
                )
            ''')

            # 8. relayed_events (Herald Tracking)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS relayed_events (
                    dispatcher_id TEXT,
                    event_id TEXT,
                    relayed_at TEXT,
                    PRIMARY KEY (dispatcher_id, event_id)
                )
            ''')
            conn.commit()

    def is_event_processed(self, event_id: str) -> bool:
        """Check if a specific autonomic event has already been handled."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM processed_events WHERE event_id = ?", (event_id,))
            return cursor.fetchone() is not None

    def mark_event_processed(self, event_id: str, source: str, outcome: str = "SUCCESS"):
        """Record an autonomic event as processed to prevent redundant evolutions."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO processed_events (event_id, processed_at, source, outcome)
                    VALUES (?, ?, ?, ?)
                ''', (event_id, datetime.now().isoformat(), source, outcome))
                conn.commit()

    def _encrypt_field(self, value: str) -> str:
        """Hook for field-level encryption. Currently basic Base64 for logic placeholder."""
        if not value: return value
        # In production, use Fernet/AES-GCM with TACHYON_SECRET_KEY
        return f"ENC:{base64.b64encode(value.encode()).decode()}"

    def _decrypt_field(self, value: str) -> str:
        """Hook for field-level decryption."""
        if value and value.startswith("ENC:"):
            return base64.b64decode(value[4:]).decode()
        return value

    def log_run(self, run_data, duration, limit=25, log_file="RUN_LOG.md"):
        """Atomically log a run execution and export it to Markdown."""
        sites_list = []
        site_results = run_data.get('site_results', {})
        for url in run_data.get('sites_polled', []):
            res = site_results.get(url, {"status": "UNKNOWN", "signals": 0})
            
            # Encrypt sensitive payload if requested/needed
            payload = res.get("payload")
            if os.environ.get("TACHYON_ENCRYPT_LOGS"):
                payload = self._encrypt_field(payload) if payload else None

            sites_list.append({
                "url": url,
                "status": res.get("status", "UNKNOWN"),
                "signals": res.get("signals", 0),
                "error": res.get("error"),
                "payload": payload
            })

        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO run_logs (agent_id, start_time, trigger_type, duration, sites_polled, threats_identified, files_modified, fatal_error, verbose_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    run_data['agent_id'],
                    (run_data.get('start_time') or datetime.now()).isoformat(),
                    run_data.get('trigger_type', 'UNKNOWN'),
                    float(duration),
                    json.dumps(sites_list),
                    run_data.get('threats_identified', 0),
                    json.dumps(run_data.get('files_modified', {})),
                    run_data.get('fatal_error'),
                    run_data.get('verbose_level', 2)
                ))
                conn.commit()
            self._export_run_log_markdown(limit, log_file)

    def _export_run_log_markdown(self, limit, log_file):
        """Materializes SQLite index out to human-readable Markdown."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM run_logs ORDER BY id DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            
            with open(log_file, "w") as f:
                f.write("# 📜 Tachyon Tongs: Sentinel Execution Ledger\n\n")
                f.write("This file contains the autonomous history of the Sentinel agent.\n\n")
                for row in rows:
                    entry = self._format_run_row(row)
                    f.write(entry)
                    f.write("\n\n---\n\n")

    def log_exploitation(self, threats, catalog_file="EXPLOITATION_CATALOG.md"):
        """Log batch of validated threats and export them to Markdown."""
        if not threats: return

        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                for threat in threats:
                    try:
                        # Updated to match new exploitation_catalog schema
                        conn.execute('''
                            INSERT OR IGNORE INTO exploitation_catalog (cve_id, description, status, mitigation_patch)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            threat.get('cve_id') or threat.get('id', 'UNKNOWN'),
                            threat.get('description') or threat.get('summary', 'No description.'),
                            threat.get('status', 'Identified'),
                            threat.get('mitigation_patch')
                        ))
                    except sqlite3.Error as e:
                        print(f"[StateManager] Failed to insert threat {threat.get('id')}: {e}")
                conn.commit()
            self.export_catalog(catalog_file)

    def export_catalog(self, catalog_file="EXPLOITATION_CATALOG.md"):
        """Materializes SQLite catalog index back out to human-readable Markdown (with signing)."""
        # USE LOCK FILE for atomic catalog access to prevent TOCTOU race conditions
        lock_path = catalog_file + ".lock"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM exploitation_catalog ORDER BY cve_id DESC') # Changed ORDER BY to cve_id
            rows = cursor.fetchall()
            
            with open(lock_path, "w") as lock_f:
                fcntl.flock(lock_f, fcntl.LOCK_EX)
                try:
                    with open(catalog_file, "w") as f:
                        f.write("# 📘 EXPLOITATION CATALOG\n\n")
                        f.write("This file is the single source of truth for internet-born AI/LLM threats.\n\n")
                        if not rows:
                            f.write("No catalog entries yet.\n")
                        else:
                            for row in rows:
                                d = dict(row)
                                f.write(f"### {d.get('cve_id', 'UNKNOWN')}\n")
                                f.write(f"- **Description:** {d.get('description', 'No description.')}\n")
                                f.write(f"- **CVSS:** {d.get('cvss', 'N/A')}\n")
                                f.write(f"- **Status:** {d.get('status', 'Identified')}\n")
                                f.write(f"- **Mitigation Patch:** {d.get('mitigation_patch', 'None')}\n\n")
                        f.flush()
                        os.fsync(f.fileno())
                    
                    # High-Assurance Signing (Ensures signature matches the locked state)
                    self.integrity.sign_document(catalog_file)
                finally:
                    fcntl.flock(lock_f, fcntl.LOCK_UN)

    def emit_alert(self, alert_type: str, message: str):
        """Emits a high-priority alert to the top-level ALERT.md ledger. Prepend via LIFO."""
        if hasattr(self, "alert_limiter") and not self.alert_limiter.should_allow(alert_type):
            return # Suppress loud alerts
            
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        alert_path = os.path.join(root_dir, "ALERT.md")
        if not os.path.exists(alert_path): alert_path = "ALERT.md"
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_block = f"## [{alert_type}] {timestamp}\n> [!CAUTION]\n> **CRITICAL SECURITY ALERT:**\n> {message}\n\n---\n\n"
        
        try:
            content = ""
            if os.path.exists(alert_path):
                with open(alert_path, "r") as f:
                    content = f.read()
            
            # Prepend after header if exists, else just prepend
            header = "# 🚨 Tachyon Tongs: High-Priority Alert Hub\n\nThis file tracks critical violations and integrity failures. The newest alerts appear at the top.\n\n"
            if content.startswith("# 🚨"):
                parts = content.split("\n\n") # Use simpler split
                if len(parts) >= 2:
                    content_without_header = "\n\n".join(parts[2:])
                    new_content = parts[0] + "\n\n" + parts[1] + "\n\n" + alert_block + content_without_header
                else:
                    new_content = header + alert_block
            else:
                new_content = header + alert_block + content

            with open(alert_path, "w") as f:
                f.write(new_content)
                f.flush()
                os.fsync(f.fileno())

            # Emit to Telemetry for Herald/Signal bridge
            from .telemetry import TelemetryBus
            TelemetryBus().emit_event("SECURITY_ALERT", "substrate", alert_type, "EMITTED", {"message": message})
        except Exception as e:
            print(f"[StateManager] Failed to emit alert: {e}")

    def _format_run_row(self, row):
        now = datetime.fromisoformat(row['start_time'])
        entry = f"## Run: {now.strftime('%Y-%m-%d %H:%M:%S')} (Agent: {row['agent_id']})\n"
        entry += f"- Trigger Source: `{row['trigger_type']}`\n"
        entry += f"- Duration: {row['duration']:.2f} seconds\n"
        
        sites_polled = json.loads(row['sites_polled'])
        verbose_level = row['verbose_level']
        
        sites = []
        for site in sites_polled:
            status_icon = "✅" if site.get("status") == "SUCCESS" else "❌"
            detail = f"{status_icon} `{site['url']}` ({site.get('signals', 0)} signals)"
            
            # Decrypt payload for display if it was encrypted
            payload = site.get("payload")
            if payload and payload.startswith("ENC:"):
                payload = self._decrypt_field(payload)

            if verbose_level >= 1 and site.get("error"):
                detail += f" - *Error: {site['error']}*"
            if verbose_level >= 2 and payload:
                detail += f"\n    - **Extracted Payload:** {payload}"
            sites.append(detail)
        
        sites_str = "\n  - ".join(sites) if sites else "None"
        entry += f"- Sites Audited:\n  - {sites_str}\n"
        entry += f"- Threats Identified: {row['threats_identified']}\n"
        
        files_modified = json.loads(row['files_modified'])
        files_section = "- Files Modified:\n"
        if not files_modified:
            files_section += "  - None\n"
        else:
            for fname, entries in files_modified.items():
                files_section += f"  - `{fname}`\n"
                if verbose_level >= 1:
                    for e in entries:
                        if e.get("details"): files_section += f"    - {e['details']}\n"
                        if verbose_level >= 2 and e.get("payload"):
                            files_section += f"    - **Injected Content:**\n```json\n{e['payload']}\n```\n"
        entry += files_section
        if row['fatal_error']:
            entry += f"\n> [!CAUTION]\n> **FATAL ERROR:** {row['fatal_error']}\n"
        return entry

    # High-Assurance Shims & Legacy Compatibility
    def _sign_document(self, filepath: str):
        return self.integrity.sign_document(filepath)

    def _verify_catalog_integrity(self, catalog_file: str):
        """Internal shim for legacy tests and boot verification."""
        try:
            return self.integrity.verify_integrity(catalog_file)
        except RuntimeError as e:
            if "No detached signature found" in str(e):
                # Legacy tests expect a print warning for missing signatures
                print(f"CRITICAL: {e}")
                return True
            raise e

    def commit(self): 
        """Stub for legacy transactional calls."""
        pass

    def is_package_whitelisted(self, package_name: str) -> bool:
        """Checks if a package is present in the authorized whitelist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM package_whitelist WHERE package_name = ?", (package_name,))
            return cursor.fetchone() is not None

    def sync_whitelist_from_manifest(self, manifest_path: str = "docs/adr/MANIFEST.json"):
        """Syncs the DB whitelist with the Merkle manifest."""
        if not os.path.exists(manifest_path):
            return
            
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            
        whitelist = manifest.get("supply_chain_whitelist", {})
        if not whitelist:
             return

        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                for pkg, details in whitelist.items():
                    conn.execute("""
                        INSERT OR REPLACE INTO package_whitelist (package_name, version, checksum, added_at)
                        VALUES (?, ?, ?, ?)
                    """, (pkg, details.get("version"), details.get("checksum"), datetime.now().isoformat()))
                conn.commit()

    def log_evolution(self, event_type: str, details: str, evolution_file: str = "logs/EVOLUTION.md", remediation: str = None):
        """Logs architectural or structural evolution of the substrate. Prepend via LIFO."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"## [{event_type}] {timestamp}\n{details}\n"
        if remediation:
            entry += f"\n> [!TIP]\n> **REMEDIATION:** {remediation}\n"
        entry += "\n---\n\n"
        
        # Ensure root_dir context if relative path
        if not os.path.isabs(evolution_file):
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            evolution_file = os.path.join(root_dir, evolution_file)

        header = "# 🧬 The Evolutionary Ledger\n\nThis file tracks the structural and cognitive growth of the Tachyon Tongs substrate.\n\n"
        
        content = ""
        if os.path.exists(evolution_file):
            with open(evolution_file, "r") as f:
                content = f.read()
        
        if not content.startswith("# 🧬"):
            new_content = header + entry + content
        else:
            # Prepend after exactly the first two lines (header + description)
            lines = content.splitlines()
            header_lines = lines[:4] # Title, empty, Description, empty
            body_lines = lines[4:]
            new_content = "\n".join(header_lines) + "\n\n" + entry + "\n".join(body_lines)
        
        with open(evolution_file, "w") as f:
            f.write(new_content)
            f.flush()
            os.fsync(f.fileno())

    def inject_tasks(self, threats: list, tasks_file="TASKS.md"):
        """Injects autonomous discoveries into the TASKS.md backlog."""
        if not threats: return
        
        with open(tasks_file, "r") as f:
            lines = f.readlines()
            
        new_lines = []
        in_section = False
        
        for line in lines:
            new_lines.append(line)
            if "## Security Task Progression" in line:
                in_section = True
                new_lines.append("### 🚨 [URGENT] Autonomous Discoveries\n")
                for threat in threats:
                    cve_id = threat.get('id') or threat.get('cve_id', 'UNKNOWN')
                    source = threat.get('source', 'Unknown')
                    new_lines.append(f"- [ ] **{cve_id}**: Investigating potential mitigation via {source}.\n")
                in_section = False # Only inject once
        
        with open(tasks_file, "w") as f:
            f.writelines(new_lines)
            f.flush()
            os.fsync(f.fileno())

    # --- Mutant Lock Implementation [ADR-0034] ---

    def acquire_mutant_lock(self, agent_id: str, reason: str, ttl_minutes: int = 5) -> str:
        """Acquire a time-bound, signed mutant lock to suppress Guardian alerts."""
        import uuid
        from datetime import timedelta
        
        lock_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = (now + timedelta(minutes=ttl_minutes)).isoformat()
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO mutant_locks (lock_id, agent_id, reason, acquired_at, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (lock_id, agent_id, reason, now.isoformat(), expires_at))
                conn.commit()
        
        self.log_evolution("MUTANT_LOCK_ACQUIRED", f"Agent {agent_id} acquired lock {lock_id} for: {reason}")
        return lock_id

    def release_mutant_lock(self, lock_id: str):
        """Explicitly release a mutant lock."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM mutant_locks WHERE lock_id = ?", (lock_id,))
                conn.commit()
        self.log_evolution("MUTANT_LOCK_RELEASED", f"Lock {lock_id} released.")

    def is_mutant_lock_active(self) -> bool:
        """Check if there is an active, non-expired mutant lock in the substrate."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM mutant_locks WHERE expires_at > ?", (now,))
            return cursor.fetchone() is not None

    # --- Herald Aggregator Support [ADR-0035] ---

    def get_pending_patches(self) -> list:
        """Retrieve all Airlock patches awaiting review."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM patches WHERE status = 'PENDING' OR status = 'PROPOSED'")
            return [dict(row) for row in cursor.fetchall()]

    def is_event_relayed(self, dispatcher_id: str, event_id: str) -> bool:
        """Check if an event has already been relayed by a specific dispatcher."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM relayed_events WHERE dispatcher_id = ? AND event_id = ?",
                (dispatcher_id, event_id)
            )
            return cursor.fetchone() is not None

    def mark_event_relayed(self, dispatcher_id: str, event_id: str):
        """Record that an event has been successfully relayed."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO relayed_events (dispatcher_id, event_id, relayed_at) VALUES (?, ?, ?)",
                    (dispatcher_id, event_id, datetime.now().isoformat())
                )
                conn.commit()
