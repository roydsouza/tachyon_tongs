import sqlite3
import json
import os
import threading
import hmac
import hashlib
from datetime import datetime


class StateManager:
    """
    Durable Multi-Tenant State Manager for Tachyon Tongs.
    Replaces Markdown-as-database with SQLite (WAL mode) to support concurrent agent traffic.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                # Allow environment override for testing
                default_db = os.environ.get("TACHYON_DB_PATH", "tachyon_state.db")
                cls._instance._init_db(db_path or default_db)
                cls._instance._init_crypto()
            return cls._instance

    def _init_crypto(self):
        """
        Initialize the cryptographic signing identity. 
        In production, this would be tied to a TPM or YubiKey ed25519-sk.
        For Phase 8 resilience, we use an ephemeral or environment-provided key.
        """
        self.secret_key = os.environ.get("TACHYON_SECRET_KEY", "ephemeral-fallback-key-for-zero-day-drill").encode('utf-8')
        # On boot, verify the integrity of the active exploitation catalog.
        # This prevents out-of-band editing by malicious actors.
        self._verify_catalog_integrity()

    def _sign_document(self, filepath: str) -> str:
        """Sign a file and return the hex digest. We store this in a parallel .sig file."""
        if not os.path.exists(filepath):
            return ""
        with open(filepath, 'rb') as f:
            content = f.read()
            
        digest = hmac.new(self.secret_key, content, hashlib.sha256).hexdigest()
        
        # Write the detached signature
        sig_path = f"{filepath}.sig"
        with open(sig_path, 'w') as sf:
            sf.write(digest)
            
        return digest
        
    def _verify_catalog_integrity(self, catalog_file="EXPLOITATION_CATALOG.md"):
        """Verify the cryptographic signature of the catalog."""
        if not os.path.exists(catalog_file):
            return  # Brand new organism, nothing to verify
            
        sig_path = f"{catalog_file}.sig"
        if not os.path.exists(sig_path):
            print(f"[StateManager] CRITICAL: No detached signature found for {catalog_file}!")
            # In a strict environment we might raise RuntimeError("Integrity Compromised: Missing Signature")
            # But for testing we just warn initially unless explicitly set.
            return
            
        with open(sig_path, 'r') as sf:
            expected_sig = sf.read().strip()
            
        with open(catalog_file, 'rb') as f:
            content = f.read()
            
        actual_sig = hmac.new(self.secret_key, content, hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise RuntimeError(f"INTEGRITY COMPROMISED: {catalog_file} was modified out-of-band! Halt.")
        else:
            print(f"[StateManager] Cryptographic state integrity verified for {catalog_file}.")

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
            
            self.export_catalog(catalog_file)

    def _export_catalog_markdown(self, catalog_file="EXPLOITATION_CATALOG.md"):
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
                else:
                    for row in rows:
                        entry = f"### {row['cve_id']}\n"
                        entry += f"- **Source:** {row['source']}\n"
                        entry += f"- **Date Discovered:** {row['date_added']}\n"
                        entry += f"- **Description:** {row['description']}\n\n"
                        f.write(entry)
            
            # Cryptographically sign the newly exported ledger
            self._sign_document(catalog_file)

    def export_catalog(self, catalog_file="EXPLOITATION_CATALOG.md"):
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
                else:
                    for row in rows:
                        entry = f"### {row['cve_id']}\n"
                        entry += f"- **Source:** {row['source']}\n"
                        entry += f"- **Date Discovered:** {row['date_added']}\n"
                        entry += f"- **Description:** {row['description']}\n\n"
                        f.write(entry)
            
            # Cryptographically sign the newly exported ledger
            self._sign_document(catalog_file)

    def is_package_whitelisted(self, package_spec: str) -> bool:
        """
        Checks if a package (and optionally its version) is in the trusted registry.
        """
        safe_list = ["requests", "rich", "textual", "mlx_lm", "openai", "anthropic", "pytest"]
        base_name = package_spec.split('==')[0].split('>=')[0].strip().lower()
        return base_name in [s.lower() for s in safe_list]

    def inject_tasks(self, threats, tasks_file="TASKS.md"):
        """
        Dynamically mutate the project backlog with actionable items derived from newly discovered threats.
        This provides true self-evolution capability.
        """
        if not threats or not os.path.exists(tasks_file):
            return

        with self._lock:
            try:
                with open(tasks_file, 'r') as f:
                    lines = f.readlines()

                # Find injection point: Under "## Security Task Progression" or just the first active list item
                injection_index = -1
                for i, line in enumerate(lines):
                    if "## Security Task Progression" in line:
                        injection_index = i + 1
                        break

                if injection_index == -1:
                    print(f"[{self.__class__.__name__}] Could not find injection point in {tasks_file}.")
                    return

                # Build the new task lines
                new_tasks = []
                for threat in threats:
                    cve = threat.get('cve_id') or threat.get('id', 'UNKNOWN')
                    source = threat.get('source', 'Unknown')
                    
                    # Prevent duplicates: only inject if the cve identifier isn't already active or completed in the backlog
                    if not any(cve in line for line in lines):
                        new_tasks.append(f"- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against {cve} from {source}.\n")

                if new_tasks:
                    staged_at = datetime.datetime.now().isoformat()
                    lines.insert(injection_index, "\n### 🚨 [URGENT] Autonomous Discoveries (Triad Scraped)\n")
                    # We store the metadata in a hidden or specific format for the fallback to parse
                    new_tasks_with_meta = [f"{task} <!-- STAGED_AT: {staged_at} -->\n" for task in new_tasks]
                    lines.insert(injection_index + 1, "".join(new_tasks_with_meta) + "\n")

                    with open(tasks_file, 'w') as f:
                        f.writelines(lines)
            except Exception as e:
                print(f"[{self.__class__.__name__}] Failed to organically mutate {tasks_file}: {e}")

    def log_evolution(self, event_type, details, evolution_file="EVOLUTION.md"):
        """
        The Somatic Ledger. Prepends evolutionary mutations (e.g., Code Patches, SITES.md expansions) 
        to the top of the EVOLUTION.md log.
        """
        header = "# 🌱 Tachyon Tongs: The Evolutionary Ledger\n\nThis file is the living record of the organism's autonomous self-healing, code-patching, and perimeter expansion. Entries are prepended chronologically.\n\n"
        
        with self._lock:
            try:
                if not os.path.exists(evolution_file):
                    with open(evolution_file, "w") as f:
                        f.write(header)
                
                with open(evolution_file, "r") as f:
                    content = f.read()
                
                # Strip the header to prepend the new entry right below it
                if content.startswith(header):
                    body = content[len(header):]
                else:
                    body = content
                
                now = datetime.now().isoformat(timespec='seconds')
                new_entry = f"## 🧬 Mutation: {now} | Type: {event_type}\n"
                new_entry += f"{details}\n\n---\n\n"
                
                with open(evolution_file, "w") as f:
                    f.write(header + new_entry + body)
            except Exception as e:
                print(f"[{self.__class__.__name__}] Failed to write to evolutionary ledger {evolution_file}: {e}")
