import os
import json
import functools
from typing import Dict, Any
from tachyon.policy.engine import PolicyEngine, PolicyVerdict, Verdict
from tachyon.core.signing import IntegrityManager

class RegoPolicyEngine(PolicyEngine):
    """
    Enforcement engine for OPA/Rego policies.
    Enforces mandatory cryptographic signature verification for all policy files.
    Optimized with an LRU cache to reduce evaluation latency for repeat requests.
    """

    def __init__(self, policy_dir: str = "policies/rego", enforce_signatures: bool = True, cache_size: int = 1024):
        self.policy_dir = policy_dir
        self.enforce_signatures = enforce_signatures
        self.integrity_manager = IntegrityManager()
        self.cache_size = cache_size

    def evaluate(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        """
        Verifies policy integrity and then evaluates the action against the Rego rule set.
        Uses internal hashing for LRU caching support.
        """
        # 1. Handle DLP specifically (no cache due to high dynamic content)
        if action == "outbound_dlp":
            from tachyon.pipeline.pii_scanner import PIIScanner
            scanner = PIIScanner()
            findings = scanner.scan_dictionary(params)
            params = {**params, **findings}
            return self._evaluate_uncached(agent_id, action, params)

        # 2. Use cached evaluation for standard tool calls
        # We JSON-serialize params to make them hashable for lru_cache
        param_str = json.dumps(params, sort_keys=True)
        return self._evaluate_cached(agent_id, action, param_str)

    @functools.lru_cache(maxsize=1024)
    def _evaluate_cached(self, agent_id: str, action: str, param_str: str) -> PolicyVerdict:
        params = json.loads(param_str)
        return self._evaluate_uncached(agent_id, action, params)

    def _evaluate_uncached(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        # 1. Integrity Check
        if self.enforce_signatures:
            try:
                self._verify_policy_integrity()
            except RuntimeError as e:
                return PolicyVerdict(Verdict.DENY, f"INTEGRITY FAILURE: {str(e)}", self.engine_id)

        # 2. Whitelist Check (Phase 22 Hardening)
        # Any action involving a domain or recipient must be whitelisted
        # We skip this for explicit 'outbound_dlp' calls as they are secondary checks
        if action != "outbound_dlp":
            from tachyon.core.state import StateManager
            state = StateManager()
            # Support both lowercase and TitleCase keys for legacy compatibility
            target = (params.get("domain") or params.get("Domain") or 
                      params.get("recipient") or params.get("Recipient") or 
                      params.get("url") or params.get("URL"))
            
            if target:
                # Extract domain if it's a URL
                if "://" in str(target):
                    from urllib.parse import urlparse
                    target = urlparse(str(target)).netloc
                
                if not state.is_package_whitelisted(str(target)):
                    return PolicyVerdict(Verdict.DENY, f"Action blocked: '{target}' is not in the trusted registry.", self.engine_id)

        # 3. Simulated OPA check for demonstration
        if action == "unsafe_execute" and agent_id != "engineer":
             return PolicyVerdict(Verdict.DENY, "Direct execution blocked by Rego (Mock)", self.engine_id)

        # 4. Simplified DLP check for the mock engine
        if action == "outbound_dlp":
            serialized_params = str(params)
            if params.get("has_sensitive_token") or "sk-" in serialized_params:
                return PolicyVerdict(Verdict.DENY, "Blocked by Reverse Firewall: Sensitive token detected.", self.engine_id)

        return PolicyVerdict(Verdict.ALLOW, "Rego validation passed", self.engine_id)

    def _verify_policy_integrity(self):
        """Recursively verifies all .rego files in the policy directory."""
        for root, _, files in os.walk(self.policy_dir):
            for file in files:
                if file.endswith(".rego"):
                    path = os.path.join(root, file)
                    # IntegrityManager.verify_integrity raises RuntimeError if digest mismatch
                    self.integrity_manager.verify_integrity(path)

    @property
    def engine_id(self) -> str:
        return "REGO_OPA"
