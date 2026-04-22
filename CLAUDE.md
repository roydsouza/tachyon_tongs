# Tachyon Tongs — Context for Claude

**[📍 Back to Map](../CLAUDE.md)**

## 1. Project Overview

**Tachyon Tongs** is an adaptive, post-quantum agentic firewall for zero-trust agentic environments. It defends against prompt injection, context manipulation, and polymorphic attacks targeting AI agents. The system combines an air-gapped LLM (llama.cpp) for real-time reasoning with a continuous adversarial co-evolution loop (Pathogen vs. Sentinel).

This is a **primary, actively developed security project**. All changes require additional process (see §5).

## 2. Technical Stack

- **Language:** Python (agents), Rust (performance-critical components)
- **Cryptography:** Ed25519 + ML-DSA-65 hybrid post-quantum signatures (NIST FIPS 204, Level 3)
- **Root of Trust:** Apple Secure Enclave (Touch ID-gated, non-extractable keys)
- **LLM:** llama.cpp (air-gapped, local inference)
- **Policy Engine:** OPA/Rego
- **Target:** Apple Silicon M5

## 3. Architecture

```
Policy Enforcement Point (PEP)  →  event_horizon/
Policy Decision Point (PDP)     →  singularity/
Adversarial Loop:
  Pathogen (Red Team)            — Metamorphic attack synthesis
  Sentinel (Blue Team)           — Autonomous vulnerability research
Darwin-Gödel Machine (DGM)      →  Darwin-Godel-Machine/  (sub-project)
```

**Governance modes:** HITL (Human In The Loop) → HOTL (Human On The Loop) → HOOTL (Human Out Of The Loop)

## 4. Sub-Projects

- `Darwin-Godel-Machine/` — Evolutionary agent architecture for self-improving firewall logic
- `event_horizon/` — PEP placeholder (spinning up)
- `singularity/` — PDP placeholder (spinning up)
- Future: `hyperagent/` and other peer experimental projects

## 5. Secure SDLC — REQUIRED for Every Change

**Every mutation to this project must include a signed ADR.**

1. **Examine existing ADRs:** Read `docs/adr/` to understand format and chaining
2. **Locate signing code:** Find the hybrid post-quantum signing tooling in the repo
3. **Chain the ADR:** Each ADR references the hash of its predecessor, anchored to `MANIFEST.json`
4. **Sign:** Use Ed25519 + ML-DSA-65 hybrid scheme (keys in Secure Enclave)

See `docs/SDLC.md` for the full Secure SDLC reference.

## 6. Threat Model

Every architectural decision maps to `docs/THREAT_MODEL.md` (OWASP-2026-ASI taxonomy). Keep this document updated when adding new capabilities.

## 7. Workflows & Agent Expectations

- **Opening ritual:** `git pull` → read `SYNC_LOG.md` → review `docs/adr/` for latest ADR
- **TASKS.md contract:** Mark in-progress with `/`, complete with full checkmark, update `SYNC_LOG.md` after each task
- **Multiple TASKS files:** Check `tasks/` subdirectory for `TASKS_*.md` files in addition to root `TASKS.md`
- **Testing:** Full regression suite required before marking any task done
- **Documentation sync:** `THREAT_MODEL.md`, `WHITEPAPER.md`, ADR chain, and `SYNC_LOG.md` must stay in sync with implementation
- **Tier:** Rigorous (signed ADRs, full test coverage, threat model updates, conventional commits)

## 8. Governance Process

Process law: `~/antigravity/agents/PROCESS.md` (read on every session open).

Two complementary layers — both required:
1. **Forge/Crucible gate** — session discipline, no-inflight enforcement, governance file guard
2. **Signed ADR** — cryptographic provenance for every mutation (Ed25519 + ML-DSA-65, see `docs/SDLC.md`)

| Gate command | When |
|:-------------|:-----|
| `python3 forge/gate.py session-start` | Start of every Forge session |
| `python3 forge/gate.py lock <task-id>` | Before beginning a task |
| `python3 forge/gate.py pre-submit` | Before filing to `crucible-inbox/` |
| `python3 forge/gate.py unlock` | After CLEARED verdict received |
| `python3 crucible/gate.py session-start` | Start of every Crucible session |
| `python3 crucible/gate.py pre-verdict --scripts-run` | Before filing to `crucible-verdicts/` |

**Escalation triggers (route to Claude Code via `analyst-inbox/`):**
- Any change to `docs/THREAT_MODEL.md` or `docs/SDLC.md`
- Any change to cryptographic key management or Secure Enclave integration
- ADR chain discontinuities (missing predecessor hash)
- Any change to `CLAUDE.md` or harness gate files
