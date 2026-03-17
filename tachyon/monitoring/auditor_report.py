"""
Tachyon Tongs: Sentinel Auditor Report
Parses the RUN_LOG.md and TASKS.md to generate a human-readable 
summary of the Sentinel's latest autonomic activity.
"""
import os
import re
import sys

# Add the root directory to PYTHONPATH so it can be invoked easily
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AuditorReport:
    """
    Synthesizes autonomic telemetry into human-readable executive summaries.
    """
    
    def __init__(self, log_path: str = "RUN_LOG.md", task_path: str = "TASKS.md"):
        self.log_path = log_path
        self.task_path = task_path

    def read_file_safe(self, filepath: str) -> str:
        try:
            with open(filepath, "r") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def get_latest_run(self, log_content: str) -> str:
        """Extracts the most recent run block from RUN_LOG.md."""
        runs = log_content.split("## Run: ")
        if len(runs) < 2:
            return "No execution runs recorded yet."
        
        # Get the last block and strip the trailing horizontal rule
        latest_block = runs[-1].split("---")[0].strip()
        return f"**Latest Sentinel Run:**\nDate/Time: {latest_block}"

    def get_pending_tasks(self, task_content: str) -> list:
        """Extracts all incomplete [ ] tasks from TASKS.md."""
        tasks = []
        for line in task_content.split('\n'):
            if line.strip().startswith("- [ ]"):
                tasks.append(line.strip())
        return tasks

    def generate_report(self):
        report_lines = ["# 🛡️ Sentinel Auditor Report\n"]
        
        # 1. Parse RUN_LOG.md
        log_content = self.read_file_safe(self.log_path)
        report_lines.append(self.get_latest_run(log_content))
        report_lines.append("\n---\n")
        
        # 2. Parse TASKS.md
        task_content = self.read_file_safe(self.task_path)
        pending_tasks = self.get_pending_tasks(task_content)
        
        report_lines.append("### Pending Architectural Enhancements")
        if pending_tasks:
            report_lines.append("The Sentinel (or prior roadmaps) has proposed the following unresolved defenses:\n")
            for task in pending_tasks:
                report_lines.append(task)
            report_lines.append("\n> **Recommendation:** Would you like AntiGravity to begin implementing any of the above tasks?")
        else:
            report_lines.append("✅ Architecture is currently fully hardened against all known Sentinel threat intelligence. No pending tasks.")
            report_lines.append("\n> **Recommendation:** Run `/sentinel` to poll for new zero-day advisories.")
            
        return "\n".join(report_lines)

def generate_report():
    auditor = AuditorReport()
    print(auditor.generate_report())

if __name__ == "__main__":
    generate_report()
