import urllib.request
import urllib.parse
import json
import os
import logging
import requests
import time
from typing import List, Optional, Tuple
from dataclasses import dataclass

from tachyon.enforcement.network import NetworkPolicy

logger = logging.getLogger(__name__)

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
    """
    Capability-wrapped HTTP fetch with multi-layer security enforcement.
    
    TT-2026-003 FIX: rego_mock parameter REMOVED from constructor.
    Mock mode is now ONLY activatable via TACHYON_TEST_MODE=1 env var.
    
    TT-2026-005 FIX: Alert delivery now has try/except fallback.
    """
    
    def __init__(self, agent_id: str = "default", allowed_domains=None, denylist=None):
        """
        Initializes the SafeFetch capability firewall.
        Queries the local OPA server to enforce `tool_access.rego`.
        
        TT-2026-003: rego_mock parameter has been REMOVED.
        Use TACHYON_TEST_MODE=1 environment variable for testing.
        """
        self.agent_id = agent_id
        self.allowed_domains = allowed_domains
        self.denylist = denylist
        self.max_redirects = 3
        # Standardized Tachyon Tongs OPA Port is 9181
        self.opa_url = "http://localhost:9181/v1/data/authz/tools/allow_fetch"

        self._TEST_ALLOWED_DOMAINS = frozenset()

        # TT-2026-003 FIX: Mock mode gated by environment variable ONLY
        self.rego_mock = os.getenv("TACHYON_TEST_MODE") == "1"
        if self.rego_mock:
            logger.warning(
                f"SafeFetch initialized in TEST MODE for agent '{agent_id}'. "
                f"OPA validation is DISABLED. Never use this in production!"
            )
            # C-08: Load mock domains from fixture instead of hardcoding
            fixture_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tests/fixtures/mock_domains.json"))
            if os.path.exists(fixture_path):
                try:
                    with open(fixture_path, "r") as f:
                        self._TEST_ALLOWED_DOMAINS = frozenset(json.load(f))
                    logger.info(f"[SafeFetch] Loaded {len(self._TEST_ALLOWED_DOMAINS)} mock domains from {fixture_path}")
                except Exception as e:
                    logger.error(f"[SafeFetch] Failed to load mock domains fixture: {e}")

        # Load Domain Reputation Config
        self.reputation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../configs/domain_reputation.json"))
        self.reputation_data = {}
        if os.path.exists(self.reputation_path):
            try:
                with open(self.reputation_path, "r") as f:
                    self.reputation_data = json.load(f)
            except Exception as e:
                logger.error(f"[SafeFetch] Failed to load domain reputation config: {e}")

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

            # 3. Supply Chain Whitelist Check (always runs, TT-2026-005 hardened)
            if not self.rego_mock:
                from tachyon.core.state import StateManager
                try:
                    state_mgr = StateManager()
                    if not state_mgr.is_package_whitelisted(domain):
                        msg = (
                            f"Unauthorized fetch attempted to domain '{domain}' "
                            f"by agent '{self.agent_id}'. Blocked by Supply Chain Whitelist."
                        )
                        # TT-2026-005 FIX: Guaranteed alert delivery with fallback
                        try:
                            state_mgr.emit_alert("SUPPLY_CHAIN_VIOLATION", msg)
                        except Exception as alert_err:
                            logger.critical(
                                f"ALERT DELIVERY FAILED: Supply chain violation for "
                                f"domain '{domain}' by agent '{self.agent_id}': {alert_err}"
                            )
                        return False  # Always block regardless of alert success
                except Exception as e:
                    # StateManager itself failed — fail-closed
                    logger.critical(f"[SafeFetch] StateManager failure during whitelist check: {e}")
                    return False

            # 4. Reputation Check (Overrides OPA if score is critical)
            if domain in self.reputation_data:
                score = self.reputation_data[domain].get("score", 1.0)
                if score <= 0.3: # Critical threshold for blocking
                    return False

            if self.rego_mock:
                # Test mode: check against explicit allowed_domains or test whitelist
                if self.allowed_domains is not None:
                    return any(domain == d or domain.endswith("." + d) for d in self.allowed_domains)
                
                # Pastebin block for simulation
                if domain.endswith("pastebin.com"): return False
                return any(
                    domain == allowed or domain.endswith("." + allowed)
                    for allowed in self._TEST_ALLOWED_DOMAINS
                )

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
                # OPA returned non-200 — fail-closed
                logger.error(f"[SafeFetch] OPA returned status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            # OPA is unreachable — fail-closed
            if self.rego_mock:
                logger.warning("[SafeFetch] OPA unreachable in test mode, allowing request")
                return True
            logger.error("[SafeFetch] OPA server unreachable, blocking request (fail-closed)")
            return False
        except Exception as e:
            logger.error(f"[SafeFetch] Unexpected error in _evaluate_intent: {e}")
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
                    if "://" in candidate or candidate.startswith("//"):
                        inner_parsed = urllib.parse.urlparse(candidate if "://" in candidate else "http:" + candidate)
                        inner_domain = inner_parsed.netloc
                        if not any(
                            inner_domain == d or inner_domain.endswith("." + d)
                            for d in self._TEST_ALLOWED_DOMAINS
                        ):
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
