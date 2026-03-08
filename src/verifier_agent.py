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
        Scans all string values in the Analyzer's output dictionary.
        Raises VerificationFailedError if contamination is found.
        """
        # If the Analyzer already failed intentionally (e.g., due to bounds), pass the error through
        if analyzer_output.get("status") == "error":
            return analyzer_output
            
        # Scan the payload
        for key, value in analyzer_output.items():
            if isinstance(value, str):
                if not self._check_string(value):
                    raise VerificationFailedError(f"Contamination detected in Analyzer output field: {key}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and not self._check_string(item):
                        raise VerificationFailedError(f"Contamination detected in Analyzer output list: {key}")

        # If clean, add a verification seal
        analyzer_output["verified"] = True
        return analyzer_output
