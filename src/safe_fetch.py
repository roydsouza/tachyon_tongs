"""
Tachyon Tongs: Capability Firewall for HTTP Fetching
Implements a strict intent-gate around the standard `urllib.request` library via Open Policy Agent (OPA).
"""
import urllib.request
import urllib.parse
import json
import requests

class SecurityViolationError(Exception):
    pass

class SafeFetch:
    def __init__(self, rego_mock=True, allowed_domains=None):
        """
        Initializes the SafeFetch capability firewall.
        Queries the local OPA server to enforce `tool_access.rego`.
        """
        self.rego_mock = rego_mock
        self.allowed_domains = allowed_domains
        self.opa_url = "http://localhost:9181/v1/data/authz/tools/allow_fetch"

        # Hardcoded fallback for tests if rego_mock is explicitly True
        self.mock_allowed = ["cisa.gov", "github.com", "nvd.nist.gov", "arxiv.org", "huntr.ml", "lmsys.org", "owasp.org"]

    def _evaluate_intent(self, target_url: str) -> bool:
        """Evaluates the payload against the intent policy via OPA."""
        try:
            parsed = urllib.parse.urlparse(target_url)
            domain = parsed.netloc

            if self.rego_mock:
                if domain.endswith("pastebin.com"): return False
                for allowed in self.mock_allowed:
                    if domain == allowed or domain.endswith("." + allowed): return True
                return False

            # Production: Query the real OPA server
            payload = {
                "input": {
                    "tool": "safe_fetch",
                    "domain": domain,
                    "url": target_url
                }
            }
            if self.allowed_domains is not None:
                payload["input"]["allowed_domains"] = self.allowed_domains
            
            response = requests.post(self.opa_url, json=payload, timeout=2)
            if response.status_code == 200:
                result = response.json().get("result", False)
                return result
            else:
                print(f"[SafeFetch] OPA Server returned {response.status_code}. Defaulting to DENY.")
                return False
                
        except requests.exceptions.ConnectionError:
            print("[SafeFetch] FATAL: Could not connect to OPA server at localhost:9181. Access DENIED.")
            return False
        except Exception as e:
            print(f"[SafeFetch] Unexpected intent evaluation error: {str(e)}")
            return False

    def fetch(self, url: str) -> str:
        """
        The capability-wrapped fetch command.
        Will raise a SecurityViolationError if the URL fails the OPA intent gate.
        """
        if not self._evaluate_intent(url):
            raise SecurityViolationError(f"Intent Gate blocked access to unauthorized domain in URL: {url}")
        
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
