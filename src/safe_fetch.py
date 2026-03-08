"""
Tachyon Tongs: Capability Firewall for HTTP Fetching
Implements a strict intent-gate around the standard `urllib.request` library.
"""
import urllib.request
import urllib.parse
import json

class SecurityViolationError(Exception):
    pass

class SafeFetch:
    def __init__(self, rego_mock=True):
        """
        Initializes the SafeFetch capability firewall.
        In a production environment, this would call out to an Open Policy Agent (OPA) server.
        For this prototype (rego_mock=True), we evaluate a simple Python equivalent of our tool_access.rego.
        """
        self.rego_mock = rego_mock
        self.allowed_domains = [
            "cisa.gov",
            "github.com",
            "nvd.nist.gov",
            "arxiv.org",
            "huntr.ml",
            "lmsys.org"
        ]

    def _evaluate_intent(self, target_url: str) -> bool:
        """Evaluates the payload against the intent policy."""
        try:
            parsed = urllib.parse.urlparse(target_url)
            domain = parsed.netloc

            # Check explicit denies
            if domain.endswith("pastebin.com"):
                return False

            # Check allows
            for allowed in self.allowed_domains:
                if domain == allowed or domain.endswith("." + allowed):
                    return True
            return False
        except Exception:
            return False

    def fetch(self, url: str) -> str:
        """
        The capability-wrapped fetch command.
        Will raise a SecurityViolationError if the URL fails the intent gate.
        """
        if not self._evaluate_intent(url):
            raise SecurityViolationError(f"Intent Gate blocked access to unauthorized domain in URL: {url}")
        
        # If authorized, execute the internal request (simulated for tests if needed)
        # We use a user-agent to prevent basic blocks from academic sites
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Tachyon-Tongs-Sentinel-Bot/1.0'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return f"Error fetching URL: {str(e)}"
