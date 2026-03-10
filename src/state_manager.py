import sqlite3
import json
import os
import threading
from datetime import datetime

class StateManager:
    """
    Durable Multi-Tenant State Manager for Tachyon Tongs.
    Replaces Markdown-as-database with SQLite (WAL mode) to support concurrent agent traffic.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path="tachyon_state.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                cls._instance._init_db(db_path)
            return cls._instance

    def _init_db(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            # Create Execution Ledger table
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
            # Create Exploitation Catalog table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS exploitation_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cve_id TEXT UNIQUE,
                    description TEXT,
                    source TEXT,
                    date_added TEXT
                )
            ''')
            conn.commit()

    def log_run(self, run_data, duration, limit=25, log_file="RUN_LOG.md"):
        """
        Atomically log a run execution and export it to the human-readable Markdown ledger.
        """
        
        # Transform the site data into a JSON serializable list constraint
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
            
            # Trigger the downstream pipeline format
            self._export_run_log_markdown(limit, log_file)

    def _export_run_log_markdown(self, limit, log_file):
        """
        Materializes the SQLite index back out to the human-readable Markdown.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM run_logs ORDER BY id DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            
            header = "# 📜 Tachyon Tongs: Sentinel Execution Ledger\n\n"
            header += "This file contains the autonomous, cryptographically immutable (in a prod environment) execution history of the Sentinel agent.\n\n"
            
            with open(log_file, "w") as f:
                f.write(header)
                for row in rows:
                    entry = self._format_run_row(row)
                    f.write(entry)
                    f.write("\n\n---\n\n")

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

    def log_exploitation(self, threats, catalog_file="EXPLOITATION_CATALOG.md"):
        """
        Atomically log a batch of validated threats and export them to the Markdown catalog.
        """
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
            
            self._export_catalog_markdown(catalog_file)

    def _export_catalog_markdown(self, catalog_file):
        """
        Materializes the SQLite catalog index back out to the human-readable Markdown.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM exploitation_catalog ORDER BY id DESC')
            rows = cursor.fetchall()
            
            header = "# 📘 EXPLOITATION CATALOG\n\n"
            header += "This file is the single source of truth for internet-born AI/LLM terror.\n\n"
            
            with open(catalog_file, "w") as f:
                f.write(header)
                if not rows:
                    f.write("No catalog entries yet.\n")
                    return
                    
                for row in rows:
                    entry = f"### {row['cve_id']}\n"
                    entry += f"- **Source:** {row['source']}\n"
                    entry += f"- **Date Discovered:** {row['date_added']}\n"
                    entry += f"- **Description:** {row['description']}\n\n"
                    f.write(entry)
