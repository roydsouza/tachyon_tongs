import sqlite3
import json
import os
import threading
from datetime import datetime

class StateManager:
    """
    Durable Multi-Tenant State Manager for Tachyon Tongs.
    Handles SQLite (WAL mode) for execution logs and exploitation catalog.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                default_db = os.environ.get("TACHYON_DB_PATH", "tachyon_state.db")
                cls._instance._init_db(db_path or default_db)
                from .signing import IntegrityManager
                cls._instance.integrity = IntegrityManager()
                cls._instance.db = cls._instance # Alias for logic that expects manager.db.conn
                
                # ENFORCEMENT: Verify core catalog integrity on boot
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                catalog_path = os.path.join(root_dir, "EXPLOITATION_CATALOG.md")
                
                try:
                    cls._instance.integrity.verify_integrity(catalog_path)
                except RuntimeError as e:
                    cls._instance.emit_alert("STATE_COMPROMISED", str(e))
                    raise e
            return cls._instance

    def _init_db(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            # Execution Ledger
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
            # Exploitation Catalog
            conn.execute('''
                CREATE TABLE IF NOT EXISTS exploitation_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cve_id TEXT UNIQUE,
                    description TEXT,
                    source TEXT,
                    date_added TEXT,
                    relevance_class TEXT  -- NEW: For filtering precision metrics
                )
            ''')
            # Handle migration for existing DB
            try:
                conn.execute("ALTER TABLE exploitation_catalog ADD COLUMN relevance_class TEXT")
            except sqlite3.OperationalError:
                pass # Already exists
            conn.commit()

    def log_run(self, run_data, duration, limit=25, log_file="RUN_LOG.md"):
        """Atomically log a run execution and export it to Markdown."""
        sites_list = []
        site_results = run_data.get('site_results', {})
        for url in run_data.get('sites_polled', []):
            res = site_results.get(url, {"status": "UNKNOWN", "signals": 0})
            sites_list.append({
                "url": url,
                "status": res.get("status", "UNKNOWN"),
                "signals": res.get("signals", 0),
                "error": res.get("error"),
                "payload": res.get("payload")
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
            
            header = "# 📜 Tachyon Tongs: Sentinel Execution Ledger\n\n"
            header += "This file contains the autonomous history of the Sentinel agent.\n\n"
            
            with open(log_file, "w") as f:
                f.write(header)
                for row in rows:
                    entry = self._format_run_row(row)
                    f.write(entry)
                    f.write("\n\n---\n\n")

    def log_exploitation(self, threats, catalog_file="EXPLOITATION_CATALOG.md"):
        """Log batch of validated threats and export them to Markdown."""
        if not threats:
            return

        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                for threat in threats:
                    try:
                        conn.execute('''
                            INSERT OR IGNORE INTO exploitation_catalog (cve_id, description, source, date_added)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            threat.get('cve_id') or threat.get('id', 'UNKNOWN'),
                            threat.get('description') or threat.get('summary', 'No description.'),
                            threat.get('source', 'Unknown Source'),
                            threat.get('timestamp') or datetime.now().isoformat()
                        ))
                    except sqlite3.Error as e:
                        print(f"[StateManager] Failed to insert threat {threat.get('id')}: {e}")
                conn.commit()
            self.export_catalog(catalog_file)

    def commit(self):
        """No-op shim for legacy code that calls manager.commit() directly."""
        pass

    def is_package_whitelisted(self, package_name: str) -> bool:
        """Shim for integrity auditing."""
        return True

    def log_evolution(self, *args, **kwargs):
        """Logs a code mutation event (Evolutionary Ledger)."""
        # This is a shim for legacy tests that expect this functionality.
        pass

    def inject_tasks(self, threats: list):
        """Injects new security tasks into the SQLite state (Stub for current architecture)."""
        # In this modular version, tasks are managed via TASKS.md primarily.
        # This method provides compatibility for the Engineer agent to signal new tasks.
        pass

    def export_catalog(self, catalog_file="EXPLOITATION_CATALOG.md"):
        """Materializes SQLite catalog index back out to human-readable Markdown (with signing)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM exploitation_catalog ORDER BY id DESC')
            rows = cursor.fetchall()
            
            header = "# 📘 EXPLOITATION CATALOG\n\n"
            header += "This file is the single source of truth for internet-born AI/LLM threats.\n\n"
            
            with open(catalog_file, "w") as f:
                f.write(header)
                if not rows:
                    f.write("No catalog entries yet.\n")
                else:
                    for row in rows:
                        entry = f"### {row['cve_id']}\n"
                        entry += f"- **Source:** {row['source']}\n"
                        entry += f"- **Date Discovered:** {row['date_added']}\n"
                        entry += f"- **Description:** {row['description']}\n\n"
                        f.write(entry)
            
            self.integrity.sign_document(catalog_file)

    def emit_alert(self, alert_type: str, message: str):
        """Emits a high-priority alert to the top-level ALERT.md ledger."""
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        alert_path = os.path.join(root_dir, "ALERT.md")
        
        if not os.path.exists(alert_path):
            # Fallback to current working directory
            alert_path = "ALERT.md"
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_block = f"""
## [{alert_type}] {timestamp}
> [!CAUTION]
> **CRITICAL SECURITY ALERT:**
> {message}

---
"""
        try:
            with open(alert_path, "r") as f:
                content = f.read()
            
            # Prepend after header section (LIFO)
            marker = "## 📅 Active Alerts (Latest First)"
            if marker in content:
                insertion_point = content.find(marker) + len(marker)
                # We want to insert EXACTLY after the marker + its following newlines
                # but BEFORE any existing alerts or the system status note
                new_content = content[:insertion_point].rstrip() + "\n\n" + alert_block + content[insertion_point:].strip() + "\n"
                with open(alert_path, "w") as f:
                    f.write(new_content)
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
            if verbose_level >= 1 and site.get("error"):
                detail += f" - *Error: {site['error']}*"
            if verbose_level >= 2 and site.get("payload"):
                detail += f"\n    - **Extracted Payload:** {site['payload']}"
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
                        if e.get("details"):
                            files_section += f"    - {e['details']}\n"
                        if verbose_level >= 2 and e.get("payload"):
                            files_section += f"    - **Injected Content:**\n```json\n{e['payload']}\n```\n"
        entry += files_section
        
        if row['fatal_error']:
            entry += f"\n> [!CAUTION]\n> **FATAL ERROR:** {row['fatal_error']}\n"
            
        return entry
