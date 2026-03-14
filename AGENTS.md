# 🧠 AGENTS.md: The Tachyon Tongs Map

This document is the primary entry point for AI agents. It defines the structural boundaries, behavioral principles, and the "Memory as Documentation" hierarchy of the Tachyon Tongs project.

## 🛡️ Control Plane
- **Identity & Mission**: [.agent/rules/IDENTITY.md](file:///.agent/rules/IDENTITY.md)
- **Behavioral Principles (Soul)**: [.agent/rules/SOUL.md](file:///.agent/rules/SOUL.md)
- **Global Constraints**: [.agent/rules/MISSION.md](file:///.agent/rules/MISSION.md)

## 📂 Project Hierarchy
- **Core Substrate**: `src/` (The secure execution engine)
- **Agent Manifests**: `agents/` (In-Band agent configurations)
- **Intelligence Layer**: `intelligence/` (Threat catalogs and research sites)
- **Memory Layer**: `memory/` (Episodic logs and architectural history)
- **Governance**: `policies/` (OPA Rego intent gating)
- **Administrative**: `scripts/` (Orchestration and administrative tools)

## 🧠 Memory Documents
- **Long-term Memory**: [MEMORY.md](file:///MEMORY.md) (Standard procedures and key decisions)
- **Active Task Plan**: [memory/task_plan.md](file:///memory/task_plan.md) (Current session focus)
- **Evolutionary Ledger**: [memory/evolution.md](file:///memory/evolution.md) (Codebase mutations)
- **Run Log**: [memory/run_log.md](file:///memory/run_log.md) (Execution audits)

## 📜 Execution Backlog
- **Backlog**: [TASKS.md](file:///TASKS.md) (Primary engineering tracker)
- **Roadmap**: [docs/ROADMAP.md](file:///docs/ROADMAP.md) (Strategic milestones)

## 🤖 Automation Mandates
All agents MUST follow these automation steps before task completion:
1. **Task Currency**: Update `TASKS.md` to reflect current state.
2. **Regression Testing**: Add and run regression tests for all new functionality.
3. **Documentation**: Update all relevant `.md` files to match the implementation.
4. **Sync**: Push all changes to the `tachyon_tongs` repository.
