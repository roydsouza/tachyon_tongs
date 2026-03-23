# Tachyon Tongs: Agentic Architecture (The Immune Collective)

**Version:** 2.0  
**Status:** Adopted Architecture  

---

## 1. Core Philosophy: The Immune Collective

The ad hoc and organic growth of Tachyon Tongs into an Agentic Firewall mirrors the autonomic immune system. The goal of this architecture is to crystallize that "living organism" quality into a clean, evolvable framework while preserving every ounce of the biological elegance that makes the project distinctive.

**Key Design Principles:**

1. **Roles Over Agents:** Agents are explicit implementations of roles, not one-off scripts. The substrate uses an **Agent Plugin Architecture (ADR-0033)** where agents are decoupled from the core and discovered via the `AgentRegistry`.
2. **Event-First Backplane:** Agents never call each other directly. All coordination flows through pub/sub on a unified, SQLite-backed Telemetry Bus.
3. **Sign Everything:** Every output is signed; every input payload is verified. Trust is anchored in Post-Quantum Cryptography (PQC) using Ed25519 + ML-DSA-65 hybrid signatures.
4. **Oversight Built-In:** Human-In-The-Loop (HITL), Human-On-The-Loop (HOTL), and Human-Out-Of-The-Loop (HOOTL) modes are integrated natively into all execution patterns via the **Airlock** system.
5. **Architectural Purity:** Single Responsibility holds true. Agents do one thing well, sign for it, and leave a complete forensic trail.
6. **Forensic by Default:** Every action produces an immutable `ActionRecord`. Any past decision can be fully reconstructed and replayed.
7. **Defense in Depth via Asymmetry:** Communication with the outside world is strictly proxied through specialized agents (e.g., the Herald). High-value administrative agents are air-gapped from the network.
8. **Secure Gateway Portability:** The entire substrate is designed to run locally on a standard workstation (Apple Silicon) or as a dedicated, high-assurance security gateway device.
9. **Ecosystem Interoperability**: The **Claw Compatibility Bridge (Phase 41)** allows secure ingestion of external agent skills while re-wrapping them in Tachyon's **Quarantine Mode** gating.

---

## 2. Taxonomy: The Six-Tier Architecture

To manage the expanding collective, the ecosystem is categorized into six functional domains. Each agent is listed with its role, trigger conditions, and primary outputs.

### A. Threat Intelligence (The Sensory Layer)
*Purpose: Discover, simulate, and understand attacks.*

| Agent | Role | Triggers | Outputs |
|-------|------|----------|---------|
| **Sentinel** | Full-spectrum CVE detection and cataloging | Scheduled (cron), Manual (`/sentinel`) | `EXPLOITATION_CATALOG` updates, new CVE entries |
| **Canary** | Lightweight early warning probes / sacrificial sandboxes | System events, honeypot hits | Alert triggers, anomaly reports |
| **Pathogen** | Adversarial red-team simulator (self-stress-testing) | New catalog entries, test requests | Exploit validation results, defense recommendations |
| **Synthesizer** | Exploit pattern generation and mutation | Multiple threat detections | Attack pattern recognition, mutated payloads |
| **Forge** | Synthetic zero-day adversary generator (Metal-accelerated) | Scheduled, on-demand | Complex multi-stage attack scenarios |
| **Forensic Auditor** | Deep post-facto forensic analysis | Git commits, file changes, audit requests | Vulnerability reports, signed attestation findings |

### B. Defense & Mitigation (The Muscle)
*Purpose: Implement fixes and active defenses.*

| Agent | Role | Triggers | Outputs |
|-------|------|----------|---------|
| **Engineer (Autopatcher)** | Synthesizes and applies surgical code/infrastructure patches | CVE assignments, approved fixes | Code patches, configuration updates |
| **Quarantine Manager** | Isolation controller for suspicious state | Critical alerts, suspicious activity | Container isolation, process sandboxing |

### C. System Integrity & Trust (The Purity Layer)
*Purpose: Ensure the substrate remains uncompromised.*

| Agent | Role | Triggers | Outputs |
|-------|------|----------|---------|
| **Guardian** | Real-time substrate integrity enforcement and IDS | Network events, file-system changes, Merkle root drift | Block actions, alert escalations |
| **Verifier** | Continuous validation of Merkle roots and hybrid signatures | Scheduled, post-mutation | Integrity reports, signed verification results |
| **Compliance Auditor** | Periodically checks all agents satisfy their Cedar/Rego policies | Policy updates, scheduled audits | Compliance reports, remediation tasks |

### D. Quality & Maintenance (The Metabolic Layer)
*Purpose: Homeostasis, optimization, and code hygiene.*

| Agent | Role | Triggers | Outputs |
|-------|------|----------|---------|
| **Cleaner (Janitor)** | Scans for orphans, stale debates, prunes old logs | Daily cycle, filesystem changes | Orphan removal proposals (via Airlock) |
| **Refactorer** | Identifies technical debt and suggests simplifications | Code changes, low-activity periods | Refactoring proposals, quality reports |
| **Regression Guard** | Ensures mutations don't cause performance or capability drift | Post-deployment, post-patch | Performance baselines, anomaly flags |
| **Dependency Warden** | Supply chain security scanning | Dependency updates, new packages | Vulnerability scans, update recommendations |

### E. Orchestration & Communication (The Nervous System)
*Purpose: Coordinate agents, schedule events, and alert humans.*

| Agent | Role | Triggers | Outputs |
|-------|------|----------|---------|
| **Scheduler** | Centralized time-based synthetic event generator | Cron expressions, calendar events | Agent wake-ups, synthetic `SCHEDULED_TASK` events |
| **Herald (Notifier)** | Translates raw alerts into "Diplomatic Dispatches" delivered via Signal | Priority events from EventBus | Signal messages, formatted digests |
| **Event Dispatcher** | Pub/sub broker for the backplane | All system events | Event routing, subscription management |

### F. Strategy & Persona (The Executive Brain)
*Purpose: Top-level strategic planning, adaptation, and human interface representation.*

| Agent | Role | Triggers | Outputs |
|-------|------|----------|---------|
| **Firewall Administrator** | Meta-agent / persona simulating expert knowledge. Orchestrates, never does raw work. | All high-severity events, policy changes | Oversight decisions, Mutant Lock issuance, strategy adjustments |
| **Horizon Analyzer (Scout)** | Long-range strategic awareness and threat forecasting | Weekly cycle, new research publications | Trend analysis, future threat predictions |
| **Risk Scorer** | Dynamically assigns numeric risk to files, agents, and changes | Agent completions, outcome metrics | Risk scores feeding Firewall Administrator decisions |
| **Reflector** | Self-evolution agent proposing new agents and taxonomy changes | Weekly self-assessment | "State of the Collective" ADR proposals |

### Debate & Deliberation (Cross-Cutting Pattern)
The following agents participate in the **Debate Arena** pattern for multi-perspective analysis of complex decisions. They are not a separate tier but span across Threat Intelligence and Strategy:

| Agent | Role | Triggers | Outputs |
|-------|------|----------|---------|
| **Debater** | Presents and defends one side of a security trade-off | Ambiguous threats, complex decisions | Debate transcripts |
| **Skeptic** | Adversarial critic challenging proposed actions | Engineer proposals, patch submissions | Counter-arguments, risk objections |
| **Meta-Critic** | Final arbiter synthesizing debate positions | Debate completion | Consensus recommendations, signed verdicts |

---

## 3. The Agent Protocol

All agents conform to a universal, amortized interface built on top of a `BaseAgent` class to ensure consistent telemetry, capability gating, and forensics.

### 3.1 The Execution Lifecycle

Agents are discovered and instantiated via the **`AgentRegistry`** (`agents/_core/registry.py`), ensuring that all plugins follow a standardized lifecycle and capability binding.

Every agent follows a strict state machine:

```
DORMANT → TRIGGERED → AUTHENTICATING → EXECUTING → RECORDING → NOTIFYING → DORMANT
```

1. **DORMANT:** Agent is registered, subscribed to EventBus topics, waiting.
2. **TRIGGERED:** Event matched agent's subscription filter.
3. **AUTHENTICATING:** Agent verifies the peer signature on the incoming event (PQC).
4. **EXECUTING:** Intent-gated action is routed via `ToolRouter` and performed.
5. **RECORDING:** Agent creates an immutable `ActionRecord` and signs it.
6. **NOTIFYING:** Agent publishes the result as a new `Event` on the bus.
7. **DORMANT:** Agent returns to waiting state.

### 3.2 Core Data Structures

```python
@dataclass
class Event:
    """Standard event format for agent triggering."""
    event_id: str                    # Unique event identifier
    event_type: EventType            # Enum: CVE_DISCOVERED, CODE_CHANGED, etc.
    timestamp: datetime
    source: str                      # Which agent/system generated this
    priority: Priority               # CRITICAL, HIGH, MEDIUM, LOW
    data: Dict[str, Any]             # Event-specific payload
    categories: List[AgentCategory]  # Which agent types should respond
    signature: bytes                 # Source signature for verification

@dataclass
class AgentContext:
    """Read-only execution context provided to the agent."""
    event: Event
    config: Dict[str, Any]           # Agent-specific configuration
    workspace: Path                  # Agent's working directory
    oversight_mode: OversightMode    # HITL, HOTL, or HOOTL
    allowed_actions: Set[ActionType] # Capability-gated tool access
    backplane: EventBusClient        # For pub/sub and data access

@dataclass
class AgentResult:
    """Standardized agent output."""
    agent_id: str
    event_id: str
    status: Status                   # SUCCESS, FAILURE, PARTIAL, PENDING_APPROVAL
    findings: List[Finding]          # What was discovered
    actions_taken: List[Action]      # What was done
    recommendations: List[str]       # Human-actionable suggestions
    signature: bytes                 # Result signature
    approval_required: bool          # For HITL/HOTL modes
    approval_timeout: Optional[timedelta]
```

### 3.3 Standard Agent Interface (BaseAgent)

```python
class BaseAgent(ABC):
    """All agents in the Immune Collective implement this protocol."""

    def __init__(self, role: str, category: AgentCategory):
        self.identity = load_or_create_key(role)  # Ed25519 + ML-DSA-65
        self.bus = EventBusClient()
        self.airlock = AirlockClient()

    @abstractmethod
    async def on_event(self, event: Event) -> AgentResult:
        """Core execution logic triggered by an event."""
        ...

    def verify_peer_signature(self, event: Event) -> bool:
        """Verify the cryptographic identity of the event source."""
        ...

    def sign_output(self, result: AgentResult) -> bytes:
        """Sign the result with this agent's hybrid PQC key."""
        ...

    def record_action(self, result: AgentResult) -> ActionRecord:
        """Create an immutable forensic record of the action taken."""
        ...
```

---

## 4. The Event Backplane & Coordination

### 4.1 EventBus (SQLite WAL)

Inter-agent direct calls are strictly forbidden. The system utilizes a lightweight, local SQLite-backed EventBus operating in Write-Ahead Log (WAL) mode. This guarantees crash-safety without needing external dependencies (no Redis, no Postgres).

- Agents subscribe to topics based on categories and severity (e.g., `threat_intelligence/high`).
- The **Scheduler** replaces ad hoc cron jobs by injecting synthetic timing events directly into the bus.

### 4.2 Event Schema

```json
{
  "event_id": "uuid-v4",
  "event_type": "CVE_DISCOVERED",
  "timestamp": "2026-03-21T10:30:00Z",
  "source": "sentinel-v1",
  "priority": "HIGH",
  "categories": ["THREAT_INTELLIGENCE", "DEFENSE_MITIGATION"],
  "data": { "cve_id": "CVE-2026-1234", "cvss": 8.1 },
  "signature": "base64-encoded-hybrid-sig"
}
```

### 4.3 Event Routing Rules

```yaml
routing:
  CVE_DISCOVERED:
    categories: [THREAT_INTELLIGENCE, DEFENSE_MITIGATION]
    priority: HIGH
    throttle: 1/minute

  CODE_CHANGED:
    categories: [QUALITY_MAINTENANCE, THREAT_INTELLIGENCE]
    priority: MEDIUM
    batch: true
    batch_window: 5m

  CRITICAL_ALERT:
    categories: [COMMUNICATION]
    priority: CRITICAL
    immediate: true  # No batching or throttling

  APPROVAL_REQUIRED:
    categories: [COMMUNICATION]
    priority: HIGH
    immediate: true
```

### 4.4 Event Types

```python
class EventType(Enum):
    CVE_DISCOVERED = "cve_discovered"
    CODE_CHANGED = "code_changed"
    SYSTEM_ALERT = "system_alert"
    SCHEDULED_TASK = "scheduled_task"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    AGENT_COMPLETED = "agent_completed"
    CRITICAL_ALERT = "critical_alert"
    MUTATION_LOCK_REQUESTED = "mutation_lock_requested"
    MUTATION_LOCK_GRANTED = "mutation_lock_granted"
    DEBATE_INITIATED = "debate_initiated"
    DEBATE_CONCLUDED = "debate_concluded"

class Priority(Enum):
    CRITICAL = 0  # Immediate human attention
    HIGH = 1      # Same-day response
    MEDIUM = 2    # This week
    LOW = 3       # Informational
```

---

## 5. Security & Cryptographic Identity

### 5.1 Hybrid Post-Quantum Identity

Every agent operating in the substrate is bounded by cryptographic primitives:
- Agents use **Ed25519 + ML-DSA-65** hybrid signatures.
- Delegation Certificates and a local Revocation List (CRL) guarantee that compromised agents can be instantly defunded of their capabilities.
- Certificates include `allowed_actions` and `max_oversight_mode` constraints.

### 5.2 The "Mutant Lock" Pattern

Effector agents (such as the Engineer or Cleaner) making file-system mutations must first secure a time-bound, signed "Mutation Token" / Mutant Lock from the Firewall Administrator. This ensures the Guardian doesn't fire false "State Compromised" alarms during a legitimate patching event.

The Mutant Lock lifecycle:
1. Engineer publishes `MUTATION_LOCK_REQUESTED` event.
2. Firewall Administrator evaluates the request, issues a signed, time-bound lock via `MUTATION_LOCK_GRANTED`.
3. Engineer performs its mutation within the lock window.
4. Guardian checks for an active Mutant Lock before raising integrity alarms.
5. Lock expires automatically; any mutation after expiry triggers a full Guardian alert.

### 5.3 Capability Gating (PDP/PEP)

Every agent's access to internal tools is restricted via Semantic Intent Gating:
- The `AgentContext.allowed_actions` set is populated from the agent's Delegation Certificate.
- The `ToolRouter` acts as the Policy Enforcement Point (PEP), checking each tool invocation against the certificate before execution.
- No agent ever writes directly to disk or calls `subprocess` outside the `AppleSandbox` + `ToolRouter`.

---

## 6. The Firewall Administrator & Operational Modes

The **Firewall Administrator** acts as the overarching consciousness of the entire substrate. It never performs raw labor (scanning, coding, patching); instead, it orchestrates the collective based on predefined risk configurations and adaptive learning.

### 6.1 Cognitive Engine (Local `mlx_lm` Inference)

To guarantee absolute operational security (OpSec), zero network latency, and continuous high availability, the Firewall Administrator is powered exclusively by a localized LLM (via `mlx_lm` optimized for Apple Silicon / Metal). This ensures that continuous, "always-on" meta-reasoning over sensitive substrate telemetry (alerts, file drifts, state changes, and patch strategies) *never* leaves the machine or incurs external cloud API bottlenecks.

**Design Rationale:**
- **Zero Intelligence Leakage:** The Administrator's constant awareness of the substrate's exact defensive posture never traverses the network.
- **Zero-Cost Telemetry:** No per-token charges for continuous meta-reasoning over hundreds of daily events.
- **High Availability:** Immune to cloud provider outages, DDoS, or API quota exhaustion.
- **Apple Silicon Synergy:** Unified memory architecture enables running a quantized model perpetually with minimal thermal/battery overhead.

### 6.2 Adaptive Learning Module

The Firewall Administrator does not remain static. Its decision-making improves over time:

```python
class AdaptiveLearning:
    """Tracks defense effectiveness and evolves strategy."""

    def update(self, attack_vector: str, defense_effectiveness: float):
        """Record how well a defense performed against an attack type."""
        ...

    def get_recommended_strategy(self, threat_type: str) -> Strategy:
        """Return the best-performing strategy for a given threat class."""
        ...

class KnowledgeBase:
    """Long-term pattern storage for the Administrator."""

    def add_pattern(self, pattern: AttackPattern, mitigation: Mitigation):
        """Record a successful attack-mitigation pair."""
        ...

    def query_similar(self, new_threat: Threat) -> List[HistoricalResponse]:
        """Find historically similar threats and their outcomes."""
        ...
```

The Administrator's `KnowledgeBase` accumulates historical attack patterns and defense outcomes. Over time, it recognizes recurring threat vectors and pre-selects proven mitigation strategies — adapting its behavior from reactive rule-matching to proactive pattern anticipation.

### 6.3 Handling Oversight & Communication

The Administrator manages the transition between oversight modes and adjusts verbosity thresholds. *Crucially, it is cryptographically air-gapped from external networks.* It does not integrate directly with Signal or email APIs. Instead, it delegates communication to the **Herald** agent via the EventBus:

- **HITL (Human-in-the-Loop):** Every change pauses in the Airlock. The Administrator pushes an event to the Herald to format a "nag" styling demanding human confirmation via Signal.
- **HOTL (Human-on-the-Loop):** Low/Medium risk patches execute automatically. High-risk actions prompt the Administrator to issue an alert through the Herald with a time-bound veto window.
- **HOOTL (Hands-out-of-the-Loop):** Fully autonomous operation. Generates a daily "Diplomatic Summary" event, which the Herald consumes and transmits via Signal without blocking operations.

---

## 7. The Herald: Trust Boundary & Signal Integration

The **Herald** is the single most sensitive agent in terms of network exposure. It is the *only* agent in the collective with external network access. This demands a rigorous trust boundary specification.

### 7.1 Capabilities & Constraints

| Attribute | Value |
|-----------|-------|
| **Network Access** | ✅ Outbound to Signal API (via `signal-cli` or equivalent) |
| **Filesystem Write** | ❌ None. Cannot modify substrate files. |
| **Mutant Lock Authority** | ❌ Cannot request or hold a Mutation Token. |
| **Signing Authority** | ✅ Signs its own EventBus messages only. |
| **Bidirectional** | ✅ Receives inbound commands via Signal webhooks. |

### 7.2 Outbound Flow (Alerts → Signal)

1. The Firewall Administrator decides a finding is worth communicating.
2. It publishes a `CRITICAL_ALERT` or `APPROVAL_REQUIRED` event to the EventBus.
3. The Herald picks up the event, formats it into an aesthetic "Diplomatic Dispatch."
4. The Herald transmits the formatted message to Signal via `signal-cli`.

**Example Dispatch (HOTL Mode):**
> "The Engineer has proposed a surgical patch for CVE-2026-0001. The Skeptic was unimpressed, but the Meta-Critic has allowed it. You have 4 hours to veto via the Airlock before auto-deployment."

### 7.3 Inbound Flow (Signal → Commands)

1. The human replies to a Signal message (e.g., "Approve" or "Deny").
2. The Herald receives the webhook, parses the command.
3. The Herald creates an `APPROVAL_GRANTED` or `APPROVAL_DENIED` event, signs it with its own key, and publishes it to the EventBus.
4. The Firewall Administrator reads the event, verifies the Herald's signature, and *only then* executes the state change.

**Security Invariant:** If the Herald is compromised (e.g., a spoofed Signal webhook), the worst possible outcome is noisy events on the bus. Because the Herald lacks filesystem mutation authority and Mutant Lock privilege, the substrate remains perfectly safe.

---

## 8. Forensic Reconstruction

Every agent action produces an immutable, signed `ActionRecord`. This enables full forensic reconstruction of any past decision — a critical feature for a high-assurance security substrate.

### 8.1 ActionRecord Structure

```python
@dataclass
class ActionRecord:
    """Immutable record of an agent action."""
    record_id: str
    agent_id: str
    event_id: str                    # What triggered this action
    timestamp: datetime
    action_type: ActionType
    inputs: Dict[str, Any]           # What data the agent consumed
    outputs: Dict[str, Any]          # What the agent produced
    files_modified: List[Path]       # Filesystem changes (if any)
    status: Status
    duration: timedelta
    signature: bytes                 # Agent's hybrid PQC signature
    oversight_mode: OversightMode    # Mode at time of execution
    approval_id: Optional[str]       # HITL approval reference (if applicable)
    human_override: bool             # Whether a human intervened
```

### 8.2 Decision Replay

```python
def reconstruct_agent_decision(record_id: str) -> DecisionPath:
    """Recreate the full context and reasoning of any past agent action."""

    record = get_action_record(record_id)
    event = get_event(record.event_id)

    agent_state = {
        "config": get_config_snapshot(record.agent_id, record.timestamp),
        "previous_actions": get_previous_actions(
            record.agent_id,
            since=record.timestamp - timedelta(hours=24)
        ),
    }

    return DecisionPath(
        trigger=event,
        agent_state=agent_state,
        action=record,
        outcome=record.outputs,
    )
```

This function enables a one-command replay of any decision in the system's history: what event triggered it, what state the agent was in, what it decided, and what the outcome was.

---

## 9. Migration & Rollout Strategy

To introduce this framework safely, Tachyon Tongs will adopt a **Zero-Disruption Migration** path:

1. **ADR First:** Create `docs/adr/0033-agentic-collective-taxonomy.md` formally adopting this architecture.
2. **Backbone:** Implement the `EventBus` (SQLite WAL) and `Scheduler` underneath the active system without changing existing agent behavior.
3. **BaseAgent Protocol:** Update the `BaseAgent` Python class to enforce the Uniform Lifecycle, while keeping existing ad hoc scripts running in parallel.
4. **First Migration (Sentinel):** Convert the noisiest agent to the new protocol to validate stability and correctness.
5. **Iterative Migration:** Issue Airlock approvals to migrate Guardian, Engineer, and Pathogen one by one.
6. **New Agents:** Instantiate the Firewall Administrator (with `mlx_lm`), Herald (with Signal integration), and Cleaner.
7. **Debate Integration:** Wire the existing Debater/Skeptic/Meta-Critic into the EventBus as first-class participants.

---

## 10. Paths Not Taken (Rejected Architecture Ideas)

During the design analysis of this architecture, several concepts were explicitly considered and discarded.

### ❌ Heavy External Infrastructure (Redis / PostgreSQL / Elasticsearch)
Suggestions to use Redis for pub/sub, PostgreSQL for event history, and Elasticsearch for search were rejected.
**Rationale:** Tachyon Tongs thrives as an Apple Silicon local-native, secure system. Heavyweight persistent daemons and external network boundaries break the "no network except through safe_fetch" rule and increase the attack surface. SQLite-WAL and local file semantics provide equivalent functionality with zero additional dependencies.

### ❌ 4-Branch Taxonomy & 7-Level Tiers
Proposals offering a simplistic 4-branch model (Somatic, Purity, Vision, Command) or an overly complex 7-level structure were both dropped in favor of a balanced 6-tier architecture.
**Rationale:** 4 layers were too rigid to properly classify Support vs Administrative functions, while 7 layers introduced artificial boundaries (like separating "Persona" into its own tier rather than treating it as part of Strategy/Executive).

### ❌ Agent Responsibility Merging
Ideas to fold the Canary directly into the Sentinel as a "mode," or combine the Auditor into the Guardian, were explicitly rejected.
**Rationale:** Doing so violates the "Single Responsibility" principle. Sentinel handles broad external scanning, whereas Canary focuses on local trap detection. Guardian ensures runtime integrity, while Auditor performs deep forensic analysis post facto. Clean boundaries yield cleaner forensic audit trails.

### ❌ Log Processing as an Agent
Proposals to make the "Log Aggregator" a first-class agent were discarded.
**Rationale:** Centralized log processing should be an implicit service provided by the Telemetry Bus backplane, rather than an agent that evaluates and signs behavior. Agents *emit* events; the infrastructure handles storage and rotation.

### ❌ Organic / Open-Ended Tool Access
Allowing agents unstructured or overly broad access to internal systems to facilitate "flexibility."
**Rationale:** Violates the principle of tight, capability-gated control (PDP/PEP integration). Every tool use must map strictly to the `allowed_actions` set in the agent's Delegation Certificate.

### ❌ Firewall Administrator with Direct Network Access
Suggestions to have the Firewall Administrator directly integrate with Signal or external APIs for notifications and C2.
**Rationale:** The Administrator holds the keys to the kingdom (Mutant Lock issuance, oversight mode control, strategy). Granting it external network access creates an unacceptable attack surface. The Herald proxy pattern ensures the "brain" is air-gapped from the "mouth," providing a critical layer of **Defense in Depth** where the attacker must compromise multiple isolated agent identities to reach the executive controller.

### ❌ Cloud-Hosted LLM for the Administrator
Using external cloud LLM APIs (OpenAI, Anthropic, etc.) for the Firewall Administrator's cognitive engine.
**Rationale:** Continuous meta-reasoning over the substrate's exact defensive posture would constitute massive intelligence leakage. Local `mlx_lm` inference guarantees zero data exfiltration, zero latency, zero cost, and immunity to cloud provider outages. This local-first constraint makes the architecture an optimal candidate for **Secure Hardware Gateway** deployments where the entire security logic resides in a trusted, air-gapped physical envelope.
