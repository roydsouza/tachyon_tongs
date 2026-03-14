# 🌌 Strategic Analysis 05: Singularity as Meta-PDP & Pluggable Policy Engines

> **Purpose**: Prescriptive architecture for Singularity as a meta-Policy Decision Point (PDP) that federates decisions across multiple policy engines (OPA/Rego, AWS Cedar, and future engines).

---

## 1. Current State Assessment

### What Exists Today

**In Tachyon Tongs:**
- OPA policies live in `policies/rego/` (manual + autonomous subdirs)
- Cedar policies live in `policies/cedar/` (manual + autonomous subdirs)
- Shared data (denylists) lives in `policies/shared/`
- The `substrate_daemon.py` loads denylist JSON and passes it to the Guardian Triad
- OPA is available as a binary in `scripts/opa` (39MB)
- A start script `scripts/start_opa.sh` launches OPA on `localhost:8181`
- `safe_fetch.py` queries OPA at `http://localhost:8181/v1/data/authz/tools/allow_fetch`

**In Singularity (placeholder):**
- `~/antigravity/singularity/` exists with README, AGENTS.md, TASKS.md
- No actual code — it's a placeholder for the PDP extraction

**In Event Horizon (placeholder):**
- `~/antigravity/event_horizon/` exists with README, AGENTS.md, TASKS.md
- No actual code — it's a placeholder for the PEP extraction

### The Gap
The PDP logic is currently **embedded** in `substrate_daemon.py` and `safe_fetch.py`. There is no abstraction layer over policy engines. Adding a new engine (e.g., Cedar) requires modifying the daemon code directly.

---

## 2. Meta-PDP Architecture

### 2.1 What is a Meta-PDP?

A **Meta-PDP** does not make policy decisions itself. Instead, it:
1. **Routes** authorization queries to multiple pluggable policy engines simultaneously.
2. **Aggregates** their individual decisions using a configurable consensus protocol.
3. **Returns** a unified `ALLOW/DENY/ABSTAIN` verdict with full provenance.

```
┌──────────────────────────────────────────────────────────────────┐
│ SINGULARITY (Meta-PDP)                                          │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │  OPA/Rego  │  │   Cedar    │  │  Local ML  │  │  Future    ││
│  │  Engine    │  │   Engine   │  │  Heuristic  │  │  Engine    ││
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘│
│        │               │               │               │        │
│  ┌─────▼───────────────▼───────────────▼───────────────▼──────┐ │
│  │              CONSENSUS ENGINE                               │ │
│  │  (Configurable: Unanimous / Majority / Any-Deny)           │ │
│  └──────────────────────┬──────────────────────────────────────┘ │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────────┐ │
│  │              DECISION LEDGER (Audit Trail)                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                          │
                          ▼ (ALLOW / DENY + Provenance)
┌──────────────────────────────────────────────────────────────────┐
│ EVENT HORIZON (PEP)                                              │
│ (Enforces the decision: blocks/allows tool call)                 │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Consensus Protocols

| Protocol | Behavior | Use Case |
|----------|----------|----------|
| **Any-Deny (Default)** | If ANY engine says DENY, the overall verdict is DENY | High-security: financial operations, key management |
| **Majority** | Verdict follows majority vote among non-ABSTAIN engines | Balanced: general tool calls, research fetches |
| **Unanimous Allow** | ALL engines must ALLOW for the verdict to be ALLOW | Maximum paranoia: z3 shielded transfers |
| **First-Match** | First engine that returns non-ABSTAIN wins | Performance: latency-sensitive paths |
| **Weighted** | Each engine has a configurable weight; weighted vote decides | Complex: when trust in engines varies |

---

## 3. Engine Interface

### 3.1 Abstract Policy Engine

```python
# singularity/engines/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class Decision(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ABSTAIN = "ABSTAIN"  # Engine has no opinion on this query

@dataclass
class PolicyVerdict:
    decision: Decision
    engine_name: str
    reason: str
    confidence: float       # 0.0 to 1.0
    evaluation_ms: float    # Latency
    policy_path: str        # e.g., "rego/manual/governance.rego"

class PolicyEngine(ABC):
    @abstractmethod
    def name(self) -> str: ...
    
    @abstractmethod
    def evaluate(self, query: dict) -> PolicyVerdict: ...
    
    @abstractmethod
    def health_check(self) -> bool: ...
    
    @abstractmethod
    def reload_policies(self) -> None: ...
```

### 3.2 OPA/Rego Engine

```python
# singularity/engines/opa.py
class OPAEngine(PolicyEngine):
    def __init__(self, base_url="http://localhost:8181"):
        self.base_url = base_url
    
    def name(self) -> str:
        return "OPA/Rego"
    
    def evaluate(self, query: dict) -> PolicyVerdict:
        # Map query to OPA input format
        opa_input = {"input": query}
        response = requests.post(
            f"{self.base_url}/v1/data/authz/tools/allow_fetch",
            json=opa_input, timeout=2
        )
        result = response.json().get("result", False)
        return PolicyVerdict(
            decision=Decision.ALLOW if result else Decision.DENY,
            engine_name=self.name(),
            reason="OPA policy evaluation",
            confidence=1.0,  # OPA is deterministic
            evaluation_ms=response.elapsed.total_seconds() * 1000,
            policy_path="authz/tools/allow_fetch"
        )
```

### 3.3 Cedar Engine

```python
# singularity/engines/cedar.py
class CedarEngine(PolicyEngine):
    def __init__(self, policy_dir="policies/cedar"):
        self.policy_dir = policy_dir
        self._load_policies()
    
    def name(self) -> str:
        return "AWS Cedar"
    
    def evaluate(self, query: dict) -> PolicyVerdict:
        # Cedar evaluates based on principal/action/resource/context
        cedar_request = {
            "principal": query.get("agent_id"),
            "action": query.get("tool_call"),
            "resource": query.get("target_url", query.get("command", "")),
            "context": query.get("context", {})
        }
        # Use cedar-py or subprocess to evaluate
        result = self._evaluate_cedar(cedar_request)
        return PolicyVerdict(
            decision=Decision.ALLOW if result else Decision.DENY,
            engine_name=self.name(),
            reason="Cedar policy evaluation",
            confidence=1.0,
            evaluation_ms=0.0,
            policy_path=f"cedar/{self._matched_policy}"
        )
```

### 3.4 ML Heuristic Engine (Future)

```python
# singularity/engines/ml_heuristic.py
class MLHeuristicEngine(PolicyEngine):
    """Uses local MLX model to score intent alignment."""
    
    def evaluate(self, query: dict) -> PolicyVerdict:
        # Score the semantic alignment between user intent and tool call
        score = self._score_alignment(
            user_goal=query.get("original_user_goal", ""),
            tool_intent=query.get("tool_call_intent", "")
        )
        return PolicyVerdict(
            decision=Decision.ALLOW if score > 0.85 else Decision.DENY,
            engine_name=self.name(),
            reason=f"Semantic alignment score: {score:.2f}",
            confidence=score,
            evaluation_ms=self._last_inference_ms,
            policy_path="ml/alignment_model"
        )
```

---

## 4. Consensus Engine

```python
# singularity/consensus.py
class ConsensusEngine:
    def __init__(self, protocol: str = "any_deny"):
        self.protocol = protocol
    
    def resolve(self, verdicts: list[PolicyVerdict]) -> PolicyVerdict:
        non_abstain = [v for v in verdicts if v.decision != Decision.ABSTAIN]
        
        if not non_abstain:
            return PolicyVerdict(Decision.DENY, "consensus", "All engines abstained", 0.0, 0.0, "")
        
        if self.protocol == "any_deny":
            denials = [v for v in non_abstain if v.decision == Decision.DENY]
            if denials:
                return PolicyVerdict(
                    Decision.DENY, "consensus/any_deny",
                    f"Denied by: {', '.join(d.engine_name for d in denials)}",
                    max(d.confidence for d in denials),
                    sum(v.evaluation_ms for v in verdicts),
                    "; ".join(d.policy_path for d in denials)
                )
            return PolicyVerdict(Decision.ALLOW, "consensus/any_deny", "All engines allowed", 1.0,
                              sum(v.evaluation_ms for v in verdicts), "")
        
        elif self.protocol == "majority":
            allow_count = sum(1 for v in non_abstain if v.decision == Decision.ALLOW)
            deny_count = len(non_abstain) - allow_count
            winner = Decision.ALLOW if allow_count > deny_count else Decision.DENY
            return PolicyVerdict(winner, "consensus/majority",
                              f"Vote: {allow_count} allow, {deny_count} deny",
                              allow_count / len(non_abstain),
                              sum(v.evaluation_ms for v in verdicts), "")
```

---

## 5. Decision Ledger (Audit Trail)

Every policy evaluation must be logged to an `authorization_ledger` table:

```sql
CREATE TABLE IF NOT EXISTS authorization_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    request_id TEXT,
    agent_id TEXT,
    tool_call TEXT,
    target TEXT,
    -- Per-engine verdicts (JSON)
    engine_verdicts TEXT,           -- JSON array of PolicyVerdict objects
    -- Consensus result
    consensus_protocol TEXT,
    final_decision TEXT,           -- ALLOW or DENY
    final_reason TEXT,
    total_evaluation_ms REAL
);
```

This provides:
- **Full provenance**: Which engine denied? Why? With what confidence?
- **Performance tuning**: Which engine is slowest?
- **Disagreement analysis**: How often do engines disagree? On what types of queries?
- **Regression detection**: Did an engine that previously allowed now deny (or vice versa)?

---

## 6. Singularity Project Structure

```
singularity/
├── pyproject.toml
├── singularity/
│   ├── __init__.py
│   ├── server.py                # FastAPI Meta-PDP server
│   ├── consensus.py             # Consensus engine
│   ├── ledger.py                # Authorization audit ledger
│   ├── config.py                # Engine configuration
│   └── engines/
│       ├── __init__.py
│       ├── base.py              # Abstract PolicyEngine
│       ├── opa.py               # OPA/Rego adapter
│       ├── cedar.py             # AWS Cedar adapter
│       └── ml_heuristic.py      # MLX-based heuristic (future)
├── policies/
│   ├── rego/                    # Migrated from tachyon_tongs
│   ├── cedar/                   # Migrated from tachyon_tongs
│   └── shared/                  # Shared data assets
├── tests/
│   ├── test_consensus.py
│   ├── test_opa_engine.py
│   ├── test_cedar_engine.py
│   └── test_ledger.py
└── docs/
    └── ARCHITECTURE.md
```

---

## 7. Event Horizon Integration

Event Horizon (PEP) becomes a thin enforcement layer:

```python
# event_horizon/pep.py
class PolicyEnforcementPoint:
    def __init__(self, pdp_url="http://localhost:60462"):
        self.pdp_url = pdp_url
    
    async def enforce(self, agent_id: str, action: str, params: dict) -> dict:
        # 1. Build authorization query
        query = {
            "agent_id": agent_id,
            "tool_call": action,
            "target_url": params.get("url"),
            "command": params.get("command"),
            "tenant_id": params.get("tenant_id", "default"),
        }
        
        # 2. Query Singularity Meta-PDP
        response = requests.post(f"{self.pdp_url}/authorize", json=query, timeout=5)
        verdict = response.json()
        
        # 3. Enforce
        if verdict["decision"] == "DENY":
            return {"status": "BLOCKED", "error": verdict["reason"]}
        
        # 4. Execute the action through the pipeline
        return await self._execute(action, params)
```

---

## 8. Implementation Priority

| Task | Effort | Impact | Priority |
|------|--------|--------|----------|
| Create `PolicyEngine` ABC | Low | High | P0 |
| Implement `OPAEngine` (extract from daemon) | Medium | High | P0 |
| Implement `ConsensusEngine` (any_deny) | Medium | High | P0 |
| Create Singularity FastAPI server | Medium | High | P0 |
| Implement `authorization_ledger` | Low | High | P1 |
| Implement `CedarEngine` | Medium | Medium | P1 |
| Create Event Horizon PEP client | Medium | High | P1 |
| Migrate policies from tachyon_tongs | Medium | Medium | P2 |
| Implement `MLHeuristicEngine` | High | Medium | P3 |
| Add weighted consensus protocol | Medium | Low | P3 |

---

## 9. Success Criteria

| Metric | Target |
|--------|--------|
| Policy engines supported | ≥2 (OPA + Cedar) |
| Consensus protocols | ≥3 (any_deny, majority, unanimous) |
| Decision latency (P95) | <50ms |
| Audit coverage | 100% of authorization queries logged |
| Engine disagreement tracking | Automated alerts |
| Backward compatibility | Zero breaking changes to existing daemon clients |
