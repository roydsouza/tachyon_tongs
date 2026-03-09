"""
Tachyon Tongs: Execution Ledger Manager
Implements immutable-style logging for the Sentinel's autonomous runs.
Now supports prepending and a 25-run limit.
"""
import datetime
import os

class ExecutionLogger:
    def __init__(self, log_file="RUN_LOG.md", limit=25):
        self.log_file = log_file
        self.limit = limit
        self.run_data = {
            "start_time": None,
            "trigger_type": "UNKNOWN",
            "sites_polled": [],
            "threats_identified": 0,
            "files_modified": [],
            "fatal_error": None
        }

    def start_run(self, trigger_type="CRON"):
        self.run_data["start_time"] = datetime.datetime.now()
        self.run_data["trigger_type"] = trigger_type

    def add_site_polled(self, url):
        if url not in self.run_data["sites_polled"]:
            self.run_data["sites_polled"].append(url)

    def add_threat_found(self):
        self.run_data["threats_identified"] += 1

    def add_file_updated(self, file_path):
        basename = os.path.basename(file_path)
        if basename not in self.run_data["files_modified"]:
            self.run_data["files_modified"].append(basename)

    def log_fatal_error(self, error_msg):
        self.run_data["fatal_error"] = error_msg

    def _format_entry(self):
        now = self.run_data["start_time"] or datetime.datetime.now()
        duration = (datetime.datetime.now() - now).total_seconds()
        
        entry = f"## Run: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        entry += f"- Trigger Source: `{self.run_data['trigger_type']}`\n"
        entry += f"- Duration: {duration:.2f} seconds\n"
        
        sites = ", ".join(self.run_data["sites_polled"]) if self.run_data["sites_polled"] else "None"
        entry += f"- Sites Polled: {sites}\n"
        
        entry += f"- Threats Identified: {self.run_data['threats_identified']}\n"
        
        files = ", ".join(self.run_data["files_modified"]) if self.run_data["files_modified"] else "None"
        entry += f"- Files Modified: {files}\n"
        
        if self.run_data["fatal_error"]:
            entry += f"\n> [!CAUTION]\n> **FATAL ERROR:** {self.run_data['fatal_error']}\n"
            
        entry += "\n---\n\n"
        return entry

    def finalize_run(self):
        new_entry = self._format_entry()
        
        header = "# 📜 Tachyon Tongs: Sentinel Execution Ledger\n\n"
        header += "This file contains the autonomous, cryptographically immutable (in a prod environment) execution history of the Sentinel agent.\n\n"
        
        existing_content = ""
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                existing_content = f.read()
        
        # Strip header from existing content if it exists
        if existing_content.startswith("# 📜 Tachyon Tongs"):
            # Find the first run entry (starts with ## Run:)
            run_pos = existing_content.find("## Run:")
            if run_pos != -1:
                existing_content = existing_content[run_pos:]
            else:
                existing_content = ""

        # Split into individual runs (assuming partitioned by "---")
        runs = [r.strip() for r in existing_content.split("---") if "## Run:" in r]
        
        # Combine new entry with existing runs
        all_runs = [new_entry.strip()] + runs
        
        # Apply the limit (N=25)
        all_runs = all_runs[:self.limit]
        
        # Write back to file with header
        with open(self.log_file, "w") as f:
            f.write(header)
            for run in all_runs:
                f.write(run)
                f.write("\n\n---\n\n")
