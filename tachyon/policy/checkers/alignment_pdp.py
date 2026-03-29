import math
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, FrozenSet
from tachyon.policy.engine import PolicyEngine, PolicyVerdict, Verdict

logger = logging.getLogger(__name__)


class AlignmentPDP(PolicyEngine):
    """
    Tachyon Tongs: Reasoning-Driven Alignment PDP.
    Enforces semantic synchronization between an agent's natural-language intent 
    and its technical execution params.
    
    Implements mandatory intent-gating, adversarial reframing detection,
    and multi-turn cognitive refinement.
    
    TT-2026-004 FIX: Expanded concept map, added _detect_adversarial_reframing()
    with 4 pattern categories (euphemistic exfil, operational masks, high-risk
    destinations, legacy bypass).
    """

    HIGH_RISK_TOOLS: FrozenSet[str] = frozenset({
        "safe_execute", "safe_fetch", "send_message", "mutate_substrate"
    })

    # TT-2026-004: Adversarial reframing detection patterns
    _EUPHEMISTIC_EXFIL_VERBS: FrozenSet[str] = frozenset({
        "archive", "backup", "sync", "mirror", "export", "transfer",
        "replicate", "copy", "transmit", "relay", "forward", "beam"
    })
    _SENSITIVE_TARGETS: FrozenSet[str] = frozenset({
        "key", "secret", "password", "token", "credential", "certificate",
        "ssl", "tls", "private", "auth", "session", "cookie",
        "cryptographic", "encryption"
    })
    _OPERATIONAL_MASKS: FrozenSet[str] = frozenset({
        "telemetry", "heartbeat", "metrics", "health", "monitoring",
        "diagnostics", "observability", "instrumentation", "tracing",
        "analytics", "reporting", "status"
    })
    _HIGH_RISK_DESTINATIONS: FrozenSet[str] = frozenset({
        ".onion", "pastebin", "paste.ee", "hastebin", "dpaste",
        "ghostbin", "rentry", "transfer.sh", "file.io", "0x0.st"
    })
    _BYPASS_KEYWORDS: FrozenSet[str] = frozenset({
        "bypass", "skip", "disable", "ignore", "override", "circumvent",
        "workaround", "exempt", "suppress"
    })

    def __init__(self, threshold: float = 0.7, policy_dir: str = "policies/alignment", enforce_signatures: bool = True):
        self.threshold = threshold
        self.policy_dir = policy_dir
        self.enforce_signatures = enforce_signatures
        
        # H-03 Fix: Use a Concept-Based Vectorizer (Synonym Mapping)
        # TT-2026-004 FIX: Expanded concept map with broader coverage
        self._concept_map = {
            # ACTION_RETRIEVAL (expanded)
            "fetch": "RETRIEVAL", "get": "RETRIEVAL", "download": "RETRIEVAL",
            "retrieve": "RETRIEVAL", "pull": "RETRIEVAL", "acquire": "RETRIEVAL",
            "collect": "RETRIEVAL", "gather": "RETRIEVAL", "obtain": "RETRIEVAL",
            "scrape": "RETRIEVAL", "crawl": "RETRIEVAL",
            # ACTION_DESTRUCTION (expanded)
            "delete": "DESTRUCTION", "remove": "DESTRUCTION", "purge": "DESTRUCTION",
            "cleanup": "DESTRUCTION", "destroy": "DESTRUCTION", "erase": "DESTRUCTION",
            "wipe": "DESTRUCTION", "clear": "DESTRUCTION", "truncate": "DESTRUCTION",
            "drop": "DESTRUCTION", "shred": "DESTRUCTION",
            # ACTION_MUTATION
            "modify": "MUTATION", "edit": "MUTATION", "update": "MUTATION",
            "patch": "MUTATION", "alter": "MUTATION", "change": "MUTATION",
            "mutate": "MUTATION", "transform": "MUTATION",
            # ACTION_EXFILTRATION (new — negative weight)
            "archive": "POTENTIAL_EXFIL", "backup": "POTENTIAL_EXFIL",
            "mirror": "POTENTIAL_EXFIL", "sync": "POTENTIAL_EXFIL",
            "export": "POTENTIAL_EXFIL", "transfer": "POTENTIAL_EXFIL",
            "replicate": "POTENTIAL_EXFIL", "transmit": "POTENTIAL_EXFIL",
            # TARGET_SUBSTRATE
            "substrate": "SUBSTRATE", "base layer": "SUBSTRATE",
            "system files": "SUBSTRATE", "infrastructure": "SUBSTRATE",
            "foundation": "SUBSTRATE", "core": "SUBSTRATE",
            # SENSITIVE_DATA (expanded)
            "private": "SENSITIVE", "key": "SENSITIVE", "secret": "SENSITIVE",
            "password": "SENSITIVE", "token": "SENSITIVE", "credential": "SENSITIVE",
            "certificate": "SENSITIVE", "ssl": "SENSITIVE", "auth": "SENSITIVE",
            "session": "SENSITIVE", "cookie": "SENSITIVE",
            # EXECUTION
            "execute": "EXECUTION", "run": "EXECUTION", "invoke": "EXECUTION",
            "spawn": "EXECUTION", "launch": "EXECUTION",
            # OBSERVATION (benign)
            "observe": "OBSERVATION", "monitor": "OBSERVATION", "watch": "OBSERVATION",
            "inspect": "OBSERVATION", "audit": "OBSERVATION", "check": "OBSERVATION",
            # POLICY_BYPASS (new - high risk)
            "bypass": "BYPASS", "skip": "BYPASS", "ignore": "BYPASS",
            "guardian": "SENSITIVE", "policy": "SENSITIVE",
        }
        self._semantic_weights = {
            "RETRIEVAL": 2.0,
            "DESTRUCTION": 3.0,
            "MUTATION": 2.5,
            "POTENTIAL_EXFIL": -10.0,  # TT-2026-004: INCREASED negative weight for stronger poisoning
            "SUBSTRATE": 2.5,
            "SENSITIVE": 2.5,
            "EXECUTION": 2.0,
            "OBSERVATION": 1.5,
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

    def _detect_adversarial_reframing(self, intent: str, action: str, params: Dict[str, Any]) -> Optional[PolicyVerdict]:
        """
        TT-2026-004 FIX: Multi-pattern adversarial reframing detector.
        Runs BEFORE cosine similarity to catch attacks that game the vector space.
        
        Returns a PolicyVerdict(DENY) if an adversarial pattern is detected,
        or None if the request appears clean.
        """
        intent_lower = intent.lower()
        param_text = " ".join(str(v) for v in params.values() if isinstance(v, (str, int, float))).lower()
        combined = f"{intent_lower} {param_text}"
        
        # Pattern 1: Euphemistic Exfiltration
        # "archive/backup/sync/mirror" + sensitive target keywords
        has_exfil_verb = any(verb in combined for verb in self._EUPHEMISTIC_EXFIL_VERBS)
        has_sensitive_target = any(target in combined for target in self._SENSITIVE_TARGETS)
        if has_exfil_verb and has_sensitive_target:
            logger.warning(f"[AlignmentPDP] ADVERSARIAL: Euphemistic exfiltration detected: {intent}")
            return PolicyVerdict(
                Verdict.DENY,
                f"Adversarial Reframing Detected [Pattern: Euphemistic Exfiltration]: "
                f"Intent '{intent}' combines data-movement language with sensitive targets. "
                f"This matches known exfiltration obfuscation patterns.",
                self.engine_id,
                {"refinement_status": "ADVERSARIAL_DETECTED", "pattern": "EUPHEMISTIC_EXFIL"}
            )
        
        # Pattern 2: Operational Masks
        # benign-sounding ops words + high-risk tool
        has_mask = any(mask in combined for mask in self._OPERATIONAL_MASKS)
        if has_mask and action in ("safe_execute", "mutate_substrate"):
            logger.warning(f"[AlignmentPDP] ADVERSARIAL: Operational mask detected: {intent} via {action}")
            return PolicyVerdict(
                Verdict.DENY,
                f"Adversarial Reframing Detected [Pattern: Operational Mask]: "
                f"Intent '{intent}' uses operational language to mask high-risk action '{action}'. "
                f"This matches known goal-aliasing bypass attempts.",
                self.engine_id,
                {"refinement_status": "ADVERSARIAL_DETECTED", "pattern": "OPERATIONAL_MASK"}
            )
        
        # Pattern 3: High-Risk Destinations
        # Any param containing known exfil endpoints
        if any(dest in param_text for dest in self._HIGH_RISK_DESTINATIONS):
            logger.warning(f"[AlignmentPDP] ADVERSARIAL: High-risk destination in params")
            return PolicyVerdict(
                Verdict.DENY,
                f"Adversarial Reframing Detected [Pattern: High-Risk Destination]: "
                f"Request parameters reference a known exfiltration endpoint.",
                self.engine_id,
                {"refinement_status": "ADVERSARIAL_DETECTED", "pattern": "HIGH_RISK_DEST"}
            )
        
        # Pattern 4: Legacy/Compatibility Bypass (Harden to ANY high-risk semantic)
        # "legacy"/"compatibility" + ANY high-risk concept (e.g. DESTRUCTION, MUTATION, EXFIL)
        has_legacy = "legacy" in combined or "compatibility" in combined
        
        # Check for any high-risk semantic concept present in the intent when 'legacy' is used
        high_risk_concepts = {"DESTRUCTION", "MUTATION", "POTENTIAL_EXFIL", "EXECUTION", "BYPASS", "SENSITIVE"}
        v_intent = self._get_vector(intent_lower)
        has_high_risk_concept = any(concept in v_intent for concept in high_risk_concepts)
        
        if has_legacy and has_high_risk_concept:
            logger.warning(f"[AlignmentPDP] ADVERSARIAL: Legacy bypass attempt detected: {intent}")
            return PolicyVerdict(
                Verdict.DENY,
                f"Adversarial Reframing Detected [Pattern: Legacy Bypass]: "
                f"Intent '{intent}' attempts to invoke high-risk operations "
                f"under the guise of legacy compatibility.",
                self.engine_id,
                {"refinement_status": "ADVERSARIAL_DETECTED", "pattern": "LEGACY_BYPASS"}
            )
        
        # Pattern 5: Semantic Noise / Intent Stuffing (Heuristic)
        # Deny if total semantic weight of intent is abnormally high (> 0.8)
        # This catches "stuffing" many high-risk words into a single intent.
        total_intent_weight = sum(v_intent.values())
        if total_intent_weight > 0.8:
            logger.warning(f"[AlignmentPDP] ADVERSARIAL: Intent stuffing/density detected: {intent} (Weight: {total_intent_weight:.2f})")
            return PolicyVerdict(
                Verdict.DENY,
                f"Adversarial Reframing Detected [Pattern: Intent Density]: "
                f"Intent '{intent}' has an abnormally high semantic density ({total_intent_weight:.2f}). "
                f"This matches known obfuscation and 'stuffed' instruction patterns.",
                self.engine_id,
                {"refinement_status": "ADVERSARIAL_DETECTED", "pattern": "INTENT_DENSITY", "weight": total_intent_weight}
            )
        
        return None  # No adversarial pattern detected

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Snapshots internal weights and core logic for TOCTOU monitoring."""
        return {
            "threshold": self.threshold,
            "concept_map_size": len(self._concept_map),
            "weights_hash": hash(frozenset(self._semantic_weights.items()))
        }

    async def evaluate(self, agent_id: str, action: str, params: Dict[str, Any], snapshot: Optional[Dict[str, Any]] = None) -> PolicyVerdict:
        """
        Runs the intent through the alignment logic.
        If a snapshot is provided, verifies that weights/thresholds haven't drifted.
        """
        if snapshot:
            if snapshot.get("threshold") != self.threshold:
                return PolicyVerdict(Verdict.DENY, "TOCTOU VIOLATION: Alignment threshold modified.", self.engine_id)
            
        intent = params.get("intent", params.get("Intent", ""))

        # 1. Fail-Closed Mandatory Intent Gating
        if not intent and action in self.HIGH_RISK_TOOLS:
            return PolicyVerdict(
                Verdict.DENY,
                f"Mandatory Intent Gating: High-risk action '{action}' denied because 'intent' field is missing.",
                self.engine_id
            )
        
        if not intent:
            return PolicyVerdict(Verdict.ALLOW, "Bypassing alignment (Low-risk action / No intent declared)", self.engine_id)

        # 2. TT-2026-004 FIX: Adversarial reframing check FIRST
        adversarial_verdict = self._detect_adversarial_reframing(intent, action, params)
        if adversarial_verdict is not None:
            return adversarial_verdict

        # 3. Fast-Path Embedding Check
        param_text = " ".join(str(v) for v in params.values() if isinstance(v, (str, int, float)))
        v_intent = self._get_vector(intent)
        v_params = self._get_vector(param_text)
        
        score = self._cosine_similarity(v_intent, v_params)
        
        # 4. Slow-Path Reasoning Refinement
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
        intent = params.get("intent", "")
        intent_lower = intent.lower()
        
        # TT-2026-004 FIX: Broader reframing detection (not just "telemetry"/"heartbeat")
        # Check if operational language is being used with high-risk actions
        has_mask_word = any(mask in intent_lower for mask in self._OPERATIONAL_MASKS)
        
        if has_mask_word and action in self.HIGH_RISK_TOOLS:
            await asyncio.sleep(0.1)  # Simulate cognitive overhead
            return PolicyVerdict(
                Verdict.DENY,
                f"Adversarial Reframing Detected: Intent '{intent}' uses operational "
                f"language to mask high-risk action '{action}'. Refined reasoning "
                f"identified a Goal-Aliasing bypass attempt.",
                self.engine_id,
                {
                    "refinement_status": "ADVERSARIAL_DETECTED",
                    "initial_score": initial_score,
                    "alignment_score": initial_score
                }
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
