"""
Tachyon Tongs: Execution Ledger Manager
Implements immutable-style logging for the Sentinel's autonomous runs.
Now supports prepending and a 25-run limit.
"""
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List

class ExecutionLogger:
    """
    Forensic Logger for the Sentinel Agent's execution runs.
    Materializes structured logs into human-readable Markdown (RUN_LOG.md).
    Includes auto-pruning and archival logic to prevent 'Log Fog'.
    """
    def __init__(self, agent_id="Sentinel", log_path: str = "RUN_LOG.md", limit=25, verbose_level=2, archive_dir: str = "memory/archive"):
        self.log_path = log_path
        self.archive_dir = archive_dir
        self.max_log_size = 100 * 1024 # 100 KB
        self.limit = limit
        self.agent_id = agent_id
        self.verbose_level = verbose_level
        
    @property
    def log_file(self):
        return self.log_path
    
    @log_file.setter
    def log_file(self, value):
        self.log_path = value

    @property
    def run_data(self):
        # ... logic to return default run_data if not set ...
        if not hasattr(self, "_run_data") or self._run_data is None:
             self._run_data = {
                "agent_id": self.agent_id,
                "start_time": None,
                "trigger_type": "UNKNOWN",
                "sites_polled": [],
                "site_results": {},
                "threats_identified": 0,
                "files_modified": {},
                "fatal_error": None
            }
        return self._run_data

    @run_data.setter
    def run_data(self, value):
        self._run_data = value

    def start_run(self, trigger="CRON"):
        # Reset run_data for a new run, but keep agent_id
        self.run_data = {
            "agent_id": self.agent_id,
            "start_time": datetime.now(),
            "trigger_type": trigger,
            "sites_polled": [],
            "site_results": {},
            "threats_identified": 0,
            "files_modified": {},
            "fatal_error": None
        }

    def add_site_polled(self, url):
        if url not in self.run_data["sites_polled"]:
            self.run_data["sites_polled"].append(url)

    def add_site_result(self, url, status="SUCCESS", signals=0, error=None, payload=None):
        self.add_site_polled(url)
        self.run_data["site_results"][url] = {
            "status": status,
            "signals": signals,
            "error": error,
            "payload": payload
        }

    def add_threat_found(self):
        self.run_data["threats_identified"] += 1

    def add_file_updated(self, file_path, details=None, payload=None):
        basename = os.path.basename(file_path)
        if basename not in self.run_data["files_modified"]:
            self.run_data["files_modified"][basename] = []
        if details or payload:
            self.run_data["files_modified"][basename].append({"details": details, "payload": payload})

    def log_fatal_error(self, error_msg):
        self.run_data["fatal_error"] = error_msg

    def finalize_run(self):
        duration = 0.0
        if self.run_data["start_time"]:
            duration = (datetime.now() - self.run_data["start_time"]).total_seconds()
            
        self._check_archival_needed()

        # Hook into the multi-tenant durable StateManager
        from tachyon.core.state import StateManager
        manager = StateManager()
        manager.log_run(
            run_data=self.run_data,
            duration=duration,
            limit=self.limit,
            log_file=self.log_path
        )

    def _check_archival_needed(self):
        """Archives the current log if it exceeds the size threshold."""
        if not os.path.exists(self.log_path):
            return

        if os.path.getsize(self.log_path) > self.max_log_size:
            os.makedirs(self.archive_dir, exist_ok=True)
            archive_name = f"RUN_LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            archive_path = os.path.join(self.archive_dir, archive_name)
            
            try:
                shutil.move(self.log_path, archive_path)
                with open(self.log_path, "w") as f:
                    f.write(f"# 📜 Tachyon Tongs: Execution Ledger (New Epoch)\n")
                    f.write(f"Previous logs archived to: `{archive_path}`\n\n---\n\n")
            except Exception as e:
                print(f"[ExecutionLogger] Failed to archive log: {e}")

