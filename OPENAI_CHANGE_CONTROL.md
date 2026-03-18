# Question:

This is Tachyon Tongs, my Agentic Firewall that I am vibe coding using AntiGravity. I would like to make a few enhancements: (a) add change control so that any modifications to the substrate are logged, so that we can view diffs to see what changed with any update, so that we can look for errors or exploits. We already have a mechanism that tracks architectural changes. (b) add a "path not taken" log (maybe a folder or a markdown file) that documents decisions that were deliberately not made, and why we must not take that path, and (c) some kind of memory hierarchy, so that this information is relegated to the secondary, or tertiary tier, and does not contaminate the context unless needed. All these need to be markdown files. So please give me a clean and very detailed architecture change control document in markdown that I can cut and paste and hand over to AntiGravity.

# OpenAI:

# Tachyon Tongs — Change Control, Decision Logging, and Memory Hierarchy Architecture

## Overview

This document defines a structured, self-auditable change control and memory management system for the Tachyon Tongs Agentic Firewall. It introduces three core enhancements:

1. **Substrate Change Control System** — Full traceability of all modifications with diff visibility and exploit detection hooks.
2. **“Path Not Taken” Decision Log** — Explicit recording of rejected architectural decisions and associated risk reasoning.
3. **Hierarchical Memory Architecture** — Tiered memory model to prevent context pollution while preserving long-term intelligence.

These systems are designed to integrate with existing architectural change tracking while remaining lightweight, composable, and agent-friendly.

---

# 1. Substrate Change Control System

## 1.1 Objectives

* Ensure **full transparency** of all substrate changes
* Enable **diff-based inspection** for exploit detection
* Maintain **immutable audit trails**
* Support **automated regression and anomaly detection**
* Provide **LLM-readable structured logs**

---

## 1.2 Directory Structure

```
/tachyon_tongs/
│
├── substrate/
│   ├── current/
│   └── snapshots/
│
├── change_control/
│   ├── logs/
│   │   ├── YYYY-MM-DD_change_log.md
│   │   └── index.md
│   │
│   ├── diffs/
│   │   ├── YYYY-MM-DD_diff.md
│   │
│   ├── approvals/
│   │   ├── pending/
│   │   └── approved/
│   │
│   └── metadata/
│       └── change_registry.json
```

---

## 1.3 Change Log Format (Markdown)

Each change must generate a structured markdown entry:

````markdown
# Change Log Entry

## Metadata
- Change ID: TT-CC-YYYYMMDD-XXXX
- Timestamp: ISO-8601
- Agent: <agent_name>
- Trigger: (manual | autonomous | external input)
- Risk Level: (low | medium | high | critical)

## Summary
Brief description of the change.

## Files Modified
- path/to/file1
- path/to/file2

## Diff Summary
High-level explanation of what changed.

## Full Diff
```diff
<insert diff here>
````

## Rationale

Why this change was made.

## Expected Impact

* Functional impact
* Security implications

## Validation

* Tests executed
* Results

## Rollback Plan

Steps to revert change.

## Approval Status

* Pending / Approved / Rejected
* Approved By: <agent/human>

````

---

## 1.4 Diff Generation Strategy

- Use deterministic diffing:
  - `git diff` (if repo-backed)
  - or structured AST diff for code
- Store:
  - **Raw diff**
  - **Semantic summary (LLM-generated)**

---

## 1.5 Security Hooks

Each change triggers:

- **Exploit Scan**
  - Pattern matching for:
    - prompt injection
    - unsafe eval
    - privilege escalation
- **Anomaly Detection**
  - Compare against baseline behavior
- **Regression Tests**
  - Automatically generated where applicable

---

## 1.6 Change Registry (Machine-Readable)

```json
{
  "change_id": "TT-CC-20260317-0001",
  "timestamp": "2026-03-17T10:15:00Z",
  "files": ["memory/hierarchy.md"],
  "risk": "medium",
  "status": "approved",
  "hash_before": "abc123",
  "hash_after": "def456"
}
````

---

# 2. “Path Not Taken” Decision Log

## 2.1 Purpose

Prevent re-exploration of **known-dangerous or suboptimal design paths**, especially under adversarial pressure or model drift.

---

## 2.2 Directory Structure

```
/memory/
├── decisions/
│   ├── taken/
│   │   └── YYYY-MM-DD_decision.md
│   │
│   ├── rejected/
│   │   └── YYYY-MM-DD_path_not_taken.md
│   │
│   └── index.md
```

---

## 2.3 Path Not Taken Template

```markdown
# Path Not Taken

## Decision ID
TT-DNT-YYYYMMDD-XXXX

## Proposal
Description of the idea that was rejected.

## Context
Why this was considered.

## Risks Identified
- Security risks
- Architectural risks
- Long-term degradation risks

## Reason for Rejection
Clear explanation of why this path must not be taken.

## Failure Mode Simulation
(Optional but recommended)
What would likely happen if this were implemented?

## Exploit Potential
How an attacker might leverage this path.

## Permanent Constraints
Rules to prevent reconsideration:
- Constraint 1
- Constraint 2

## Related Decisions
Links to other decisions.

## Review Policy
- Never revisit / revisit after X conditions
```

---

## 2.4 Usage Rules

* Agents must:

  * Check this log before major architectural decisions
  * Reference it when rejecting similar proposals
* Treated as **“soft constraints with strong bias”**

---

# 3. Memory Hierarchy Architecture

## 3.1 Objectives

* Prevent **context contamination**
* Preserve **long-term intelligence**
* Enable **selective recall**
* Support **agent reasoning efficiency**

---

## 3.2 Memory Tiers

### Tier 0 — Active Context

* Immediate working memory
* Included in prompt
* Small, high-signal

---

### Tier 1 — Operational Memory

* Recent decisions
* Active architectural state
* Frequently accessed

Location:

```
/memory/operational/
```

---

### Tier 2 — Strategic Memory

* Change logs
* Accepted decisions
* Patterns and lessons

Location:

```
/memory/strategic/
```

---

### Tier 3 — Archival / Cold Memory

* Path Not Taken logs
* Historical diffs
* Deprecated designs

Location:

```
/memory/archive/
```

---

## 3.3 Memory Promotion / Demotion Rules

| Action  | Condition             |
| ------- | --------------------- |
| Promote | Frequently referenced |
| Demote  | No access over time   |
| Archive | Explicitly deprecated |

---

## 3.4 Retrieval Policy

Agents must:

1. Start with Tier 0
2. Query Tier 1 if needed
3. Escalate to Tier 2 for reasoning
4. Only access Tier 3 when:

   * investigating anomalies
   * detecting repeated mistakes
   * auditing

---

## 3.5 Context Injection Guardrails

* Tier 2/3 data:

  * Must be summarized before injection
  * Never directly injected raw
* Use:

  * embeddings or indexing
  * retrieval scoring

---

## 3.6 Memory Index File

```markdown
# Memory Index

## Tier 1
- operational_state.md
- recent_decisions.md

## Tier 2
- change_logs/
- decisions_taken/

## Tier 3
- paths_not_taken/
- archived_diffs/
```

---

# 4. Integration with Agentic Loop

## 4.1 Change Lifecycle

```
Propose → Validate → Diff → Log → Scan → Approve → Commit → Archive Snapshot
```

---

## 4.2 Decision Lifecycle

```
Propose → Evaluate → Accept OR Reject → Log → Index → Enforce Constraints
```

---

## 4.3 Memory Flow

```
Experience → Tier 1 → (promote) → Tier 2 → (archive) → Tier 3
```

---

# 5. Anti-Exploit Design Principles

* **Transparency over cleverness**
* **Immutable logs**
* **Explicit reasoning trails**
* **Separation of concerns (memory tiers)**
* **No silent mutations**
* **Diff-first validation**

---

# 6. Optional Enhancements (Future)

* Semantic diffing using AST + embeddings
* Automated “suspicion scoring” for changes
* Self-generated regression tests
* Cross-agent consensus for approvals
* Cryptographic signing of change logs

---

# 7. Minimal Viable Implementation (MVP)

If implementing incrementally:

1. Start with:

   * Change logs + diff storage
2. Add:

   * Path Not Taken logs
3. Then:

   * Memory tier folders + retrieval rules

---

# Final Notes

This system is designed to:

* Make Tachyon Tongs **self-auditing**
* Reduce **silent failure modes**
* Encode **institutional memory**
* Improve **resilience against adversarial drift**

It should remain:

* Markdown-native
* Agent-readable
* Incrementally extensible

---

**End of Document**


