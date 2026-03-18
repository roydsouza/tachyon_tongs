import os
from datetime import datetime
from typing import Dict, Any
from tachyon.core.signing import IntegrityManager

class DebateLogger:
    """
    Captures the adversarial discourse between the Triad agents and 
    writes it to timestamped markdown files for forensic review.
    """
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Use absolute path relative to project root (tachyon/utils/debate_logger.py -> project_root/debates)
            this_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(this_dir))
            self.base_dir = os.path.join(project_root, "debates")
        else:
            self.base_dir = base_dir
            
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def log_debate(self, state: Dict[str, Any]):
        """
        Extracts proposal, critique, and verdict from state and writes the log.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cve_id = state.get("cve_context", {}).get("id", "UNKNOWN_THREAT")
        filename = f"DEBATE_{timestamp}_{cve_id}.md"
        filepath = os.path.join(self.base_dir, filename)

        proposal = state.get("patch_files", {})
        critique = state.get("critique", {})
        verdict = state.get("verdict", {})

        with open(filepath, "w") as f:
            f.write(f"# ⚔️ Airlock Debate: {cve_id}\n\n")
            f.write(f"**Timestamp**: {datetime.now().isoformat()}\n")
            f.write(f"**Status**: {verdict.get('status', 'PENDING').upper()}\n\n")

            f.write("## 🏗️ The Engineer's Proposal\n")
            for fname, content in proposal.items():
                f.write(f"### `{fname}`\n")
                f.write(f"```python\n{content}\n```\n\n")

            f.write("## 🧐 The Skeptic's Critique\n")
            f.write(f"> \"{critique.get('banter', 'Your logic is as flimsy as a wet paper towel.')}\"\n\n")
            f.write(f"**Risk Score**: {critique.get('risk_score', 0.0)}\n")
            f.write("**Concerns**:\n")
            for concern in critique.get("concerns", []):
                f.write(f"- {concern}\n")
            f.write("\n")

            f.write("## ⚖️ The Meta-Critic's Arbitration\n")
            f.write(f"> \"{verdict.get('banter', 'Proceed, but be warned: I am watching.')}\"\n\n")
            f.write(f"**Verdict**: {verdict.get('status', 'REJECTED')}\n")
            f.write(f"**Justification**: {verdict.get('justification', 'N/A')}\n")

        # 🔐 Forensic Signing
        try:
            signer = IntegrityManager()
            signer.sign_document(filepath)
        except Exception as e:
            print(f"[DebateLogger] [WARNING] Failed to sign debate log: {e}")

        return filepath
