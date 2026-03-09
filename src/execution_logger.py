"""
Tachyon Tongs: Sentinel Execution Logger
Maintains a verifiable markdown audit trail of all autonomous runs.
"""
import os
from datetime import datetime

class ExecutionLogger:
    def __init__(self, log_file="RUN_LOG.md"):
        self.log_file = log_file
        self.start_time = None
        self.end_time = None
        self.trigger_type = "UNKNOWN"
        self.sites_polled = []
        self.threats_found = 0
        self.files_updated = []
        self.fatal_error = None
        
        # Ensure file exists with a header if new
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("# 📜 Tachyon Tongs: Sentinel Execution Ledger\n\n")
                f.write("This file contains the autonomous, cryptographically immutable (in a prod environment) execution history of the Sentinel agent.\n\n")

    def start_run(self, trigger_type: str):
        self.trigger_type = trigger_type
        self.start_time = datetime.now()

    def add_site_polled(self, site: str):
        self.sites_polled.append(site)
        
    def add_threat_found(self):
        self.threats_found += 1
        
    def add_file_updated(self, file_name: str):
        if file_name not in self.files_updated:
            self.files_updated.append(file_name)

    def log_fatal_error(self, error_msg: str):
        self.fatal_error = error_msg

    def finalize_run(self):
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        # Format the markdown ledger entry
        entry = f"## Run: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        entry += f"- **Trigger Source:** `{self.trigger_type}`\n"
        entry += f"- **Duration:** {duration.total_seconds():.2f} seconds\n"
        
        if self.sites_polled:
            entry += f"- **Sites Polled:** {', '.join(self.sites_polled)}\n"
        else:
            entry += "- **Sites Polled:** None\n"
            
        entry += f"- **Threats Identified:** {self.threats_found}\n"
        
        if self.files_updated:
            entry += f"- **Files Modified:** {', '.join(self.files_updated)}\n"
        else:
            entry += "- **Files Modified:** None\n"
            
        if self.fatal_error:
            entry += f"\n> [!CAUTION]\n> **Sentinel Crash Detected:**\n> ```\n> {self.fatal_error}\n> ```\n"
            
        entry += "\n---\n\n"
        
        # Append to the ledger
        with open(self.log_file, "a") as f:
            f.write(entry)
