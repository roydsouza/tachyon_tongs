import os
import json
import functools
from typing import Dict, Any, Optional
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

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Snapshots all policy file hashes for TOCTOU verification."""
        snapshot = {}
        if os.path.exists(self.policy_dir):
            for root, _, files in os.walk(self.policy_dir):
                for file in files:
                    if file.endswith(".rego"):
                        path = os.path.join(root, file)
                        snapshot[path] = self.integrity_manager.get_file_hash(path)
        return snapshot

    async def evaluate(self, agent_id: str, action: str, params: Dict[str, Any], snapshot: Optional[Dict[str, Any]] = None) -> PolicyVerdict:
        """
        Verifies policy integrity and then evaluates the action against the Rego rule set.
        If a snapshot is provided, it verifies that the current file hashes match the snapshot.
        """
        # TOC/TOU Verification
        if snapshot:
            for path, expected_hash in snapshot.items():
                if not os.path.exists(path):
                    return PolicyVerdict(Verdict.DENY, f"TOCTOU VIOLATION: Policy file {path} vanished.", self.engine_id)
                current_hash = self.integrity_manager.get_file_hash(path)
                if current_hash != expected_hash:
                    return PolicyVerdict(Verdict.DENY, f"TOCTOU VIOLATION: Policy file {path} modified during evaluation.", self.engine_id)

        # 1. Handle DLP specifically (no cache due to high dynamic content)
        if action == "outbound_dlp":
            from tachyon.pipeline.pii_scanner import PIIScanner
            scanner = PIIScanner()
            findings = scanner.scan_dictionary(params)
            params = {**params, **findings}
            # Skip whitelist for internal DLP checks
            return self._evaluate_uncached(agent_id, action, params, skip_whitelist=True)

        # 2. For send_message, we MUST also check outbound_dlp internally
        if action == "send_message":
            # Pass 1: Primary action (send_message) check
            verdict = self._evaluate_uncached(agent_id, action, params)
            if verdict.verdict == Verdict.DENY:
                return verdict
            
            # Pass 2: Secondary content (outbound_dlp) check
            return await self.evaluate(agent_id, "outbound_dlp", params)

        # 3. Use cached evaluation for standard tool calls
        # C-03: Prune attacker-controlled noise parameters before caching
        normalized_params = self._normalize_cache_params(params)
        param_str = json.dumps(normalized_params, sort_keys=True)
        return self._evaluate_cached(agent_id, action, param_str)

    def _normalize_cache_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prunes non-security-relevant keys to prevent cache poisoning DoS."""
        # Security-critical parameters that impact policy verdicts
        SECURITY_KEYS = {
            "url", "domain", "Domain", "URL",
            "recipient", "Recipient",
            "package", "package_name",
            "command", "args",
            "access_type", "resource_id"
        }
        return {k: v for k, v in params.items() if k in SECURITY_KEYS}

    @functools.lru_cache(maxsize=1024)
    def _evaluate_cached(self, agent_id: str, action: str, param_str: str) -> PolicyVerdict:
        params = json.loads(param_str)
        return self._evaluate_uncached(agent_id, action, params)

    def _evaluate_uncached(self, agent_id: str, action: str, params: Dict[str, Any], skip_whitelist: bool = False) -> PolicyVerdict:
        # 1. Integrity Check
        if self.enforce_signatures:
            try:
                self._verify_policy_integrity()
            except RuntimeError as e:
                return PolicyVerdict(Verdict.DENY, f"INTEGRITY FAILURE: {str(e)}", self.engine_id)

        # 2. Whitelist Check (Phase 22 Hardening)
        if not skip_whitelist:
            from tachyon.core.state import StateManager
            state = StateManager()
            target = (params.get("domain") or params.get("Domain") or 
                      params.get("recipient") or params.get("Recipient") or 
                      params.get("url") or params.get("URL"))

            
            if target:
                target_str = str(target)
                # Extract domain if it's a URL
                if "://" in target_str:
                    from urllib.parse import urlparse
                    target_str = urlparse(target_str).netloc
                
                if not state.is_package_whitelisted(target_str):
                    return PolicyVerdict(Verdict.DENY, f"Action blocked: '{target_str}' is not in the trusted registry.", self.engine_id)

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
        if not os.path.exists(self.policy_dir):
            return
            
        for root, _, files in os.walk(self.policy_dir):
            for file in files:
                if file.endswith(".rego"):
                    path = os.path.join(root, file)
                    sig_path = path + ".sig"
                    
                    if not os.path.exists(sig_path):
                        raise RuntimeError(f"Missing mandatory signature sidecar: {file}.sig")
                        
                    # IntegrityManager.verify_integrity returns False if mismatch
                    if not self.integrity_manager.verify_integrity(path):
                        raise RuntimeError(f"Integrity check failed for {file}")

    @property
    def engine_id(self) -> str:
        return "REGO_OPA"
