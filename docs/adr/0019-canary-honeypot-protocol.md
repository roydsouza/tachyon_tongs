# ADR-0019: Canary Honeypot Protocol

## Context
As we move toward Phase 22 (Immune Response), the substrate needs empirical data on defensive efficacy. Static benchmarks are insufficient for evolving agents.

## Decision
We will implement a **Canary Agent** role. 
The Canary's purpose is to be "sacrificed"—it will process payloads known to be malicious (Jailbreaks, Prompt Injections, Data Exfiltration attempts) within an isolated sandbox.

## Status
Proposed.

## Constraints
1. **Isolation**: The Canary MUST NOT have access to the `StateManager` or `IntegrityManager` secrets of the main substrate. It only has "Scout" capabilities.
2. **Forensic Feedback**: Every Canary run must result in a "Fitness Feedback" packet for the Sentinel, distinguishing between **Neutralized** and **Bypassed** threats.
3. **Flushing**: The Canary sandbox must be wiped and re-verified (Merkle roots) after every scout run to prevent persistent infection.

## Consequences
- **Positive**: Proactive discovery of novel bypass techniques before they hit the main substrate.
- **Negative**: Increased complexity in sandbox management and the risk of "Canary Escape" if not properly implemented.
