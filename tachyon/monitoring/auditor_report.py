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

def read_file_safe(filepath: str) -> str:
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def get_latest_run(log_content: str) -> str:
    """Extracts the most recent run block from RUN_LOG.md."""
    runs = log_content.split("## Run: ")
    if len(runs) < 2:
        return "No execution runs recorded yet."
    
    # Get the last block and strip the trailing horizontal rule
    latest_block = runs[-1].split("---")[0].strip()
    return f"**Latest Sentinel Run:**\nDate/Time: {latest_block}"

def get_pending_tasks(task_content: str) -> list:
    """Extracts all incomplete [ ] tasks from TASKS.md."""
    tasks = []
    for line in task_content.split('\n'):
        if line.strip().startswith("- [ ]"):
            tasks.append(line.strip())
    return tasks

def generate_report():
    print("# 🛡️ Sentinel Auditor Report\n")
    
    # 1. Parse RUN_LOG.md
    log_content = read_file_safe("RUN_LOG.md")
    print(get_latest_run(log_content))
    print("\n---\n")
    
    # 2. Parse TASKS.md
    task_content = read_file_safe("TASKS.md")
    pending_tasks = get_pending_tasks(task_content)
    
    print("### Pending Architectural Enhancements")
    if pending_tasks:
        print("The Sentinel (or prior roadmaps) has proposed the following unresolved defenses:\n")
        for task in pending_tasks:
            print(task)
        print("\n> **Recommendation:** Would you like AntiGravity to begin implementing any of the above tasks?")
    else:
        print("✅ Architecture is currently fully hardened against all known Sentinel threat intelligence. No pending tasks.")
        print("\n> **Recommendation:** Run `/sentinel` to poll for new zero-day advisories.")

if __name__ == "__main__":
    generate_report()
