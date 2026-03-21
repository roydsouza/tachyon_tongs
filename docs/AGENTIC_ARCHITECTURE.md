# Tachyon Tongs: Agentic Architecture (The Immune Collective)

**Version:** 1.0  
**Status:** Adopted Architecture  

## 1. Core Philosophy: The Immune Collective

The ad hoc and organic growth of Tachyon Tongs into an Agentic Firewall mirrors the autonomic immune system. The goal of this architecture is to crystallize that "living organism" quality into a clean, evolvable framework. 

**Key Design Principles:**
1. **Roles Over Agents:** Agents are explicit implementations of roles, not one-off entities. Meta-agents compose other agents rather than doing raw work.
2. **Event-First Backplane:** Agents never call each other directly. They use pub/sub on a unified Telemetry Bus.
3. **Sign Everything:** Every output is signed; every input payload is verified. Trust is anchored in Post-Quantum Cryptography (PQC).
4. **Oversight Built-In:** Human-In-The-Loop (HITL), Human-On-The-Loop (HOTL), and Human-Out-Of-The-Loop (HOOTL) are integrated natively into all execution patterns.
5. **Architectural Purity:** Single Responsibility holds true. Agents do one thing well, sign for it, and leave a forensic trail.

---

## 2. Taxonomy: The Six-Tier Architecture

To manage the expanding collective, the ecosystem is categorized into six functional domains.

### A. Threat Intelligence (The Sensory Layer)
*Purpose: Discover, simulate, and understand attacks.*
- **Sentinel:** Continuous full-spectrum detection, cataloging external intelligence.
- **Canary:** Lightweight early warning probes and sacrificial sandboxes.
- **Pathogen:** Adversarial simulator executing self-stress-tests.
- **Synthesizer:** Exploit pattern generation and mutation.
- **Forensic Auditor:** Deep post-facto forensic analysis of events.

### B. Defense & Mitigation (The Muscle)
*Purpose: Implement fixes and active defenses.*
- **Engineer (Autopatcher):** Synthesizes and applies surgical code/infrastructure patches.
- **Patcher / Quarantine Manager:** Safely isolates malicious state immediately when detected.

### C. System Integrity & Trust (The Purity Layer)
*Purpose: Ensure the substrate remains uncompromised.*
- **Guardian:** Real-time substrate integrity enforcement and intrusion detection.
- **Verifier:** Continuous validation of Merkle roots and signature checks.
- **Attestation Agent:** Remote trust proofs mapping substrate behavior to formal standards.

### D. Quality & Maintenance (The Metabolic Layer)
*Purpose: Homeostasis, optimization, and code hygiene.*
- **Cleaner (Janitor):** Scans for orphans, stale debates, and prunes old logs.
- **Refactorer:** Identifies technical debt, suggests simplifications, and streamlines logic.
- **Regression Guard:** Ensures mutations don't cause performance or capability drift.

### E. Orchestration & Communication (The Nervous System)
*Purpose: Coordinate agents, schedule events, and alert humans.*
- **Scheduler:** Centralized time-based synthetic event generator.
- **Notifier / Herald:** Translates raw alerts into "Diplomatic Dispatches" delivered via Signal or external channels.
- **Event Dispatcher:** Pub/sub broker for the backplane.

### F. Strategy & Persona (The Executive Brain)
*Purpose: Top-level strategic planning, adaptation, and human interface representation.*
- **Firewall Administrator:** A meta-agent / persona simulating expert knowledge. It manages oversight modes, adjusts thresholds, and delegates tasks (e.g., escalating to the Notifier or triggering the Engineer). 
- **Horizon Analyzer (Scout/Oracle):** Long-range strategic awareness and threat forecasting.
- **Risk Scorer:** Dynamically assigns numeric risk to files, agents, and external changes.

---

## 3. The Agent Protocol

All agents conform to a universal, amortized interface built on top of a `BaseAgent` class to ensure consistent telemetry, capability gating, and forensics.

### The Execution Lifecycle
1. **Triggered (Event Received):** Event arrives via the Telemetry Bus.
2. **Identity Handshake & Verification:** Agent verifies the peer signature embedded in the event (using PQC keys) before proceeding.
3. **Capability Gating (PDP/PEP):** Agent's access to internal tools is restricted by its configured Semantic Intent and current certificate.
4. **Execution:** Intent-gated action is routed and performed.
5. **Signing & Output:** Agent creates an `ActionRecord`, signs it, and publishes the result back as an Event.

---

## 4. The Event Backplane & Coordination

### EventBus (SQLite WAL)
Inter-agent calls are strictly forbidden. The system utilizes a lightweight, local SQLite-backed EventBus operating in Write-Ahead Log (WAL) mode to guarantee crash-safety without needing external dependencies.
- Agents subscribe to topics based on categories and severity (e.g., `threat_intelligence/high`).
- The **Scheduler** replaces ad hoc cron jobs by injecting synthetic timing events directly into the bus.

---

## 5. Security & Cryptographic Identity

### Hybrid Post-Quantum Identity
Every agent operating in the substrate is bounded by cryptographic primitives.
- Agents use **Ed25519 + ML-DSA-65** hybrid signatures.
- Delegation Certificates and a local Revocation List (CRL) guarantee that compromised agents can be instantly defunded of their capabilities.

### The "Mutant Lock" Pattern
Effector agents (such as the Engineer or Cleaner) making file-system mutations must first secure a time-bound, signed "Mutation Token" / Mutant Lock from the Firewall Administrator. This ensures the Guardian doesn't fire false "State Compromised" alarms during a legitimate patching event.

---

## 6. The Firewall Administrator & Operational Modes

The **Firewall Administrator** acts as the overarching consciousness of the entire substrate. It never performs raw labor (like scanning logs or writing code); instead, it orchestrates the collective based on predefined risk configurations and adaptive learning.

**Cognitive Engine (Local `llama.cpp` Inference):**
To guarantee absolute operational security (OpSec), zero network latency, and continuous high availability, the Firewall Administrator is powered exclusively by a localized LLM (via `llama.cpp` compiled for Apple Silicon/Metal). This ensures that continuous, "always-on" meta-reasoning over sensitive substrate telemetry (alerts, file drifts, state changes, and patch strategies) *never* leaves the machine or incurs external cloud API bottlenecks.

**Handling Oversight & Communication:**
The Administrator manages the transition between oversight modes and adjusts verbosity thresholds. *Crucially, it is cryptographically air-gapped from external networks.* It does not integrate directly with Signal or email APIs. Instead, it delegates communication to the **Herald** agent via the EventBus:
- **HITL (Human-in-the-Loop):** Every change pauses in the Airlock. The Administrator pushes an event to the Herald to format a "nag" styling demanding human confirmation via Signal.
- **HOTL (Human-on-the-Loop):** Low/Medium risk patches execute automatically. High-risk actions prompt the Administrator to issue an alert through the Herald with a time-bound veto window.
- **HOOTL (Hands-out-of-the-Loop):** Fully autonomous operation. Generates a daily "Diplomatic Summary" event, which the Herald consumes and transmits via Signal without blocking operations.

---

## 7. Migration & Rollout Strategy

To introduce this framework safely, Tachyon Tongs will adopt a **Zero-Disruption Migration**:
1. Implement the `EventBus` and `Scheduler` backbone underneath the active system.
2. Update the `BaseAgent` Python protocol to enforce the Uniform Lifecycle while keeping ad hoc scripts running.
3. Migrate one noisy agent (e.g., Sentinel) to the new protocol to validate stability.
4. Issue Airlock approvals iteratively to migrate Guardian, Engineer, and Pathogen.
5. Instantiate the new Administrative agents (Firewall Administrator, Herald, Cleaner).

---

## 8. Paths Not Taken (Rejected Architecture Ideas)

During the design analysis of this architecture, several concepts were explicitly considered and discarded. 

### ❌ Heavy External Infrastructure
Suggestions to use Redis, PostgreSQL, and Elasticsearch for the backplane and storage were rejected. 
**Rationale:** Tachyon Tongs thrives as an Apple Silicon local-native, secure system. Enforcing large external network boundaries or heavyweight persistent daemons breaks the "no network except through safe_fetch" rule and increases the attack surface unnecessarily. We rely on SQLite-WAL and local file semantics.

### ❌ 4-Branch Taxonomy & 7-Level Tiers
Proposals offering a simplistic 4-branch model (Somatic, Purity, Vision, Command) or an overly complex 7-level structure were both dropped in favor of a balanced 6-tier architecture. 
**Rationale:** 4 layers were too rigid to properly classify Support vs Administrative functions, while 7 layers introduced artificial boundaries (like separating "Persona" into a complete tier rather than treating it as Strategy/Executive).

### ❌ Agent Responsibility Merging
Ideas to fold the Canary directly into the Sentinel, or combine the Auditor into the Guardian, were explicitly rejected.
**Rationale:** Doing so violates the "Single Responsibility" principle. Sentinel handles broad scanning, whereas Canary focuses on local trap detection. Guardian ensures runtime integrity, while Auditor performs deep forensic analysis post facto. Clean boundaries yield cleaner action audits.

### ❌ Log Processing as an Agent
Proposals to make the "Log Aggregator" an active agent were discarded.
**Rationale:** Centralized log processing should be an implicit service provided by the Telemetry Bus backplane, rather than an agent that evaluates and signs behavior. 

### ❌ Organic / Open-Ended Tool Access
Allowing agents unstructured or overly broad access to internal systems to facilitate "flexibility".
**Rationale:** Violates the principle of tight, capability-gated control (PDP/PEP integration). Every tool use must map strictly to the context approved for that agent.
