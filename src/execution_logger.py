"""
Tachyon Tongs: Execution Ledger Manager
Implements immutable-style logging for the Sentinel's autonomous runs.
Now supports prepending and a 25-run limit.
"""
import datetime
import os

class ExecutionLogger:
    def __init__(self, agent_id="Sentinel", log_file="RUN_LOG.md", limit=25, verbose_level=2):
        self.log_file = log_file
        self.limit = limit
        self.agent_id = agent_id
        self.verbose_level = verbose_level
        self.run_data = {
            "agent_id": self.agent_id,
            "start_time": None,
            "trigger_type": "UNKNOWN",
            "sites_polled": [],
            "site_results": {}, # Maps URL -> {"status": "SUCCESS/FAIL", "signals": N, "error": msg}
            "threats_identified": 0,
            "files_modified": {}, # Maps filename -> list of [details]
            "fatal_error": None
        }

    def start_run(self, trigger="CRON"):
        # Reset run_data for a new run, but keep agent_id
        self.run_data = {
            "agent_id": self.agent_id,
            "start_time": datetime.datetime.now(),
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
            duration = (datetime.datetime.now() - self.run_data["start_time"]).total_seconds()
            
        # Hook into the multi-tenant durable StateManager
        from src.state_manager import StateManager
        manager = StateManager()
        manager.log_run(
            run_data=self.run_data,
            duration=duration,
            limit=self.limit,
            log_file=self.log_file
        )

