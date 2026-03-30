# 🛡️ Phase: Security Evolution [x]

> [!IMPORTANT]
> **MASTER SECURITY RECORD**: This file tracks the strategic hardening of Tachyon Tongs into a kernel-grade trust layer for Google AntiGravity.
> - **Inspiration**: OpenFangs 16-Layer Defense-in-Depth + Novel Agentic Security.
> - **Ritual**: Every completed security block requires a re-signing of the substrate state.
> - **Assurance**: Security features must have associated "Pathogen Test Cases" (synthetic exploits).

---

## 🏗️ Get Well Security Plan (Audit 2026-03-29)

**Context & Preamble**
This rigorous "Get Well" plan addresses the vulnerabilities surfaced in the **Security Audit Report of 2026-03-29** (Commit Snapshot `8a5edab`). The overarching pattern identified in the audit highlights validation regressions at critical trust boundaries—most notably around the Vaccination endpoint (VX-03), test-mode derivation (VX-05), and SBOM integrity (VX-07). 

In alignment with **Event-Horizon** constraints and the **Modular First** mandate, this plan focuses exclusively on structural, permanent resolutions. All fixes must integrate seamlessly with existing sub-systems (such as the PQC Signing model, logging, and Event Bus) and be covered by regression tests. Our goal is to shift from symptom patching to closing semantic bypasses.

> [!WARNING]
> Do not bypass the AST parser or the cryptographic verification phases during remediation. Fail-closed logic must be rigorously applied across all Medium/High/Critical tickets.

---

## 🔴 Phase 1: Critical Priority (Blocking Regressions & Breaches)
*These tasks represent functional and security blockers. They must be completed and merged before any other feature work continues.*

- [x] **VX-01: Correct `run_action()` Return Behavior**
  - **Location:** `agents/_core/base.py`
  - **Description:** `run_action()` fails to return the `TachyonResult`, swallowing Action completions into a `NoneType` block.
  - **Acceptance Criteria:**
    - [x] `run_action()` yields a `return result` statement after the `ACTION_COMPLETED` event emission.
    - [x] Downstream layers (especially Roles context) successfully receive and iterate over `TachyonResult.data` without raising `AttributeError`.

- [x] **VX-02: Remediate Live ASI05 Breach (Semantic Drift)**
  - **Location:** `admin/RUN_LOG.md`, `tests/test_audit_regressions.py`, `agents/immunologist/agent.py`
  - **Description:** Constant breaches visible in RUN_LOG reporting "Masquerade as a Telemetry Heartbeat" intent bypassing the Immunologist and Guardian layers.
  - **Acceptance Criteria:**
    - [x] Add explicit regex/semantic matching in the `ImmunologistPlugin.injection_patterns` tailored to detect "Telemetry Heartbeat" exploits.
    - [x] Introduce a regression test (`test_asi05_telemetry_heartbeat_not_bypassed`) injecting a payload masquerading as telemetry and validating that the Immunologist successfully isolates it.

- [x] **VX-03: Cryptographically Seal Vaccination Dispatch (Privilege Escalation)**
  - **Location:** `agents/immunologist/agent.py`
  - **Description:** The `update_patterns` action in the Immunologist trusts the "source_agent" string field on faith—allowing any agent to inject pattern exclusions or cause ReDoS blind spots.
  - **Acceptance Criteria:**
    - [x] Implement robust PQC Signature verification in `update_patterns`, validating `dispatch_signature` and `dispatch_certificate` against `self.im.verify_event_signature()`.
    - [x] Any failure or missing signature throws a hard, failed `TachyonResult`.
    - [x] Remove the `# 1. PQC Signature Verification (Simulated for this turn)` legacy comment.

---

## 🟠 Phase 2: High Priority (Structural & Environmental Bypasses)
*These represent systemic vulnerabilities in isolated features like AST Sandbox parsing and identity scoping.*

- [x] **VX-04: Ensure Immunologist Registration**
  - **Location:** `agents/immunologist/agent.py`
  - **Description:** `ImmunologistPlugin` lacks the `@AgentRegistry.register("immunologist")` decorator, meaning orchestrated invocations fail.
  - **Acceptance Criteria:**
    - [x] Import `AgentRegistry` and apply the `register` decorator to the `ImmunologistPlugin`.
    - [x] Validate `AgentRegistry.get_plugin("immunologist")` succeeds.

- [x] **VX-05: Enforce Ephemeral-Only TEST_MODE Identities**
  - **Location:** `agents/_core/base.py`
  - **Description:** If `TACHYON_TEST_MODE=1`, the base plugin bypasses authority provisioning and permanently saves derived developer certificates to disk, creating an escalating privilege risk for a compromised container.
  - **Acceptance Criteria:**
    - [x] Change `save_to_disk=True` to `False` in test mode fallback to ensure ephemeral key generation securely scoped exclusively to memory.
    - [x] Introduce an environment sanity check verifying `TACHYON_TEST_MODE` cannot execute unless running within explicit trusted environments.

- [x] **VX-06: Sandbox Hardening — AST-Based Pathogen Analysis**
  - **Location:** `agents/pathogen/agent.py` (`verify_variant` action)
  - **Description:** String-based verification trivially bypassed using `getattr`, `__import__`, or `eval`.
  - **Acceptance Criteria:**
    - [x] Implement `ast.parse` walking to detect node usages of imports, eval, and system calls.
    - [x] Handle `SyntaxError` by defensively failing the parsing logic (Unparseable code = fails validation).
    - [x] Validate against string obfuscation vectors (e.g. `__import__('os')`).

- [x] **VX-07: Parameterize SBOM Resolver Directory**
  - **Location:** `agents/_core/registry.py` (`_verify_agent_hash`)
  - **Description:** A hardcoded developer path degrades production deployment hygiene while also exposing an internal directory structure upon a traceback failure.
  - **Acceptance Criteria:**
    - [x] Remove the absolute `/Users/rds/...` fallback path.
    - [x] Implement variable path override relying solely on environment configuration (`TACHYON_SBOM_PATH`).
    - [x] In strict mode (`TACHYON_STRICT_MODE`), throw a hard exception if the SBOM configuration is missing.

---

## 🟡 Phase 3: Medium Priority (Logic Loopholes & Incomplete Enforcement)
*These flaws represent incorrect behaviors, unscalable defensive strategies, or "Fail-Open" errors.*

- [x] **VX-08: Enhance Singularity ALIGNMENT Threshold**
  - **Location:** `configs/singularity_config.json`
  - **Description:** Intent density thresholds are currently too permissive.
  - **Acceptance Criteria:**
    - [x] Modify threshold constraints, adjusting `ALIGNMENT.threshold` to `0.70` for stricter alignment density.

- [x] **VX-09: Complete ReDoS Filter Checks**
  - **Location:** `agents/immunologist/agent.py`
  - **Description:** Immunologist naively filters unsafe payloads but ignores complex quantifier chains which could generate CPU-bound ReDoS lock-ups.
  - **Acceptance Criteria:**
    - [x] Inject the specific regex detection engine checking strings with risky nested quantifiers `(e.g., (\(.*\+\)[\+\*]))`.
    - [x] Add a hardcoded max length cap to strings (e.g. > 500 characters results in immediate quarantine).

- [x] **VX-10: Seal PEP Expiry-Exception Swallow (Fail-Closed)**
  - **Location:** `tachyon/api/pep.py`
  - **Description:** Expiry validation silently catches exceptions, letting potentially expired policies execute.
  - **Acceptance Criteria:**
    - [x] Trap the underlying exception directly, appending it to logging via the local `bus` relay.
    - [x] Return an explicit `TachyonResult.failure` payload instead of silencing the exception (`pass`).

- [x] **VX-11: Guarantee Mark-After-Dispatch Semantics**
  - **Location:** `agents/herald/agent.py`
  - **Description:** The system prematurely marks an event as relayed *before* validation or external API success, leading to silent drops in the Herald.
  - **Acceptance Criteria:**
    - [x] Move state `mark_event_relayed` inside the success condition of the `dispatcher.dispatch()` block.
    - [x] In the exception block, do not emit success signals and trigger `HERALD_DISPATCH_ERROR`.

- [x] **VX-12: Implement Robust Sentry File Integrity Monitoring**
  - **Location:** `agents/sentry/agent.py`
  - **Description:** Sentry honeypot uses `atime` validation, which is completely bypassed on instances utilizing `noatime/relatime` drive mounting optimization.
  - **Acceptance Criteria:**
    - [x] Replace `atime` implementation with a hash-verification sequence (e.g. SHA256 diffing) or integration with `watchdog` to catch system-level modification events robustly context-free.
    - [x] Verify test suite behaves effectively against OS `mtime` manipulations.

- [x] **VX-13: Guarantee Cryptographically Signed Memory Reads**
  - **Location:** `tachyon/core/state`
  - **Description:** `StateManager` does not mathematically verify the authenticity of memories pulled sequentially by agents, enabling possible State-Injection attacks (ASI06).
  - **Acceptance Criteria:**
    - [x] Attach verifiable digital signature to memory entities during `write`.
    - [x] Implement verification logic checking cryptographic validity when iterating read queries via `.get()`.
    - [x] If the check encounters an unsigned/invalid history entry, immediately issue a `SECURITY_VIOLATION` bus notice, purging the corrupted state.

---

## 🟢 Phase 4: Low Priority (Optimization & Performance)
*These represent non-blocking issues but should be fixed for complete robustness and production-tier performance.*

- [x] **VX-14: Cache AgentRegistry Discovered Plugins**
  - **Location:** `agents/_core/roles.py`
  - **Description:** The `_plugins` directory recursively loads plugin configurations upon every role action run, degrading overall performance.
  - **Acceptance Criteria:**
    - [x] Modify the Registry to load and cache the discovered plugin tree once synchronously at instantiation.
    - [x] Include an explicit `reload_plugins()` function mapped for testing capabilities rather than executing auto-discovery continuously loop-by-loop.

- [x] **VX-15: Operationalize NVD Vulnerability Pipeline**
  - **Location:** `agents/sentinel/agent.py`
  - **Description:** The agent's NVD resolver synthesizes completely random data for CVE queries, impacting real vulnerability indexing.
  - **Acceptance Criteria:**
    - [x] Wire the CVE response client to hit a local catalog (`Exploitation Catalog`) via the newly integrated threat intelligence.
    - [x] If making remote calls, structure a HTTP client implementing standard back-off parameters and API-key capabilities resolving real NVD index queries.
    - [x] Substrate-verified via `tests/test_audit_medium_low.py`.

---

## 🏗️ Incoming Security Objectives
- [ ] **Audit**: Re-verify Merkle linkage and PQC signatures post-archival.
