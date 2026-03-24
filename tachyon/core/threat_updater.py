import os
import sqlite3
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

class ThreatModelUpdater:
    """
    Autonomously propagates adversarial findings from forensics into THREAT_MODEL.md.
    Links Pathogen/Sentinel discoveries to formal ASI categories.
    """
    def __init__(self, db_path: Optional[str] = None, threat_model_path: Optional[str] = None):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.db_path = db_path or os.path.join(root_dir, "memory", "operational", "forensics.db")
        self.threat_model_path = threat_model_path or os.path.join(root_dir, "docs", "THREAT_MODEL.md")
        
        from .signing import IntegrityManager
        self.integrity = IntegrityManager()

    def propagate_findings(self) -> int:
        """Query forensics and update THREAT_MODEL.md sections."""
        if not os.path.exists(self.threat_model_path):
             print(f"[Updater] ALERT: Threat model not found at {self.threat_model_path}")
             return 0
             
        # 1. Fetch raw findings (Pathogen Breaches or Sentinel Discoveries)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM forensic_log WHERE event_type IN (?, ?) ORDER BY id ASC",
                ("PATHOGEN_BREACH", "SENTINEL_DISCOVERY")
            )
            findings = [dict(row) for row in cursor]
            
        if not findings:
            return 0
            
        print(f"[*] Found {len(findings)} new findings to propagate.")
        
        # 2. Iterate and Inject
        updates_count = 0
        for f in findings:
            details = json.loads(f["details"])
            asi_id = details.get("asi_id", "ASI-UNKNOWN")
            forensic_uri = f"forensic:{f['id']}"
            
            # Prepare the Markdown entry
            entry = f"\n- [FORENSIC] {f['timestamp']} | **Discovery**: {details.get('summary', 'No summary')} | [Source]({forensic_uri})"
            
            if self._inject_into_section(asi_id, entry):
                updates_count += 1
                
        # 3. Final Re-sign
        if updates_count > 0:
            self.integrity.sign_document(self.threat_model_path)
            
        return updates_count

    def _inject_into_section(self, asi_id: str, entry: str) -> bool:
        """Injects an entry into the specific ASI section of THREAT_MODEL.md."""
        with open(self.threat_model_path, "r") as f:
            content = f.read()
            
        # Look for the section header, e.g., "### [ASI-01] ..."
        # regex to find the section and inject before the next header or end of file
        pattern = rf"(### \[{asi_id}\].*?)(?=\n### |$)"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            # Fallback to general evidence section if ASI not found
            pattern = r"(## Adversarial Evidence.*?)(?=\n## |$)"
            match = re.search(pattern, content, re.DOTALL)
            
        if match:
            section_content = match.group(0)
            if entry in section_content:
                return False # Avoid duplicates
                
            new_section = section_content.strip() + entry
            new_content = content.replace(section_content, new_section + "\n")
            
            with open(self.threat_model_path, "w") as f:
                f.write(new_content)
            return True
        
        return False
