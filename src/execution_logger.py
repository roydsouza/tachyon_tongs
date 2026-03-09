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

    def _format_entry(self):
        now = self.run_data["start_time"] or datetime.datetime.now()
        duration = (datetime.datetime.now() - now).total_seconds()
        
        entry = f"## Run: {now.strftime('%Y-%m-%d %H:%M:%S')} (Agent: {self.run_data['agent_id']})\n"
        entry += f"- Trigger Source: `{self.run_data['trigger_type']}`\n"
        entry += f"- Duration: {duration:.2f} seconds\n"
        
        sites = []
        for url in self.run_data["sites_polled"]:
            res = self.run_data["site_results"].get(url, {"status": "UNKNOWN", "signals": 0})
            status_icon = "✅" if res["status"] == "SUCCESS" else "❌"
            detail = f"{status_icon} `{url}` ({res['signals']} signals)"
            if self.verbose_level >= 1 and res.get("error"):
                detail += f" - *Error: {res['error']}*"
            if self.verbose_level >= 2 and res.get("payload"):
                detail += f"\n    - **Extracted Payload:** {res['payload']}"
            sites.append(detail)
        
        sites_str = "\n  - ".join(sites) if sites else "None"
        entry += f"- Sites Audited:\n  - {sites_str}\n"
        
        entry += f"- Threats Identified: {self.run_data['threats_identified']}\n"
        
        files_section = "- Files Modified:\n"
        if not self.run_data["files_modified"]:
            files_section += "  - None\n"
        else:
            for fname, entries in self.run_data["files_modified"].items():
                files_section += f"  - `{fname}`\n"
                if self.verbose_level >= 1:
                    for e in entries:
                        if e.get("details"):
                            files_section += f"    - {e['details']}\n"
                        if self.verbose_level >= 2 and e.get("payload"):
                            files_section += f"    - **Injected Content:**\n```json\n{e['payload']}\n```\n"
        entry += files_section
        
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
