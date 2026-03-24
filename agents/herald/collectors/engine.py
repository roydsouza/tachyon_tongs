import os
import re
from typing import List, Dict, Any

class BaseCollector:
    def collect(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

class FileLogCollector(BaseCollector):
    def __init__(self, filepath: str, pattern: str):
        self.filepath = os.path.abspath(filepath)
        self.pattern = re.compile(pattern)

    def collect(self) -> List[Dict[str, Any]]:
        events = []
        if not os.path.exists(self.filepath):
            return events
            
        with open(self.filepath, "r") as f:
            content = f.read()
            # Split by separator to handle blocks
            blocks = content.split("---")
            for block in blocks:
                match = self.pattern.search(block)
                if match:
                    event_type = match.group(1)
                    if event_type in ["MUTANT_LOCK_ACQUIRED", "MUTANT_LOCK_RELEASED"]:
                        continue # Skip forensic-only lock noise
                        
                    # Phase 30: Filter out development/stress-test noise from the Herald
                    if "STRESS_TEST" in event_type or "PATH_TEST" in event_type:
                        continue
                        
                    timestamp = match.group(2)
                    summary = block.replace(match.group(0), "").strip()
                    
                    # Phase 30: Aesthetic Cleanup - Strip top-level headers and admonition blocks
                    summary_lines = []
                    for line in summary.split("\n"):
                        l = line.strip()
                        if not l or l.startswith("#") or l.startswith("> [!"):
                            continue
                        # If it's a quote block starting a header we already saw, skip
                        if l.startswith(">") and ("CRITICAL SECURITY ALERT" in l or "Tachyon Tongs" in l):
                            continue
                        summary_lines.append(line)
                    summary = "\n".join(summary_lines).strip()
                    
                    # Enhanced Failure Analysis
                    if "Failure" in event_type or "FAILURE" in event_type:
                        summary = self._parse_failure(block, summary)

                    import hashlib
                    # Use stable content (Type + Summary) for the ID, ignoring fluctuating timestamps/formatting
                    # This ensures that a repair for a specific failure is recognized as the same 'event'
                    stable_id_str = f"{event_type}:{summary.split('**Implications**')[0].strip()}"
                    event_id = hashlib.md5(stable_id_str.encode()).hexdigest()
                    
                    events.append({
                        "id": event_id,
                        "type": event_type,
                        "timestamp": timestamp,
                        "summary": summary,
                        "source": os.path.basename(self.filepath)
                    })
        return events

    def _parse_failure(self, block: str, raw_summary: str) -> str:
        """Extract implications and remediation from failure blocks."""
        analysis = raw_summary
        if "REMEDIATION:" in block:
            # Already structured
            return raw_summary
        
        # Heuristic analysis for unstructured legacy failures
        if "No such file or directory" in raw_summary:
            analysis += "\n\n**Implications**: Critical components or logs are missing; agents cannot verify state."
            analysis += "\n**Remediation**: Check substrate integrity via `tt status` and ensure all directories exist."
        return analysis

class AirlockCollector(BaseCollector):
    def collect(self) -> List[Dict[str, Any]]:
        from tachyon.core.state import StateManager
        state = StateManager()
        patches = state.get_pending_patches()
        return [{
            "id": f"patch:{p['id']}",
            "type": "AIRLOCK_PENDING",
            "summary": p['summary'],
            "cve_id": p['cve_id'],
            "source": "Airlock"
        } for p in patches]

class TaskCollector(BaseCollector):
    def __init__(self, tasks_file: str):
        self.tasks_file = os.path.abspath(tasks_file)

    def collect(self) -> List[Dict[str, Any]]:
        events = []
        if not os.path.exists(self.tasks_file):
            return events
            
        with open(self.tasks_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.strip().startswith("- [ ]") and "HITL" in line:
                    import hashlib
                    event_id = hashlib.md5(line.strip().encode()).hexdigest()
                    events.append({
                        "id": event_id,
                        "type": "HITL_TASK",
                        "summary": line.strip()[6:],
                        "source": "TASKS.md"
                    })
        return events
class ForensicCollector(BaseCollector):
    def collect(self) -> List[Dict[str, Any]]:
        from tachyon.core.forensics import ForensicStore
        store = ForensicStore()
        # Fetch latest 20 high-signal forensic events
        rows = store.query_latest(limit=20)
        events = []
        for row in rows:
            events.append({
                "id": f"forensic:{row['id']}",
                "type": row['event_type'],
                "timestamp": row['timestamp'],
                "summary": f"{row['action']} -> {row['status']}\n{row['details']}",
                "source": f"ForensicLedger:{row['agent_id']}"
            })
        return events
