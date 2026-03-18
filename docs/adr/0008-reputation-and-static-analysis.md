# ADR-0008: Intelligence-Driven Enforcement (Reputation & Static Analysis)

## Status
Proposed (Phase 16)

## Context
Standard policy engines (OPA/Cedar) handle deterministic access control but struggle with dynamic threats like malicious domains or vulnerable code payloads. To achieve "High-Assurance," the substrate must move toward intelligence-driven gating that inspects the *quality* and *risk* of the data being fetched or executed.

## Decision
We are introducing a "Competitive Gap" security layer:

1.  **Domain Reputation Engine**: A scoring system for URLs in `safe_fetch`. 
    - Trusted domains (e.g., `google.com`, `github.com`) receive high scores.
    - Known bad or "Squatting" domains receive low scores.
    - Threshold-based blocking in `safe_fetch.py`.
2.  **Pre-Execution Static Analysis**: Integrating `StaticAnalyzer` (Bandit-lite) for Python payloads in `apple_sandbox.py`.
    - Any code payload attempting `os.system`, `eval`, or using hardcoded secrets will be rejected *before* sandbox entry.
3.  **Semantic Alignment**: Implementing `AlignmentChecker` in `tachyon/enforcement/alignment_checker.py`.
    - Uses cosine similarity between agent `intent` and `action_payload`.
    - Detects drift where technical execution deviates from declared goal.

## Consequences
- **Positive**: Proactive defense against zero-day URLs and common coding vulnerabilities; reduced reliance on manual blocklists.
- **Negative**: Increased latency for initial tool calls due to scanning/lookup; potential for false positives in legitimate administrative scripts.
- **Maintenance**: Requires a curated and updated `domain_reputation.json`.
