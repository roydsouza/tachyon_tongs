# Tachyon Tongs: Operational Strategy

Our operational strategy focuses on active resilience over static defense, transitioning from localized incident response to generalized "Systemic Paranoia" through an amortized defense model.

## 1. Amortized Defense (Substrate-First)

The architecture is predicated on centralizing threat intelligence and security execution.

### Centralized Threat Intelligence
The Sentinel agent functions as a continuous intelligence aggregation service (Scout) rather than a simple peer. It routinely audits uncurated web intelligence feeds (e.g., GitHub Advisories, NVD, arXiv) searching for adversarial machine learning tactics and Prompt Injection strategies to update the `EXPLOITATION_CATALOG.md`.
- **The Result:** When the Sentinel synthesizes a threat, the mitigations automatically propagate to the centralized Daemon policies, instantly inoculating all connected downstream agents in the workspace.

### Mandatory Interception (The Substrate Law)
Agents and tools are prevented from executing network egress (`safe_fetch`) or system operations directly. All capabilities are proxied through the Substrate Daemon to enforce Open Policy Agent (OPA) gating.
- **The Rationale:** If an agent is manipulated via an upstream vulnerability, it cannot bypass the Daemon to access root systems or extract raw, unvetted intelligence payloads because the Guardian Triad explicitly sanitizes all pipeline traffic.

### Verification Enforcement (The Bouncer)
The final stage of the Guardian pipeline, the **Verifier Agent**, acts as an exit node integrity check. It structurally enforces:
- Verification of unbroken Unicode boundaries indicating a successful containment string.
- Non-existence of unauthorized Markdown downloads or remote execution scripts.
- Terminal parsing for shell-injection invocations.

If the analytical reasoning node is successfully tricked into disregarding safety protocols via a sophisticated payload, the Verifier catches the semantic discrepancies and aborts the execution run entirely.

## 2. The Feedback Loop: Sentinel -> Substrate -> Pathogen

The system remains resilient through an autonomous, continuous improvement lifecycle:

1. **Discovery:** The Sentinel aggregates an uncataloged Prompt Injection vector from an external advisory stream.
2. **Cataloging:** Structurally verified threats are atomically committed to `EXPLOITATION_CATALOG.md` via the SQLite `StateManager`.
3. **Daemon Ingestion:** The Substrate Hot-Reloads updated rules or regex definitions to counter the newly documented heuristic patterns.
4. **Adversarial Synthesis (Pathogen):** The active Red Team agent, the Pathogen, autonomously reads the new entry within `EXPLOITATION_CATALOG.md`. Operating under unprivileged tenant rules, it dynamically synthesizes a targeted payload utilizing the new attack vector and initiates an assault against the Substrate to guarantee the new security patches effectively trap the exploit.

## 3. Self-Improvement Protocol

The pipeline actively audits diagnostic efficiency over time:
- If the air-gapped Analyst continuously fails to categorize vulnerability types, the Sentinel generates explicit structural tasks to update its prompt taxonomy.
- If an intelligence target within the `SITES.md` registry fails to yield any actionable zero-days or mitigations over a 30-day epoch, the endpoint is queued for deletion to optimize API quotas and compute bandwidth.
