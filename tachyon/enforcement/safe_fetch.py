import urllib.request
import urllib.parse
import json
import os
import requests
import time
from typing import List, Optional, Tuple
from dataclasses import dataclass

from tachyon.enforcement.network import NetworkPolicy

@dataclass
class FetchResult:
    """Structured fetch result object (SF-03)."""
    status: str
    url: str
    result: Optional[str] = None
    error: Optional[str] = None
    latency_ms: float = 0.0

class SecurityViolationError(Exception):
    pass

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Custom handler to disable automatic redirects so we can re-verify at each hop."""
    def http_error_301(self, req, fp, code, msg, headers): return None
    def http_error_302(self, req, fp, code, msg, headers): return None
    def http_error_303(self, req, fp, code, msg, headers): return None
    def http_error_307(self, req, fp, code, msg, headers): return None
    def http_error_308(self, req, fp, code, msg, headers): return None

class SafeFetch:
    def __init__(self, agent_id: str = "default", rego_mock=False, allowed_domains=None, denylist=None):
        """
        Initializes the SafeFetch capability firewall.
        Queries the local OPA server to enforce `tool_access.rego`.
        """
        self.agent_id = agent_id
        self.rego_mock = rego_mock
        self.allowed_domains = allowed_domains
        self.denylist = denylist
        self.max_redirects = 3
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
            # 1. Basic URL Validation (H-01)
            if not NetworkPolicy.validate_url(target_url):
                return False

            parsed = urllib.parse.urlparse(target_url)
            domain = parsed.netloc.split(':')[0] # Strip port if present
            
            # 2. DNS-before-connect IP Validation (S-01)
            ips = NetworkPolicy.resolve_safe(domain)
            if not ips:
                return False # Cannot resolve, block by default
            
            for ip in ips:
                if NetworkPolicy.is_ip_private(ip):
                    return False # Block private IP ranges

            # 3. Integrated Supply Chain Whitelist Check (Phase 22 Hardening)
            if not self.rego_mock:
                from tachyon.core.state import StateManager
                if not StateManager().is_package_whitelisted(domain):
                     # Phase 47: Fail-Loud Supply Chain Violation (ADR-0062)
                     msg = f"Unauthorized fetch attempted to domain '{domain}' by agent '{self.agent_id}'. Blocked by Supply Chain Whitelist."
                     StateManager().emit_alert("SUPPLY_CHAIN_VIOLATION", msg)
                     return False

            # 4. Reputation Check (Overrides OPA if score is critical)
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

    def _check_redirect_bypasses(self, url: str) -> bool:
        """Detects open-redirect parameters pointing to untrusted domains (H-05)."""
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        # Common redirect parameters
        redirect_keys = ["url", "q", "dest", "redirect", "goto", "next"]
        for key in redirect_keys:
            if key in params:
                for candidate in params[key]:
                    # If the parameter looks like a URL, check its domain
                    if "://" in candidate or candidate.startswith("//"):
                        inner_parsed = urllib.parse.urlparse(candidate if "://" in candidate else "http:" + candidate)
                        inner_domain = inner_parsed.netloc
                        if not any(inner_domain == d or inner_domain.endswith("." + d) for d in self.mock_allowed):
                             return False
        return True

    def fetch(self, url: str, intent: str = "DEFAULT") -> FetchResult:
        """
        The capability-wrapped fetch command with manual redirect handling.
        Returns a structured FetchResult object (SF-03).
        """
        start_time = time.perf_counter()
        current_url = url
        hops = 0
        
        # We manually handle redirects to ensure EVERY hop is validated (S-01)
        opener = urllib.request.build_opener(NoRedirectHandler())
        
        try:
            while hops <= self.max_redirects:
                # 1. Validate the current URL/IP/Domain
                if not self._evaluate_intent(current_url):
                    raise SecurityViolationError(f"Security Gate blocked access to unauthorized or private host in URL: {current_url}")
                    
                # 2. Open Redirect Parameter Check (H-05)
                if not self._check_redirect_bypasses(current_url):
                    raise SecurityViolationError(f"Redirect parameter to untrusted domain detected in URL: {current_url}")
                
                req = urllib.request.Request(
                    current_url, 
                    headers={'User-Agent': f'Tachyon-Tongs-{self.agent_id}/1.0'}
                )
                
                with opener.open(req, timeout=10) as response:
                    code = response.getcode()
                    
                    # If it's a redirect, get the Location header and loop
                    if code in [301, 302, 303, 307, 308]:
                        new_url = response.headers.get('Location')
                        if not new_url:
                            break
                        # Handle relative URLs
                        current_url = urllib.parse.urljoin(current_url, new_url)
                        hops += 1
                        continue
                    
                    # If it's a success, return content
                    content = response.read().decode('utf-8', errors='ignore')
                    latency = (time.perf_counter() - start_time) * 1000.0
                    return FetchResult(status="SUCCESS", url=current_url, result=content, latency_ms=latency)

            if hops > self.max_redirects:
                raise SecurityViolationError(f"Maximum redirect hops ({self.max_redirects}) exceeded.")
                
        except SecurityViolationError as e:
             latency = (time.perf_counter() - start_time) * 1000.0
             return FetchResult(status="BLOCKED", url=current_url, error=str(e), latency_ms=latency)
        except Exception as e:
             latency = (time.perf_counter() - start_time) * 1000.0
             return FetchResult(status="ERROR", url=current_url, error=str(e), latency_ms=latency)
        
        return FetchResult(status="ERROR", url=url, error="Unknown fetch failure", latency_ms=0.0)

def safe_fetch(url: str, agent_id: str = "default", allowed_domains: list = None, denylist: list = None) -> dict:
    """Convenience wrapper for SafeFetch."""
    fetcher = SafeFetch(agent_id=agent_id, allowed_domains=allowed_domains, denylist=denylist)
    return fetcher.fetch(url)
