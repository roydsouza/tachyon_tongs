# Phase 22: Self-Evolving Policies & Immune Response

Phase 22 transitions the Tachyon Tongs substrate from a **Fixed Defense** model to an **Autonomic Immune System**.

## 1. Core Mechanics: What will it do?
The substrate will begin to "think" about its own safety rules in response to the environment:
- **Pathogen Fitness Scoring**: The `Sentinel` role will evaluate incoming threats (CVEs) not just by severity, but by **Substrate Fitness** (e.g., "Does this exploit a dependency we actually have?"). High-fitness threats trigger an "Immune Response."
- **Dynamic Policy Mutation**: The `Engineer` role can propose mutations to `tachyon/policy/pdp.py` or `sanitizer.py` to neutralize new classes of threats before they are even exploited.
- **Capability Gating**: Introduction of **Ephemeral Tokens** for tool-use. An agent's permissions are temporarily restricted if the substrate "detects inflammation" (a high-severity breach attempt).

## 2. Safety & Effectiveness: How do we know it's safe?
We rely on **Defense-in-Depth** and **Human-in-the-Loop (HITL)** gates:
- **The Airlock Gate**: No evolved policy can be applied to the substrate without a human `APPROVED` signal in the Airlock.
- **Architectural Regression**: Every mutation is auto-tested against the **ADR Baseline**. If a new policy violates a signed ADR (like ADR-0004 or ADR-0017), the mutation is auto-aborted.
- **Skeptic Oversight**: The `SkepticAgent` is programmed to be "pessimistic" about every mutation, specifically looking for ways a new rule could be used against the system (e.g., "Would this new rule block the human operator?").

## 3. Monitoring: How do I watch it?
Monitoring is handled through three forensic channels:
- **`EVOLUTION.md` (Forensic Pulse)**: Every "mutation intent" and "fitness score" is logged here with HMAC signatures. It is a chronological record of how the system is changing.
- **Airlock Dashboard**: You will see "Proposed Mutations" appearing as patches. You can use `/airlock` to inspect the "Debate Tree" (why the Engineer thinks it's good vs. why the Skeptic thinks it's risky).
- **Guardian Heartbeat**: The `GuardianIDS` runs periodically. If an autonomous evolution causes a "Merkle Mismatch" or violates a sidecar signature, it will flag a `CRITICAL` finding in `memory/strategic/CHANGE_CONTROL.md`.

## Summary
Phase 22 is not "black box" AI. It is **signed, auditable evolution** where the human remains the ultimate "Root of Trust."
