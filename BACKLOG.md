# 📋 Tachyon Tongs: Strategic Engineering Backlog

This backlog synthesizes high-fidelity security audits from **Grok** and **Gemini** (as of 2026-03-23). It serves as the primary technical roadmap for hardening the substrate against the **Agentic Inversion**.

---

## 🛡️ 1. Critical Security Remediation
High-severity gaps identified in active `ALERT.md` and `RUN_LOG.md` findings.

*   **[ ] ASI05: Semantic-Drift Bypass Hardening**
    *   Replace probabilistic cosine-similarity gating with a standalone **Alignment PDP** (Policy Decision Point).
    *   Implement "Multi-Turn Adversarial Refinement" before high-stakes tool execution.
    *   **Ref:** ADR-0041 candidate.
*   **[ ] Unified Mutant-Lock Service**
    *   Move `acquire_mutant_lock` out of `StateManager` into a dedicated service.
    *   Add **Secure Enclave-backed tokens** and mandatory 60s automatic expiry.
    *   Enforce CRL (Certificate Revocation List) cross-checks.
*   **[ ] Hardened PQC Mandate**
    *   Modify `hybrid.py` to enforce a **Fail-Closed** policy: if `ML-DSA-65` cannot be generated/verified, the ActionRecord is rejected.
*   **[ ] Model Integrity Monitoring**
    *   Implement nightly cryptographic hashing of `mlx_lm` weights against a pinned manifest.
    *   Automate quarantine if structural drift is detected in the local model cache.

---

## 🧬 2. Modular Architecture & Pipeline Refinement
Moving from prototype implementations to robust, pluggable substrate primitives.

*   **[ ] Skill-Only Agent Factory**
    *   Formalize `agents/_core/skill_factory.py` to materialize agents directly from `SKILL.md` frontmatter.
*   **[ ] Unified Forensic Ledger**
    *   Consolidate `ALERT.md`, `RUN_LOG.md`, and `EVOLUTION.md` into a single, append-only **SQLite Forensic Table** with PQC-signed rows.
*   **[ ] Policy Synthesis Pipeline (LangGraph-style)**
    *   Merge Engineer + Synthesizer into a reusable Directed Acyclic Graph (DAG) for autonomous patching.
*   **[ ] Local Model Local-Reinforcement**
    *   Implement **LoRA Fine-Tuning** loop: Turn Airlock outcomes (approve/deny) into daily local model updates to internalize operator "Vibe".

---

## 🤖 3. Intelligence & Forensic Agents
New specialized agents categorized under the **Immune Collective (Phase 31)**.

*   **[ ] Chronicle (Temporal Forensics)**: Detects "slow-burn" attacks via 72h-horizon vector analysis of the EventBus.
*   **[ ] Supply-Chain Oracle**: Enforces **SLSA Level 3** and SBOM attestation for all `pip` and Claw imports.
*   **[ ] Quarantine Auditor (v2)**: Performs live `Frida` hooks and static analysis on sandboxed payloads, feeding results to Pathogen.
*   **[ ] Historian/Oracle/Diplomat**: Complete the planned Phase 31 social-fabric agent deployments.

---

## 📺 4. Operational Transparency & CLI
Enhancing the "Aesthetic" and forensic auditability of the substrate.

*   **[ ] `tt debate replay <id>`**: Stream full, PQC-verified transcripts of the Triad (Skeptic/Analyst/Engineer) reasoning.
*   **[ ] TUI Health Dashboard**: Real-time visualization of PQC Coverage %, Pathogen Block Rate, and Alignment Drift.
*   **[ ] `tt forensic bundle`**: Generate cryptographically anchored export bundles for third-party audits.
*   **[ ] `tt bus explore`**: JSONL-paginated view of signed EventBus traffic with inline verification icons.

---

## 🧪 5. Verification & Forensic Hardening
*   **[ ] Formal Verification**: Develop TLA+ models for EventBus + Mutant-Lock interaction to prove absence of TOCTOU.
*   **[ ] Adversarial Fuzzing**: Integrate **AFL++** against the Pathogen/Reflector mutation engines.
*   **[ ] SBOM Automation**: Generate and sign CycloneDX manifests on every `git push`.

---

> **Note:** This backlog is a living document. Every entry here must be preceded by a signed ADR before implementation begins.
