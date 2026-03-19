import os
import re
import json
from datetime import datetime
from typing import Dict, Any, List
from tachyon.agents.roles import EngineerRole

class ImmuneManager:
    """
    Orchestrates the autonomic feedback loop between the Canary and the Engineer.
    """
    def __init__(self, agent_id: str = "immune-system"):
        self.agent_id = agent_id
        self.canary_log = "memory/strategic/CANARY_LOG.md"
        self.engineer = EngineerRole(f"{agent_id}-engineer")
        self.evolution_ledger = "memory/strategic/EVOLUTION.md"

    def scan_and_evolve(self) -> Dict[str, Any]:
        """
        Scans the Canary Log for bypasses and triggers the Engineer to evolve a fix.
        """
        if not os.path.exists(self.canary_log):
            return {"status": "IDLE", "reason": "No canary log found"}

        bypasses = self._get_latest_bypasses()
        if not bypasses:
            return {"status": "IDLE", "reason": "No bypasses detected in Canary Log"}

        results = []
        for bypass in bypasses:
            print(f"[*] ImmuneSystem: Detected bypass {bypass['id']}. Initiating evolution...")
            evolution_result = self._evolve_fix(bypass)
            results.append(evolution_result)

        return {
            "status": "SUCCESS",
            "evolutions_triggered": len(results),
            "details": results
        }

    def _get_latest_bypasses(self) -> List[Dict[str, str]]:
        """
        Parses CANARY_LOG.md for entries with STATUS: BYPASSED.
        """
        bypasses = []
        try:
            with open(self.canary_log, "r") as f:
                content = f.read()
            
            # Matches: ### [TIMESTAMP] ID | STATUS: BYPASSED
            # Followed by - **Payload**: `...`
            pattern = r"### \[(.*?)\] (.*?) \| STATUS: BYPASSED\n- \*\*Payload\*\*: `(.*?)`"
            matches = re.finditer(pattern, content)
            
            for match in matches:
                bypasses.append({
                    "timestamp": match.group(1),
                    "id": match.group(2),
                    "payload": match.group(3)
                })
        except Exception as e:
            print(f"[!] Error parsing Canary Log: {e}")
            
        return bypasses

    def _evolve_fix(self, bypass: Dict[str, str]) -> Dict[str, Any]:
        """
        Triggers the Engineer to generate a policy update.
        """
        params = {
            "cve_id": f"AUTO-{bypass['id']}",
            "description": f"Autonomic fix for detected bypass in Canary: {bypass['payload']}",
            "action": "evolve_policy",
            "context": {
                "bypass_payload": bypass["payload"],
                "source": "CanaryHoneypot"
            }
        }
        
        # Trigger the Engineer action
        result = self.engineer.handle_action("apply_and_test", params)
        
        # The EngineerRole returns a success wrapper; we need the inner 'result'
        inner_result = result.get("result", {})
        
        return {
            "threat_id": bypass["id"],
            "engineer_status": inner_result.get("status", "unknown"),
            "proposal_path": inner_result.get("proposal_path")
        }

if __name__ == "__main__":
    manager = ImmuneManager()
    print(json.dumps(manager.scan_and_evolve(), indent=2))
