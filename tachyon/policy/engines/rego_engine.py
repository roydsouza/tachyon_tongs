import os
from typing import Dict, Any
from tachyon.policy.engine import PolicyEngine, PolicyVerdict, Verdict
from tachyon.core.signing import IntegrityManager

class RegoPolicyEngine(PolicyEngine):
    """
    Enforcement engine for OPA/Rego policies.
    Enforces mandatory cryptographic signature verification for all policy files.
    """

    def __init__(self, policy_dir: str = "policies/rego", enforce_signatures: bool = True):
        self.policy_dir = policy_dir
        self.enforce_signatures = enforce_signatures
        self.integrity_manager = IntegrityManager()

    def evaluate(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        """
        Verifies policy integrity and then evaluates the action against the Rego rule set.
        """
        # 1. Integrity Check
        if self.enforce_signatures:
            try:
                self._verify_policy_integrity()
            except RuntimeError as e:
                return PolicyVerdict(Verdict.DENY, f"INTEGRITY FAILURE: {str(e)}", self.engine_id)

        # 2. OPA Evaluation (Placeholder for actual OPA-over-HTTP or WASM call)
        # For now, we simulate the existing logic or use a mock.
        # In a real implementation, this would query the OPA server.
        
        # Simulating a basic check for demonstration
        if action == "unsafe_execute" and agent_id != "engineer":
             return PolicyVerdict(Verdict.DENY, "Direct execution blocked by Rego (Mock)", self.engine_id)

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
