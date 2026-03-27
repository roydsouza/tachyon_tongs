import re
from typing import Any, Dict
from agents._core.base import BaseAgentPlugin
from agents._core.registry import AgentRegistry

class VerificationFailedError(Exception):
    """Raised when the VerifierAgent detects contamination (SF-02, SF-01)."""
    pass

@AgentRegistry.register("verifier")
class VerifierAgent(BaseAgentPlugin):
    """
    Verifier Agent: Implements recursive forensic scans on payloads (M-04).
    Standardized to raise VerificationFailedError on failure (SF-02).
    """
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "Verifier", config)
        self.banned_patterns = [
            "rm -rf", "chmod 777", "powershell", "curl", "wget", "/etc/passwd",
            "netcat", "nc -e", "/dev/tcp", "os.system", "subprocess.run",
            "#!/bin/bash", "cat /etc/shadow"
        ]
        
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Provides high-assurance verification as an agent action."""
        if action == "verify_data":
            try:
                self.verify(parameters.get("payload", {}))
                return {"status": "SUCCESS", "verified": True}
            except VerificationFailedError as e:
                return {"status": "DENIED", "error": str(e)}
        return {"status": "ERROR", "error": f"Unknown action: {action}"}

    def _check_string(self, text: str) -> bool:
        """Helper to scan a single string for banned artifacts."""
        for banned in self.banned_patterns: # Changed from banned_substrings to banned_patterns
            if banned in text:
                return False
                
        # Regex to catch markdown links pointing to unapproved executable drops
        # e.g., [click here](http://malicious.com/payload.sh)
        # This is a basic heuristic for the prototype
        if re.search(r'\[.*?\]\(http.*?\.(sh|py|exe|elf)\)', text, re.IGNORECASE):
            return False
            
        return True

    def verify(self, analyzer_output: dict) -> dict:
        """
        Scans all values in the Analyzer's output recursively (M-04).
        Raises VerificationFailedError if contamination is found.
        """
        if analyzer_output.get("status") == "error":
            return analyzer_output
            
        def _recursive_scan(data: Any, path: str = ""):
            if isinstance(data, str):
                if not self._check_string(data):
                    raise VerificationFailedError(f"Contamination detected in Analyzer output field: {path}")
            elif isinstance(data, dict):
                for k, v in data.items():
                    _recursive_scan(v, f"{path}.{k}" if path else k)
            elif isinstance(data, list):
                for i, v in enumerate(data):
                    _recursive_scan(v, f"{path}[{i}]")

        # Start the recursive scan
        _recursive_scan(analyzer_output)

        # If clean, add a verification seal
        analyzer_output["verified"] = True
        return analyzer_output

# Alias for compatibility
VerifierNode = VerifierAgent
