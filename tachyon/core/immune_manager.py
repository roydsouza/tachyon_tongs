import os
import re
import json
from datetime import datetime
from typing import Dict, Any, List
from tachyon.agents.roles import EngineerRole
from tachyon.core.state import StateManager

class ImmuneManager:
    """
    Orchestrates the autonomic feedback loop between the Canary and the Engineer.
    """
    def __init__(self, agent_id: str = "immune-system"):
        self.agent_id = agent_id
        self.canary_log = "memory/strategic/CANARY_LOG.md"
        self.evolution_ledger = "memory/strategic/EVOLUTION.md"
        self.state = StateManager()
        self.engineer = EngineerRole(f"{agent_id}-engineer")

    def scan_and_evolve(self) -> Dict[str, Any]:
        """
        Scans the Canary Log for bypasses and triggers the Engineer to evolve a fix.
        """
        if not os.path.exists(self.canary_log):
            return {"status": "IDLE", "reason": "No canary log found"}

        bypasses = self._get_latest_bypasses()
        if not bypasses:
            return {"status": "IDLE", "reason": "No unprocessed bypasses detected"}

        results = []
        for bypass in bypasses:
            # Check if already processed
            if self.state.is_event_processed(bypass["id"]):
                continue

            print(f"[*] ImmuneSystem: Detected bypass {bypass['id']}. Initiating evolution...")
            evolution_result = self._evolve_fix(bypass)
            
            if evolution_result.get("engineer_status") == "staged":
                self.state.mark_event_processed(bypass["id"], "CanaryHoneypot", "STAGED")
                self.state.log_evolution(
                    "Autonomic Evolution",
                    f"Mitigated bypass {bypass['id']} via synthesized Rego policy. Proposal staged in Airlock."
                )
            
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
            pattern = r"### \[(.*?)\] (.*?) \| STATUS: BYPASSED\n- \*\*Payload\*\*: `(.*?)`"
            matches = re.finditer(pattern, content)
            
            for match in matches:
                event_id = f"{match.group(2)}-{match.group(1)}" # ID + Timestamp for uniqueness
                if not self.state.is_event_processed(event_id):
                    bypasses.append({
                        "timestamp": match.group(1),
                        "id": event_id,
                        "raw_id": match.group(2),
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
            "cve_id": f"AUTO-{bypass['raw_id']}",
            "description": f"Autonomic fix for detected bypass in Canary: {bypass['payload']}",
            "action": "evolve_policy",
            "context": {
                "bypass_payload": bypass["payload"],
                "source": "CanaryHoneypot"
            }
        }
        
        # Trigger the Engineer action
        result = self.engineer.handle_action("apply_and_test", params)
        inner_result = result.get("result", {})
        
        return {
            "threat_id": bypass["id"],
            "engineer_status": inner_result.get("status", "unknown"),
            "proposal_path": inner_result.get("proposal_path")
        }

if __name__ == "__main__":
    manager = ImmuneManager()
    print(json.dumps(manager.scan_and_evolve(), indent=2))
