"""
Tachyon Tongs: Stage 4 Verifier Node
The final defense-in-depth layer. Checks the Analyzer's output for hidden exploits
like Sandbox Escapes or Malicious Markdown links before returning control.
"""
import re

class VerificationFailedError(Exception):
    pass

class VerifierAgent:
    """Stage 4: The Verifier. Evaluates Stage 3 JSON/Dict outputs."""
    
    def __init__(self):
        # Known indicators of compromised LLM output attempting a sandbox escape
        self.banned_substrings = [
            "#!/bin/bash",
            "curl -X POST",
            "import os; os.system"
        ]
        
    def _check_string(self, text: str) -> bool:
        """Helper to scan a single string for banned artifacts."""
        for banned in self.banned_substrings:
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
