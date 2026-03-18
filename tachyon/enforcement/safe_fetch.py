"""
Tachyon Tongs: Capability Firewall for HTTP Fetching
Implements a strict intent-gate around the standard `urllib.request` library via Open Policy Agent (OPA).
"""
import urllib.request
import urllib.parse
import json
import os
import requests

class SecurityViolationError(Exception):
    pass

class SafeFetch:
    def __init__(self, agent_id: str = "default", rego_mock=True, allowed_domains=None, denylist=None):
        """
        Initializes the SafeFetch capability firewall.
        Queries the local OPA server to enforce `tool_access.rego`.
        """
        self.agent_id = agent_id
        self.rego_mock = rego_mock
        self.allowed_domains = allowed_domains
        self.denylist = denylist
        # Standardized Tachyon Tongs OPA Port is 9181
        self.opa_url = "http://localhost:9181/v1/data/authz/tools/allow_fetch"

        # Load Domain Reputation Config
        self.reputation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../configs/domain_reputation.json"))
        self.reputation_data = {}
        if os.path.exists(self.reputation_path):
            with open(self.reputation_path, "r") as f:
                self.reputation_data = json.load(f)

        # Hardcoded fallback for tests if rego_mock is explicitly True
        self.mock_allowed = ["google.com", "cisa.gov", "github.com", "nvd.nist.gov", "arxiv.org", "huntr.ml", "lmsys.org", "owasp.org"]

    def _evaluate_intent(self, target_url: str) -> bool:
        """Evaluates the payload against the intent policy via OPA and Reputation."""
        try:
            parsed = urllib.parse.urlparse(target_url)
            domain = parsed.netloc
            
            # 1. Reputation Check (Overrides OPA if score is critical)
            if domain in self.reputation_data:
                score = self.reputation_data[domain].get("score", 1.0)
                if score <= 0.3: # Critical threshold for blocking
                    return False

            if self.rego_mock:
                # If we explicitly pass allowed_domains, only check that list in mock mode.
                if self.allowed_domains is not None:
                    return any(domain == d or domain.endswith("." + d) for d in self.allowed_domains)
                
                # Basic pastebin block for simulation
                if domain.endswith("pastebin.com"): return False
                for allowed in self.mock_allowed:
                    if domain == allowed or domain.endswith("." + allowed): return True
                return False

            # Production: Query the real OPA server
            payload = {
                "input": {
                    "agent_id": self.agent_id,
                    "tool": "safe_fetch",
                    "domain": domain,
                    "url": target_url
                }
            }
            if self.allowed_domains is not None:
                payload["input"]["allowed_domains"] = self.allowed_domains
            if self.denylist is not None:
                payload["input"]["malicious_domains"] = self.denylist
            
            response = requests.post(self.opa_url, json=payload, timeout=2)
            if response.status_code == 200:
                result = response.json().get("result", False)
                return result
            else:
                return False
                
        except requests.exceptions.ConnectionError:
            # Fallback to mock if OPA is down and we are in dev mode
            if self.rego_mock:
                return True # Allow for local dev flow if intentional
            return False
        except Exception:
            return False

    def fetch(self, url: str) -> dict:
        """
        The capability-wrapped fetch command.
        Returns a dict with status and content/error.
        """
        if not self._evaluate_intent(url):
            return {
                "status": "BLOCKED",
                "error": f"Intent Gate blocked access to unauthorized domain in URL: {url}"
            }
        
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': f'Tachyon-Tongs-{self.agent_id}/1.0'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return {
                    "status": "SUCCESS",
                    "result": response.read().decode('utf-8', errors='ignore')
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Error fetching URL: {str(e)}"
            }

def safe_fetch(url: str, agent_id: str = "default", allowed_domains: list = None, denylist: list = None) -> dict:
    """Convenience wrapper for SafeFetch."""
    fetcher = SafeFetch(agent_id=agent_id, allowed_domains=allowed_domains, denylist=denylist)
    return fetcher.fetch(url)
