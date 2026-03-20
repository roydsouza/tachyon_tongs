# ADR-0020: Autonomous Immune Response Protocol (AIRP)

## Status
Proposed (Pending Review)

## Context
The Tachyon Tongs substrate currently relies on manual intervention for policy updates and vulnerability remediation (Airlock oversight). While the **Sentinel** and **Canary** agents identify threats, the loop to bridge "detection" to "remediation" is manual. 

To achieve high-assurance autonomic defense, we need a protocol that allows the substrate to self-evolve its policies in response to verified bypasses detected by the **Canary Honeypot**.

## Decision
We will implement the **Autonomous Immune Response Protocol (AIRP)**. This protocol defines the handoff between three core components:

1.  **Canary Role (The Sensory Organ)**:
    - Detects successful bypasses of existing policies via honeypot probes.
    - Logs detailed bypass payloads and context to `CANARY_LOG.md`.

2.  **ImmuneManager (The Nervous System)**:
    - Monitors `CANARY_LOG.md` for new bypass events.
    - Synchronizes the detection with the **EngineerRole**.
    - Tracks "Processed" events in the state layer to prevent duplicated remediation.

3.  **EngineerRole (The Remediation Engine)**:
    - Receives bypass context from the ImmuneManager.
    - Synthesizes a specific, narrow-scope Rego or Cedar policy to block the exact bypass vector.
    - Stages the new policy as an **Airlock Proposal**.
    - Runs a local regression test suite to ensure the new policy does not break existing tool functionality.

## Technical Requirements
- All autonomic policies MUST be staged in `tachyon/enforcement/policies/auto_immune.rego`.
- All evolutions MUST be signed by the Sentinel Agent's private key (simulated).
- The portal for final approval MUST remain the **Airlock** (HITL model).

## Consequences
- **Positive**: Significantly reduced MTTM (Mean Time To Mitigation).
- **Positive**: Continuous, automated hardening of the "Reverse Firewall".
- **Negative**: Risk of over-fitted policies causing false positives if the synthesis logic is too broad.
- **Security**: The "Airlock" gate remains the primary defense against "Adversarial Policy Poisoning".

---
*Signed by: Sentinel Agent*
*Date: 2026-03-20*
