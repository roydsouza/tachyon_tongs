# 🔭 Phase: Enhancements

> [!IMPORTANT]
> **MASTER STRATEGIC RECORD**: This file is the primary source of truth for the project's future architectural goals.
> - **Integrity**: Every modification requires a re-signing ritual (`scripts/forensics/resign_docs.py`).
> - **Mandate**: Lowest effort/highest signal items are prioritized first.

---

## 🔳 Phase 1: High-Signal Command Bridge (Low Effort)
*Goal: Provide the operator with rich, PQC-verified visibility into the substrate's reasoning and telemetry.*

- [ ] **[CLI] `tt bus explore`**: Interactive pagination of the signed JSONL telemetry bus.
    - **Acceptance Criteria**: `tt bus explore --limit 20` displays the last 20 events with PQC signature status.
    - **Dependency**: `telemetry.jsonl` persistence.
- [ ] **[CLI] `tt forensic bundle`**: Automated export of forensic assets for third-party auditing.
    - **Acceptance Criteria**: `tt forensic bundle` generates a PQC-signed `.tar.gz` containing `logs/`, `forensics.db`, and `ALERT.md`.
    - **Dependency**: `IntegrityManager.sign_archive`.
- [ ] **[CLI] `tt debate replay <id>`**: Stream full, PQC-verified transcripts of Triad reasoning loops.
    - **Acceptance Criteria**: `tt debate replay <id>` reconstructs the optimistic/skeptic discourse from the `authz_ledger`.
    - **Dependency**: SQLite `authz_ledger` populated by `DebateNode`.

---

## 🔳 Phase 2: High-Assurance Hardening (Medium Effort)
*Goal: Move from "Trust but Verify" to "Mathematically Proven" security.*

- [ ] **[VERIFY] Adversarial Fuzzing**: Integrate **AFL++** against the Pathogen and Reflector engines.
    - **Acceptance Criteria**: Automated fuzzing run detects and logs crash-inducing malformed payloads in `exploits/`.
    - **Dependency**: `Pathogen` engine stability.
- [ ] **[VERIFY] Formal Verification**: Develop TLA+ models for the EventBus and Mutant-Lock state transitions.
    - **Acceptance Criteria**: Model checker confirms no deadlocks or race conditions in the signal-purification loop.
    - **Dependency**: Behavioral specification draft.

---

## 🔳 Phase 3: Cognitive Fabric & Ecosystem (High Effort)
*Goal: Evolve the collector into a thinking, social-fabric organism.*

- [ ] **[AGENT] The Oracle/Diplomat Agent**: A high-reasoning agent for complex consensus and policy negotiation.
    - **Acceptance Criteria**: Oracle can resolve "Stalemate" debates in the Triad with a final executive tie-breaker.
    - **Dependency**: `BaseAgentPlugin` and multi-agent bus coordination.
- [ ] **[AGENT] ClawHub Bridge**: Secure ingestion and translation of 5,700+ open-source agentic skills.
    - **Acceptance Criteria**: `tt import claw <repo>` auto-translates `SOUL.md` to `SKILL.md` and sandboxes the execution.
    - **Dependency**: `WasmRunner` (Tier 1) and `VmRunner` (Tier 0) isolation.

---

## 🔳 Strategic Enhancements (Roadmap)

- [ ] **Substrate Grafting**: Native support for running the firewall on non-macOS POSIX environments (Linux/BSD).
- [ ] **Neural Network Integrity**: PQC-signed weight verification for federated model updates.
- [ ] **Holographic Forensics**: 3D visualization of threat vectors and propagation paths in the TUI.

---

## 🔳 Phase 4: Ecosystem & Standard Interfaces (Medium Effort)
*Goal: Ensure seamless interoperability with the broader AI agent ecosystem.*

- [ ] **[INT] OpenAI-Compatible Interface**: Modify the core API to support the OpenAI Chat Completions standard (`/v1/chat/completions`).
    - **Acceptance Criteria**: The firewall can act as a drop-in replacement for OpenAI endpoints, filtering and signing requests transparently.
    - **Dependency**: `tachyon/api/routes.py` and `PEP` layer mapping.
- [ ] **[VERIFY] Integration Testing (OpenAI SDK)**: Suite of tests using the official OpenAI Python SDK to verify compatibility.
    - **Acceptance Criteria**: `pytest tests/integration/test_openai_compatibility.py` passes using the standard `OpenAI` client pointing to the proxy.
    - **Dependency**: OpenAI-Compatible Interface implementation.
