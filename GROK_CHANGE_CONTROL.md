# Question:

This is Tachyon Tongs, my Agentic Firewall that I am vibe coding using AntiGravity. I would like to make a few enhancements: (a) add change control so that any modifications to the substrate are logged, so that we can view diffs to see what changed with any update, so that we can look for errors or exploits. We already have a mechanism that tracks architectural changes. (b) add a "path not taken" log (maybe a folder or a markdown file) that documents decisions that were deliberately not made, and why we must not take that path, and (c) some kind of memory hierarchy, so that this information is relegated to the secondary, or tertiary tier, and does not contaminate the context unless needed. All these need to be markdown files. So please give me a clean and very detailed architecture change control document in markdown that I can cut and paste and hand over to AntiGravity.

# Grok: 

# ADR-0005: Enhanced Architecture Change Control System
## Comprehensive Mutation Logging with Diffs, Paths-Not-Taken Ledger, and Tiered Memory Hierarchy

**Status**: Proposed  
**Date**: 2026-03-17  
**Author**: Roy D'Souza (via Tachyon Tongs Substrate)  
**Supersedes**: None (extends Phase 19 Integrity Gating & Security Evolution + ADR-0004 Merkle Tree)

### 1. Context & Problem Statement

Tachyon Tongs already maintains high-assurance architectural tracking:
- **ADRs** (`docs/adr/`) protected by Merkle Tree (immutable hash-chain).
- **Security Evolution Ledger** (`docs/security_evolution/`) mapping Sentinel discoveries → Engineer patches.
- **Somatic Evolution** (`memory/EVOLUTION.md`) for code mutations.
- **Run & Sync Logs** (`RUN_LOG.md`, `SYNC_LOG.md`).

However, three gaps remain (explicitly requested by the Operator):

**(a) Full Change Control with Diffs**  
Any substrate modification (code, policy, config, doc) must be auditable. We need a single source-of-truth log containing **unified diffs** so operators can instantly see exactly what changed, detect errors, or forensic exploits. The existing mechanisms track *what* and *why* at high level but not the precise delta.

**(b) Paths-Not-Taken Ledger**  
Deliberate rejections (e.g., “we will never use Docker/Lima”, “we reject cloud PDP”) must be permanently documented with rationale and risks. Without this, future agents or humans risk re-exploring rejected paths, wasting quota or introducing brittleness.

**(c) Memory Hierarchy**  
All new logging must live in secondary/tertiary tiers so it does **not** contaminate primary context (TASKS.md, SYNC_LOG.md, RUN_LOG.md) unless explicitly required. This prevents token bloat while preserving instant access when needed.

**Constraint**: All enhancements MUST be implemented as **markdown files only** (no new Python classes or heavy code changes). Leverage existing workflows, StateManager signing, and Merkle Tree.

### 2. Decision

We introduce a **unified Change Control System** built entirely on markdown, extending the existing Merkle-protected evolution layer:

#### 2.1 New/Enhanced Markdown Artifacts

1. **`memory/CHANGE_CONTROL.md`** (new, append-only, prepended like RUN_LOG.md)  
   - **Purpose**: Single source of truth for **every** substrate mutation with full diffs.  
   - **Entry Format** (example):
     ```markdown
     ## Change: 2026-03-17 10:20 – Pathogen SKILL.md mutation
     **Type**: Autonomous (PathogenAgent)
     **Summary**: Updated intent_throttle from 0.1 → 0.05 after CVE-2025-54135 regression
     **Files Affected**: agents/pathogen/SKILL.md
     **Diff**:
     ```diff
     - intent_throttle: 0.1
     + intent_throttle: 0.05

