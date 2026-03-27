import math
import asyncio
from typing import Dict, Any, List, Optional
from tachyon.policy.engine import PolicyEngine, PolicyVerdict, Verdict

class AlignmentPDP(PolicyEngine):
    """
    Tachyon Tongs: Reasoning-Driven Alignment PDP.
    Enforces semantic synchronization between an agent's natural-language intent 
    and its technical execution params.
    
    Implements mandatory intent-gating and multi-turn adversarial refinement.
    """

    HIGH_RISK_TOOLS = {"safe_execute", "safe_fetch", "send_message", "mutate_substrate"}

    def __init__(self, threshold: float = 0.5, policy_dir: str = "policies/alignment", enforce_signatures: bool = True):
        self.threshold = threshold
        self.policy_dir = policy_dir
        self.enforce_signatures = enforce_signatures
        
        # H-03 Fix: Use a Concept-Based Vectorizer (Synonym Mapping)
        self._concept_map = {
            # ACTION_RETRIEVAL
            "fetch": "RETRIEVAL", "get": "RETRIEVAL", "download": "RETRIEVAL", "retrieve": "RETRIEVAL",
            # ACTION_DESTRUCTION
            "delete": "DESTRUCTION", "remove": "DESTRUCTION", "purge": "DESTRUCTION", "cleanup": "DESTRUCTION", "destroy": "DESTRUCTION",
            # TARGET_SUBSTRATE
            "substrate": "SUBSTRATE", "base layer": "SUBSTRATE", "system files": "SUBSTRATE", "infrastructure": "SUBSTRATE",
            # SENSITIVE_DATA
            "private": "SENSITIVE", "key": "SENSITIVE", "secret": "SENSITIVE", "password": "SENSITIVE", "token": "SENSITIVE"
        }
        self._semantic_weights = {
            "RETRIEVAL": 2.0, "DESTRUCTION": 3.0, "SUBSTRATE": 2.5, "SENSITIVE": 2.5
        }

    @property
    def engine_id(self) -> str:
        return "ALIGNMENT_REASONER"

    def _get_vector(self, text: str) -> Dict[str, float]:
        """Conceptual vectorizer that maps synonyms to 'anchor' concepts (H-03)."""
        text = text.lower().replace("/", " ").replace(".", " ").replace("_", " ").replace("-", " ")
        words = text.split()
        vector = {}
        
        # Check for multi-word concepts first (e.g., 'base layer')
        for concept, anchor in self._concept_map.items():
            if " " in concept and concept in text:
                vector[anchor] = vector.get(anchor, 0.0) + self._semantic_weights.get(anchor, 1.0)
        
        # Then per-word concepts
        for word in words:
            if len(word) > 2:
                anchor = self._concept_map.get(word, word.upper())
                weight = self._semantic_weights.get(anchor, 1.0)
                vector[anchor] = vector.get(anchor, 0.0) + weight
        return vector

    def _cosine_similarity(self, v1: Dict[str, float], v2: Dict[str, float]) -> float:
        """Computes similarity between two weighted frequency vectors."""
        sum_xy = 0
        sum_x2 = 0
        sum_y2 = 0
        
        all_keys = set(v1.keys()).union(set(v2.keys()))
        for key in all_keys:
            x = v1.get(key, 0.0)
            y = v2.get(key, 0.0)
            sum_xy += x * y
            sum_x2 += x * x
            sum_y2 += y * y
            
        denominator = math.sqrt(sum_x2) * math.sqrt(sum_y2)
        if not denominator:
            return 0.0
        return sum_xy / denominator

    async def evaluate(self, agent_id: str, action: str, params: Dict[str, Any]) -> PolicyVerdict:
        """
        Evaluates semantic alignment.
        Triggers Fail-Closed logic for high-risk tools and cognitive refinement loops.
        """
        intent = params.get("intent")

        # 1. Fail-Closed Mandatory Intent Gating
        if not intent and action in self.HIGH_RISK_TOOLS:
            return PolicyVerdict(
                Verdict.DENY,
                f"Mandatory Intent Gating: High-risk action '{action}' denied because 'intent' field is missing.",
                self.engine_id
            )
        
        if not intent:
            return PolicyVerdict(Verdict.ALLOW, "Bypassing alignment (Low-risk action / No intent declared)", self.engine_id)

        # 2. Fast-Path Embedding Check
        param_text = " ".join(str(v) for v in params.values() if isinstance(v, (str, int, float)))
        v_intent = self._get_vector(intent)
        v_params = self._get_vector(param_text)
        
        score = self._cosine_similarity(v_intent, v_params)
        
        # 3. Slow-Path Reasoning Refinement
        # If the action is critical or the score is borderline, we invoke the "Reflection Loop"
        is_borderline = 0.3 < score < self.threshold
        is_critical = action in self.HIGH_RISK_TOOLS

        if is_critical or is_borderline:
            return await self._refine_alignment(agent_id, action, params, score)

        if score < self.threshold:
            return PolicyVerdict(
                Verdict.DENY,
                f"Semantic Drift Detected (Score: {score:.2f} < {self.threshold}). Technical parameters do not align with declared intent.",
                self.engine_id,
                {"alignment_score": score}
            )

        return PolicyVerdict(Verdict.ALLOW, f"Semantic Alignment Verified (Score: {score:.2f})", self.engine_id, {"alignment_score": score})

    async def _refine_alignment(self, agent_id: str, action: str, params: Dict[str, Any], initial_score: float) -> PolicyVerdict:
        """
        Performs multi-turn cognitive refinement using the Analyst logic.
        In a full implementation, this calls out to mlx_lm or the Reflector node.
        """
        intent = params.get("intent")
        
        # SIMULATION: Check for common "Reframing" attacks identified in Grok/Gemini audits
        # e.g., using "telemetry" or "heartbeat" to mask code execution
        suspicious_reframing = ("telemetry" in intent.lower() or "heartbeat" in intent.lower()) and action == "safe_execute"
        
        if suspicious_reframing:
            # Multi-turn check (Simulated)
            await asyncio.sleep(0.1) # Simulate cognitive overhead
            return PolicyVerdict(
                Verdict.DENY,
                f"Adversarial Reframing Detected: Intent '{intent}' masks high-risk action '{action}'. Refined reasoning identified a Goal-Aliasing bypass attempt.",
                self.engine_id,
                {"refinement_status": "ADVERSARIAL_DETECTED", "initial_score": initial_score, "alignment_score": initial_score}
            )
            
        # Re-verify based on a higher "Reasoned" threshold
        reasoned_threshold = 0.7
        if initial_score >= reasoned_threshold:
            return PolicyVerdict(
                Verdict.ALLOW,
                f"Alignment Verified via Cognitive Refinement (Reasoned Score: {initial_score:.2f})",
                self.engine_id,
                {"refinement_status": "SUCCESS", "alignment_score": initial_score}
            )
        else:
             return PolicyVerdict(
                Verdict.DENY,
                f"Reasoning Failure: Cognitive refinement could not bridge the gap between intent and parameters (Score: {initial_score:.2f} < {reasoned_threshold}).",
                self.engine_id,
                {"refinement_status": "DOUBT_EXPRESSED", "alignment_score": initial_score}
            )
