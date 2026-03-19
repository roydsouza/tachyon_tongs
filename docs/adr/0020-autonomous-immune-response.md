# ADR-0020: Autonomous Immune Response Protocol

## Context
The Tachyon Tongs substrate now possesses proactive threat intelligence (Sentinel) and proactive vulnerability scouting (Canary). However, the bridge between *detection* and *remediation* currently requires manual initiation.

## Decision
We will implement an **Immune System** loop that autonomicizes the "Sense-to-Patch" transition.
The **ImmuneManager** will monitor the `CANARY_LOG.md` for "BYPASSED" status entries. Upon discovery, it will:
1.  Synthesize a **Mutation Intent** (e.g., "Add a regex guard for bypass pattern X").
2.  Trigger the **EngineerRole** to generate a candidate `.rego` or `.cedar` policy.
3.  Initiate the **Airlock Debate** (Skeptic/Meta-Critic) for the proposed policy.
4.  Stage the validated patch in the **Airlock** for final HITL approval.

## Status
Proposed.

## Constraints
- **Isolation**: The ImmuneManager must operate with read-only access to the logs and limited "Propose" access to the Airlock.
- **Fitness Scoring**: The system will track "Fitness Scores"—patches that pass the Pathogen's regression tests earn higher scores. 
- **Rollback**: Every immune patch must include an automated revert script.

## Consequences
- **Positive**: Near real-time reaction to novel prompt injections.
- **Negative**: Risk of "Policy Bloat"—the immune system might generate overly restrictive policies that hinder agent performance (False Positives).
