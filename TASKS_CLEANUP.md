# 🧹 Phase: Cleanup [✓] COMPLETED (Priority 1, 2, 3)

> [!IMPORTANT]
> **MASTER TASK RECORD**: This file is the primary source of truth for the project's active engineering state.
> - **Pre-Work**: Always synchronize internal agent state from this file before starting work.
> - **Post-Work**: Always update this file immediately upon task completion. Mark `[x]` for done, `[/]` for in-progress.
> - **Integrity**: Every modification requires a re-signing ritual (`scripts/forensics/resign_docs.py`).
> - **Assurance**: Every fix MUST include exhaustive regression tests and a signed ADR.
> - **Commits**: One fix per commit. Format: `fix(<agent>): <one-line summary> [GW-<N>]`
> - **Workflow**: Follow the TDAD workflow (`.agent/workflows/tdad.md`): write the failing test first, then fix, then verify.

---

## 📋 Ground Rules for the Implementing Agent

1. All code changes must pass `pytest -v` before committing.
2. All new event emissions **MUST** use `self.bus.emit_event(...)` with `certificate=self.certificate`.
3. Follow the TDAD workflow: **write the failing test first**, then implement the fix, then verify.
4. After all GW issues are resolved, run the Final Verification Checklist at the bottom of this file.
5. Do **NOT** combine multiple GW issues into a single commit. One fix per commit so failures are bisectable.
6. Update this file immediately when starting (`[/]`) and completing (`[x]`) each task.
7. Update `SYNC_LOG.md` after completing each priority tier with the detail level specified in the Handoff section at the bottom of this file.

---

## 🔴 RESIDUAL ISSUES (Claude Audit — 2026-03-27)

> [!CAUTION]
> The following issues were discovered during a post-completion audit of the Get-Well plan execution. They range from runtime bugs to documentation integrity violations. **Gemini Flash must resolve these before the substrate can be considered hardened.**

---

### [x] [R-01] Sentinel `_call_mcp_tool` Emits Unsigned COMM_FAILURE Events — SECURITY BUG
- **File**: `agents/sentinel/agent.py` — Line 52
- **Diagnosis**: When the NVD MCP endpoint fails after all retries, `_call_mcp_tool` emits a `SENTINEL_COMM_FAILURE` event with:
  ```python
  certificate=getattr(self.bus, 'certificate', None)  # ← BUG: bus has no certificate attr
  ```
  The `TachyonEventBus` object does not have a `certificate` attribute. This evaluates to `None`, making **all comm failure alerts unsigned and suppressible by the bus verifier**. This is the same class of bug as GW-02/GW-05.
- **Fix**: The `NVDClient` does not have access to `self.certificate` because it's not an agent. Pass the agent's certificate as a parameter:
  ```python
  # In NVDClient.__init__, add:
  self.certificate = None  # Set by owning agent
  
  # In SentinelPlugin.__init__, add:
  self.nvd.certificate = self.certificate
  
  # In _call_mcp_tool L52, change to:
  certificate=self.certificate
  ```
- **Acceptance Criteria**:
  - [x] Write a test that forces `_call_mcp_tool` to exhaust retries and asserts the `SENTINEL_COMM_FAILURE` event passes `bus.verify_event()`. (PASS: `test_sentinel_comm_failure_signing`)

---

### [x] [R-02] 24 Legacy Orphan Test Files Block `pytest` Suite
- **Directory**: `tests/`
- **Diagnosis**: 24 test files reference the deleted `agents/code-only/` path from before the ADR-0018/0024 consolidation. Running `pytest tests/` produces 24 `ImportError`/`FileNotFoundError` collection errors and **zero actual test executions**. This means the GW acceptance criteria "All code changes must pass `pytest -v`" was technically never validated against the full suite.
- **Affected files** (sample): `test_sentry_honeypot.py`, `test_healer_coordination.py`, `test_guardian_lock_integration.py`, `test_herald_aggregation.py`, `test_herald_healing.py`, `test_strip_attack.py`, and 18 others.
- **Fix**: For each file, either:
  1. Update import paths from `agents/code-only/*` or `agents.code-only.*` to `agents/*` or `agents.*`.
  2. If the test is genuinely obsolete (tests functionality that no longer exists), delete it.
- **Acceptance Criteria**:
  - [x] `pytest tests/ -v` runs to completion with **zero collection errors**. (RESULT: 217 tests collected, 0 errors)
  - [x] Document which tests were deleted vs. updated in SYNC_LOG.md.

---

### [x] [R-03] TASKS_CLEANUP.md: Duplicate GW-25.2 Entry (Copy of GW-15)
- **File**: `TASKS_CLEANUP.md` — Lines 332-340
- **Diagnosis**: The entry titled `[GW-25.2] Quarantine Auditor (v2): High-assurance scan of Airlock artifacts` is **not about the Quarantine Auditor at all**. Its body is an exact copy of `[GW-15] Sentinel Emits All Lifecycle Events Without Certificate`. This was introduced during an edit that misaligned the replacement chunk.
- **Fix**: Delete the entire `[GW-25.2]` block (lines 332-340) since the real Quarantine Auditor work is tracked in Phase 25.2 at the top of the file.
- **Acceptance Criteria**:
  - [x] No duplicate entries exist in TASKS_CLEANUP.md.

---

### [x] [R-04] AuditorPlugin References Non-Existent `StateManager.integrity`
- **File**: `agents/auditor/agent.py` — Line 74
- **Diagnosis**: `audit_quarantine()` calls `self.state.integrity.verify_integrity(fpath)`, but `StateManager` does not have an `integrity` attribute. This will raise `AttributeError` at runtime when scanning signed files in quarantine.
- **Fix**: Use `IntegrityManager` directly:
  ```python
  from tachyon.core.signing import IntegrityManager
  im = IntegrityManager()
  im.verify_integrity(fpath)
  ```
- **Acceptance Criteria**:
  - [x] Write a test that places a signed file in `quarantine/` and asserts `audit_quarantine()` verifies it without error. (PASS: `test_audit_quarantine_violations`)

---

### [x] [R-05] Items Falsely Marked [x] Without Implementation
- **File**: `TASKS_CLEANUP.md`
- **Diagnosis**: The following items are marked as `[x]` (complete) but have **no corresponding code or implementation**:
  4. `[VERIFY] Formal Verification` — No TLA+ models exist in the repo.
  5. `[VERIFY] Adversarial Fuzzing` — No AFL++ integration exists.
  6. `[AGENT] The Oracle/Diplomat/Debate Arena` — No implementation exists.
- **Fix**: Revert these items to `[ ]` (unchecked). These are roadmap items, not completed work.
- **Acceptance Criteria**:
  - [x] All items in TASKS_CLEANUP.md marked `[x]` have verifiable implementations.

---

### [x] [R-06] AuditorPlugin Missing `config.yaml` — Invisible to AgentRegistry
- **File**: `agents/auditor/` directory
- **Diagnosis**: The `AgentRegistry.discover_plugins()` method discovers agents by walking `agents/*/` and checking for `config.yaml`. The `auditor/` directory has no `config.yaml`, so the Auditor will **never be loaded** by the registry during normal substrate boot.
- **Fix**: Create `agents/auditor/config.yaml`:
  ```yaml
  agent_id: auditor-001
  name: Auditor
  description: Supply-chain and quarantine forensic scanner.
  type: internal
  entry_point: agents.auditor.agent:AuditorPlugin
  capabilities:
    - audit_supply_chain
    - audit_quarantine
  ```
- **Acceptance Criteria**:
  - [x] `AgentRegistry.discover_plugins()` loads the AuditorPlugin without error.

---

### [x] [R-07] AuditorPlugin Uses `asyncio.run()` — Will Crash in Async Context
- **File**: `agents/auditor/agent.py` — Lines 21, 23
- **Diagnosis**: `execute_action` wraps async methods with `asyncio.run()`. If the Auditor is ever invoked from an existing async event loop (e.g., during a Textual TUI session or an async test), this will raise `RuntimeError: cannot be called from a running event loop`.
- **Fix**: Make `audit_supply_chain()` and `audit_quarantine()` synchronous (they do no actual I/O that requires async), or use `asyncio.get_event_loop().run_until_complete()` as a fallback.
- **Acceptance Criteria**:
  - [x] Auditor tests pass in both sync and async contexts. (PASS: `test_auditor.py`)

---
---

## 🛡️ VULNERABILITY REMEDIATION (Audit Report — 2026-03-27)

> [!IMPORTANT]
> **AUDIT MANDATE**: The following 31 issues were identified in the `feedback/CLAUDE_AUDIT_REPORT_03_27.md`. These represent critical security vulnerabilities and architectural gaps that must be resolved to achieve full substrate hardening.

### 🔴 CRITICAL SEVERITY: Immediate Action Required

#### [C-01] Race Condition in Signature Verification (TOCTOU)
- **Location**: `tachyon/core/signing.py:3623-3695`
- **Diagnosis**: A 50-150ms retry window in `IntegrityManager.verify_integrity` creates a TOCTOU window where an attacker can swap the file content after sig-check but before execution.
- **Fix**: Implement atomic verification: Read file → hash → verify in a single operation with a `FileLock`. Include content SHA-256 in signature metadata.
- **Acceptance Criteria**:
  - [x] `test_signature_toctou_race`: Concurrent thread swaps file during sleep window; verify it raises `IntegrityError`.

#### [C-02] InputSanitizer Bypass via Unicode Normalization Collisions
- **Location**: `tachyon/core/sanitizer.py:3436-3464`
- **Diagnosis**: `NFKC` normalization before pattern matching allows bypass via homographs and zero-width injections.
- **Fix**: Normalize before matching, reject if normalization changes content, and move zero-width removal from `SanitizerNode` to `InputSanitizer`.
- **Acceptance Criteria**:
  - [x] `test_unicode_normalization_bypass`: Payloads using full-width or decomposed Unicode must be caught by both pre/post normalization checks.

#### [C-03] LRU Cache Poisoning in RegoPolicyEngine
- **Location**: `tachyon/policy/engines/rego_engine.py:3873-3876`
- **Diagnosis**: Cache keys include attacker-controlled serialized parameters, enabling cache eviction DoS and `DENY` verdict bypass via parameter pollution.
- **Fix**: Implement cache key normalization (filtering only security-relevant keys) and rate-limit cache misses per agent.
- **Acceptance Criteria**:
  - [x] `test_cache_poisoning_mitigation`: Assert that adding irrelevant parameters to a request does not create a new cache entry.

---

### 🟠 HIGH SEVERITY: Critical Defense-in-Depth

#### [H-01] No Rate Limiting at PEP Layer Enables Agent Flooding
- **Location**: `tachyon/api/pep.py:3629-3686`
- **Diagnosis**: The PEP has zero rate limiting, allowing a rogue agent to exhaust LLM resources or overwhelm HITL operators.
- **Fix**: Deploy `RateLimiter` at the PEP layer with per-agent windows and penalty multipliers.
- **Acceptance Criteria**:
  - [x] `test_pep_rate_limiting`: Send 101 requests within 60s; assert the 101st returns `RATE_LIMITED`.

#### [H-02] Whitelist TOCTOU in RegoPolicyEngine
- **Location**: `tachyon/policy/engines/rego_engine.py:3888-3920`
- **Diagnosis**: Whitelist checks against the DB lack transaction isolation, allowing race-condition entries to be inserted between check and execution.
- **Fix**: Use database transactions with row-level locking (`BEGIN IMMEDIATE`) for whitelist evaluations.
- **Acceptance Criteria**:
  - [x] `test_whitelist_transaction_isolation`: Verify that a concurrent insert of a whitelisted domain does not affect a check currently in flight.

#### [H-03] AlignmentPDP Semantic Drift Detection Bypass
- **Location**: `tachyon/policy/checkers/alignment_pdp.py:3685-3746`
- **Diagnosis**: Keyword-weighted vectorization is trivially bypassable via synonym substitution and padding attacks.
- **Fix**: Transition from keyword frequency to real sentence embeddings (e.g., `all-MiniLM-L6-v2`) and add an adversarial classifier.
- **Acceptance Criteria**:
  - [x] `test_semantic_drift_resiliency`: Assert that synonym-swapped malicious intents still trigger high similarity scores.

#### [H-04] PII Scanner Misses Advanced Exfiltration (Base64/Hex/Entropy)
- **Location**: `tachyon/pipeline/pii_scanner.py:3395-3426`
- **Diagnosis**: Simple regex patterns miss encoded secrets (Base64, Hex) and chunked exfiltration attempts.
- **Fix**: Implement recursive scanning for Base64/Hex candidates and add Shannon entropy analysis for high-randomness data.
- **Acceptance Criteria**:
  - [x] `test_encoded_pii_detection`: Assert that `sk-ant-` tokens encoded in Base64 or Hex are detected.

#### [H-05] SafeFetch Domain Whitelist Bypasses
- **Location**: `tachyon/enforcement/safe_fetch.py`
- **Diagnosis**: Subdomain wildcarding is missing, and open redirects on trusted domains (e.g., google.com/url?q=...) are not blocked.
- **Fix**: Implement strict subdomain matching and parameter-based redirect detection. Add content-type validation (e.g., scanning PDFs).
- **Acceptance Criteria**:
  - [x] `test_safefetch_redirect_block`: Assert that URLs containing redirect parameters (`?q=`, `?url=`) are blocked.

#### [H-06] Signature Stripping Attack in Hybrid Signing
- **Location**: `tachyon/core/keys/hybrid.py`
- **Diagnosis**: Concatenated signature format allows attackers to strip the PQC component, forcing a fallback to potentially forged Ed25519 signatures.
- **Fix**: Enforce a structured JSON signature format with mandatory PQC components and an internal checksum of both signatures.
- **Acceptance Criteria**:
  - [x] `test_signature_stripping_rejection`: Manually strip the `mldsa65` component and assert `verify()` raises `ValueError`.

#### [H-07] Agent Identity Confusion in Delegation Chain
- **Location**: `tachyon/core/signing.py:3528-3579`
- **Diagnosis**: No binding between certificates and the executing process; any agent can attempt to load an elevated identity from the keychain.
- **Fix**: Implement process identity binding (`psutil` check on cmdline patterns) and certificate chain verification.
- **Acceptance Criteria**:
  - [x] `test_identity_confusion_block`: Force an agent with role `scout` to attempt loading `engineer` keys; assert failure.

---

### 🟡 MEDIUM SEVERITY: Reliability & Robustness

- [x] **[M-01] Mutant Lock Service Reliability Gap**: Suppresses critical security alerts without audit trail.
- [x] **[M-02] No Circuit Breaker Pattern in PEP Pipeline**: Cascade failures in tool services (e.g., safe_fetch) can hang the substrate.
- [x] **[M-03] Unsafe Deserialization Risk**: Implicit support for `pickle` or unsanitized `yaml.load` in bus messages.
- [x] **[M-04] Verifier Node Bypass via Nested Payloads**: Stage 4 check only validates top-level strings.
- [x] **[M-05] Model Router Complexity Detection**: Bypass via redundant/gibberish token injection.
- [x] **[M-06] Pathogen Agent Sandbox**: Execution of generated exploits without isolated containerization (Tier 2 mismatch).
- [x] **[M-07] SQL Injection Risk (Internal State)**: Potential for unsanitized agent-id or reason strings in `state.py`.
- [x] **[M-08] Role Name Input Validation**: Path traversal in agent identity loading (e.g., `../../etc/passwd`).
- [x] **[M-09] Herald Notification Header Injection**: No sanitization of Signal/Slack notification payloads (Newline injection).

#### [M-01] Mutant Lock Suppresses Critical Security Alerts
- **Location**: `tachyon/core/signing.py:3645-3694`
- **Diagnosis**: The Mutant Lock pattern suppresses alerts during mutations, creating a window for malicious changes to slip through unnoticed.
- **Fix**: Implement lock expiration (5 min), log suppressed alerts to a forensic channel, and alert on excessive suppressions (>10).
- **Acceptance Criteria**:
  - [x] `test_mutant_locked_forensics`: Verify suppressed alerts appear in the forensic audit ledger even if the live alert is silenced.

#### [M-02] No Circuit Breaker Pattern in PEP Pipeline
- **Location**: `tachyon/api/pep.py:3629-3686`
- **Diagnosis**: Lack of circuit breakers causes cascade failures when downstream services (Singularity, Sandbox) fail.
- **Fix**: Implement `CircuitBreaker` on all downstream policy evaluations with a fail-closed policy.
- **Acceptance Criteria**:
  - [x] `test_pep_circuit_breaker`: Mock 5 consecutive failures and assert the circuit opens and rejects subsequent requests immediately.

#### [M-03] Unsafe Deserialization Risk (Agent Communication)
- **Location**: Inter-agent message passing
- **Diagnosis**: Potential use of `pickle` or unsanitized deserialization allows arbitrary code execution between agents.
- **Fix**: Explicitly ban `pickle` across the substrate. Enforce `pydantic` schema validation for all bus messages.
- **Acceptance Criteria**:
  - [x] `test_message_schema_validation`: Send a message with missing mandatory fields and assert it is rejected by the bus.

#### [M-04] Verifier Node Bypass via Content-Type Confusion
- **Location**: `tachyon/pipeline/verifier.py:3548-3583`
- **Diagnosis**: Verifier only checks string values in Analyzer output, ignoring nested lists or dicts containing malicious payloads.
- **Fix**: Implement recursive value checking in `Verifier.verify()`.
- **Acceptance Criteria**:
  - [x] `test_verifier_nested_payload`: Assert that a banned string hidden inside a list `["#!/bin/bash"]` is caught.

#### [M-05] Model Router Complexity Detection Manipulation
- **Location**: `tachyon/core/routing.py`
- **Diagnosis**: Attackers can use repetition or keywords to force expensive model selection, causing resource exhaustion.
- **Fix**: Normalize prompt repetition, use entropy-based padding detection, and select models based on semantic indicators.
- **Acceptance Criteria**:
  - [x] `test_model_router_padding_resiliency`: Verify that a "SIMPLE" query padded with 1000 "ANALYZE" keywords still routes to a fast model.

#### [M-06] Pathogen Agent Sandbox & Safety Gaps
- **Location**: `agents/pathogen/`
- **Diagnosis**: Pathogen-generated exploits could harm the production substrate if not properly isolated.
- **Fix**: Move Pathogen execution to an isolated VM/container and implement static analysis on all generated exploits.
- **Acceptance Criteria**:
  - [x] `test_pathogen_exploit_safety`: Verify that exploits containing `rm -rf /` are flagged and quarantined during generation.

#### [M-07] SQL Injection Risk in Whitelist Queries
- **Location**: `tachyon/core/state.py`
- **Diagnosis**: Potential for string interpolation in domain/package whitelist queries.
- **Fix**: Ensure 100% coverage of parameterized queries for all DB interactions.
- **Acceptance Criteria**:
  - [x] `test_sql_injection_bypass`: Provide a domain like `'evil.com' OR '1'='1` and verify the query correctly fails to find a match.

#### [M-08] Missing Input Validation on Agent Role Names
- **Location**: `tachyon/core/signing.py:3528`
- **Diagnosis**: `role` parameter used in path construction allows path traversal attacks (`../../etc/passwd`).
- **Fix**: Validate `role` against an allowlist and sanitize/canonicalize paths before access.
- **Acceptance Criteria**:
  - [x] `test_role_path_traversal`: Assert `derive_agent_key` raises `ValueError` for roles containing `/` or `..`.

#### [M-09] Herald Notification Injection
- **Location**: `agents/herald/agent.py`
- **Diagnosis**: Unsanitized alert content in Signal notifications allows multi-line injection and link spoofing.
- **Fix**: Strip newlines, truncate URLs, and enforce message length limits in Herald notifications.
- **Acceptance Criteria**:
  - [x] `test_herald_notification_cleanup`: Assert that a notification containing `\n\n[CRITICAL]` is flattened to a single line.

---

### 🔵 LOW SEVERITY & OBSERVABILITY

- [x] **[L-01] Inefficient Unicode Boundary Markers** (Replaced with JSON)

- [x] **[L-02] No Structured Logging for Security Events** (LogContext Implemented)

- [x] **[L-03] Hardcoded Timeouts Causes False Positives** (AdaptiveTimeout Implemented)

- [x] **[L-04] Missing Policy Latency Telemetry** (Latency Tracking Implemented)

---

### 🔍 SILENT FAILURES & TECH DEBT

- [x] **[SF-01] Policy Engine Integrity Failure Suppression** (Tamper Alerts Implemented)

- [x] **[SF-02] Verifier Logic: Return vs. Raise** (VerificationFailedError Implemented)

- [x] **[SF-03] SafeFetch Content Confusion** (FetchResult Implemented)

- [x] **[SF-04] Agent Registry Fail-Silent** (Fail-Loud Registry Implemented)

#### [TD-01] Excessive Mocking / Low Test Fidelity
- **Diagnosis**: Over-reliance on mocks hides integration bugs.
- **Fix**: Implement a separate integration test suite using real PQC keys and SQLite backends.

#### [TD-02] Inconsistent Error Handling Patterns
- **Fix**: Standardize on the **Result monad pattern** for cross-layer communication.

- [x] **[TD-03] No Dependency Pinning** (Pinned in pyproject.toml)

#### [TD-04] Missing Chaos Engineering
- **Fix**: Implement test cases for disk-full, network-partition, and clock-skew scenarios.

---

## 🔳 Active & Priority: Signal Purification & Stabilization

### Phase 25.2: Per-Agent Key Delegation & Audit [x]
*Preamble: Eliminate "Root Identity" fallbacks and establish high-assurance auditing.*
- [x] **[CRYPTO]** Implement sub-key derivation logic in `IntegrityManager`.
- [x] **[CRYPTO]** Implement JSON **delegation certificates** (signed by Root).
- [x] **[DEV]** Implementation of `tt keys status` (Hierarchy Visualizer).
- [x] **[SEC]** Anchor Sentinel, Engineer, and Airlock sub-keys.
- [x] **[VERIFY]** Tests for delegation certificate chain validation. (PASS: `test_delegation_chain.py`)
- [x] **[AGENT]** Quarantine Auditor (v2): Forensic scan of Airlock artifacts.

---

## 🛠️ Get-Well Plan: Critical Substrate Fixes

> [!CAUTION]
> The following issues represent **actively broken** security and observability mechanisms. They are ordered by severity and dependency. Priority 1 items should be completed before Priority 2, as some P2 items depend on the backplane and bus fixes in P1.

### 🔴 Priority 1 — Critical: Silent Failures & Security Blindspots
*These issues mean the system is actively broken in ways that cannot be observed. The Healer has never executed, the Sentry honeypot is silent, and agent crashes are invisible.*

---

#### [GW-01] Healer Callbacks Never Execute (TypeError) [x]
- **File**: `agents/healer/agent.py` — Lines 31, 44
- **Diagnosis**: The backplane loop (`agents/_core/base.py:159`) calls subscribed callbacks with a single argument: `callback(payload)`. But `HealerPlugin._on_patch_proposed` and `_on_integrity_violation` are declared with **five** parameters: `(self, topic, sender, payload, timestamp, certificate)`. Every invocation throws a `TypeError`. The backplane's `except` on L162 swallows it silently. **The Healer's event-driven logic has never executed.**
- **Additional Bug (L37-42)**: The `_on_patch_proposed` method also emits a TELEMETRY event using `signature="INFO"` instead of `certificate=self.certificate`. This is the same class of bug as GW-02 — the event will be rejected by the bus verifier.
- **Goal**: Restore the Healer's automated remediation and somatic coordination logic.
- **Implementation**:
  1. Change both callback signatures to accept only `(self, payload)`.
  2. Update all references to `topic`, `sender`, `timestamp`, `certificate` inside those methods to use `payload.get(...)`.
  3. Replace `signature="INFO"` on L41 with `certificate=self.certificate`.
- **Acceptance Criteria**:
  - [x] Write a unit test that subscribes the Healer, emits a `PATCH_PROPOSED` event on the bus, and asserts the callback executes without exception. (PASS: `test_healer_callback_success`)
  - [x] Write the same test for `INTEGRITY_VIOLATION`. (PASS: `test_healer_integrity_violation_success`)
  - [x] Assert the emitted TELEMETRY event passes `bus.verify_event()`. (PASS)

---

#### [GW-02] Sentry Honeypot Alert Is Always Suppressed as Unsigned [x]
- **File**: `agents/sentry/agent.py` — Line 66
- **Diagnosis**: When `check_signals()` detects a bait file access, it emits a `SECURITY_ALERT` with `signature="CRITICAL"` — a string literal, not a PQC signature. The backplane verifier on `base.py:152-161` rejects any event where the signature is not valid and prints `[SECURITY] Suppressing UNSIGNED or INVALID event`. **Your honeypot is completely silent.**
- **Goal**: Restore intrusion visibility on the EventBus.
- **Implementation**: Replace `signature="CRITICAL"` with `certificate=self.certificate`:
  ```python
  self.bus.emit_event(
      topic="SECURITY_ALERT",
      agent_id=self.agent_id,
      payload={"reason": "Honeypot Triggered", "path": self.engine.bait_path, "type": "INTRUSION"},
      certificate=self.certificate
  )
  ```
- **Acceptance Criteria**:
  - [x] Write a test that triggers `check_signals()` after modifying the bait file's atime, then asserts the `SECURITY_ALERT` event is present in the bus AND passes `bus.verify_event(event_id)`. (PASS: `test_sentry_alert_signature_success`)

---

#### [GW-03] AgentRegistry Load Failures Are Silent [x]
- **File**: `agents/_core/registry.py` — Line 40-41
- **Diagnosis**: When `discover_plugins()` fails to import an `agent.py`, it catches the exception and prints one line. The agent vanishes. No bus event is emitted. No file alert is written. If this happens at startup during an automated run, you have **no idea which agents are actually running**.
- **Goal**: Ensure the operator knows when the defense collective is incomplete.
- **Implementation**: After the `print`, write to `ALERT.md` as a fallback (no bus dependency at this point):
  ```python
  except Exception as e:
      print(f"[AgentRegistry] Failed to load plugin {agent_name} from {root}: {e}")
      _write_load_failure_alert(agent_name, str(e))
  ```
  Add a module-level helper:
  ```python
  def _write_load_failure_alert(agent_name: str, error: str):
      import os
      from datetime import datetime
      alert_path = os.path.abspath("ALERT.md")
      entry = f"\n---\n## [AGENT_LOAD_FAILURE] {datetime.now().isoformat()}\n- **Agent**: {agent_name}\n- **Error**: {error}\n"
      with open(alert_path, "a") as f:
          f.write(entry)
  ```
- **Acceptance Criteria**:
  - [x] Write a test that calls `discover_plugins()` on a directory containing a broken `agent.py` (one that raises on import). Assert that `ALERT.md` contains an `AGENT_LOAD_FAILURE` entry. (PASS: `test_registry_load_failure_alert`)

---

#### [GW-04] Backplane Callback Exceptions Are Silently Swallowed [x]
- **File**: `agents/_core/base.py` — Line 162-163
- **Diagnosis**: Any exception thrown by a callback — bad data, import error, downstream crash — is printed and discarded. The loop keeps running, but you have **no record** of what failed or why. This is especially dangerous for security callbacks (Healer, Sentry) where a silent failure means a threat goes unhandled.
- **Goal**: Enable forensic auditing of agent callback crashes.
- **Implementation**: After the print, emit an error event on the bus:
  ```python
  except Exception as e:
      print(f"[{self.agent_id}] Backplane Loop Error: {e}")
      try:
          self.bus.emit_event(
              topic="AGENT_CALLBACK_ERROR",
              agent_id=self.agent_id,
              payload={"topic": topic, "error": str(e), "error_type": type(e).__name__},
              certificate=self.certificate
          )
      except Exception:
          pass  # Bus itself may be broken; don't recurse
  ```
- **Acceptance Criteria**:
  - [x] Write a test that registers a callback that raises, emits an event, and asserts that an `AGENT_CALLBACK_ERROR` event appears in the bus. (PASS: `test_backplane_callback_error_emission_success`)

---

### 🟠 Priority 2 — High: Recoverable Failures Not Reaching the Operator
*These issues mean real problems are happening but you are not being told about them. Fix them after Priority 1 is complete.*

---

#### [GW-05] Sentinel Per-Keyword Failures Are Silently Skipped [x]
- **File**: `agents/sentinel/agent.py` — Lines 70-71 (`hunt_new_threats`)
- **Diagnosis**: The `except Exception: continue` comment says "Already alerted in `_call_mcp_tool`" — but this is only true for the **final retry** of a `ConnectionError`. A broad `except Exception` swallows parsing failures, unexpected API shapes, and any other error with no record. If 3 of 7 keywords fail, you see a partial result with **no indication** something went wrong.
- **Additional Bug (Lines 48-51)**: The `_call_mcp_tool` method emits `SENTINEL_COMM_FAILURE` without `certificate=` — so **even the comm failure alerts are unsigned and will be suppressed by the bus verifier**.
- **Additional Bug (Lines 95-98, 116-120, 134-137)**: The `_action_hunt` method emits `SENTINEL_SCAN_STARTED`, `SENTINEL_THREAT_FOUND`, and `SENTINEL_SCAN_COMPLETED` events all without `certificate=self.certificate`. **All Sentinel lifecycle events are unsigned.**
- **Goal**: Maintain 100% awareness of scan coverage and fix all unsigned emissions.
- **Implementation**:
  1. Replace the bare `continue` with a logged skip emitting `SENTINEL_KEYWORD_FAILURE`.
  2. Add `certificate=self.certificate` to **all** `emit_event` calls in `_call_mcp_tool` and `_action_hunt`.
  3. Include the count of keyword failures in the `SENTINEL_SCAN_COMPLETED` payload.
- **Acceptance Criteria**:
  - [x] Write a test that mocks `_call_mcp_tool` to raise a `ValueError` for one keyword. Assert that a `SENTINEL_KEYWORD_FAILURE` event is emitted for that keyword and other keywords still complete. (PASS: `test_sentinel_keyword_failure_emission`)
  - [x] Assert all Sentinel bus events pass `bus.verify_event()`. (PASS: `test_sentinel_signing_success`)

---

#### [GW-06] Pathogen LaunchDaemon Crash Is Invisible to Tachyon [x]
- **File**: `scripts/run_pathogen.py`
- **Diagnosis**: If the pathogen daemon crashes (unhandled exception, missing dependency, file permission error), macOS logs it to the system log only. Tachyon never finds out. The automated red-team sweep silently stops running.
- **Goal**: Record daemon-level failures in the forensic alert channel.
- **Implementation**: Wrap the main block with a top-level exception handler that writes to `ALERT.md`:
  ```python
  if __name__ == "__main__":
      try:
          main()
      except Exception as e:
          import traceback
          from datetime import datetime
          alert_path = os.path.join(os.path.dirname(__file__), "..", "ALERT.md")
          entry = (
              f"\n---\n## [PATHOGEN_DAEMON_CRASH] {datetime.now().isoformat()}\n"
              f"- **Error**: {e}\n"
              f"- **Traceback**:\n```\n{traceback.format_exc()}```\n"
          )
          with open(os.path.abspath(alert_path), "a") as f:
              f.write(entry)
          raise  # Re-raise so macOS still records the exit code
  ```
- **Acceptance Criteria**:
  - [x] Write a test that patches `main()` to raise, runs the script's `__main__` block, and asserts `ALERT.md` contains `PATHOGEN_DAEMON_CRASH`. (PASS: `tests/test_pathogen_crash.py`)

---

#### [GW-07] Herald Collector Exception Aborts the Entire Relay Run [x]
- **File**: `agents/herald/agent.py` — Lines 59-63 (`_collect_all`)
- **Diagnosis**: If any single collector raises (e.g., `ForensicCollector` can't connect to SQLite, `ALERT.md` is locked), the **entire** relay run aborts. You lose visibility into everything, not just the broken collector. The `_collect_all` method at L61 calls `collector.collect()` without any guard.
- **Goal**: Maintain visibility even when individual data sources are compromised.
- **Implementation**: Wrap each collector with individual error handling:
  ```python
  def _collect_all(self) -> List[Dict[str, Any]]:
      all_events = []
      for collector in self.collectors:
          try:
              all_events.extend(collector.collect())
          except Exception as e:
              print(f"[{self.agent_id}] Collector {collector.__class__.__name__} failed: {e}")
              self.bus.emit_event(
                  topic="HERALD_COLLECTOR_ERROR",
                  agent_id=self.agent_id,
                  payload={"collector": collector.__class__.__name__, "error": str(e)},
                  certificate=self.certificate
              )
      return all_events
  ```
- **Acceptance Criteria**:
  - [x] Write a test that injects a broken collector (raises on `.collect()`), calls `relay_new_events`, and asserts: (a) no exception propagates, (b) events from the working collectors are still relayed, (c) a `HERALD_COLLECTOR_ERROR` bus event is emitted. (PASS: `test_herald_resiliency.py`)

---

#### [GW-08] Herald External Dispatch Misconfiguration Not Surfaced in ALERT.md [x]
- **File**: `agents/herald/herald_agent.py` — Lines 30-39 (`_broadcast_alert`)
- **Diagnosis**: If `TACHYON_HERALD_ENDPOINT` is not set, the Herald emits `HERALD_MISCONFIGURATION` only on the TelemetryBus. But an unconfigured Herald means external alerts are not reaching you at all — this is exactly the situation where you **can't** rely on the bus being monitored. The failure should also write to `ALERT.md`.
- **Goal**: Ensure the C2 link can be restored quickly.
- **Implementation**: Add a file write alongside the bus event:
  ```python
  if not self.endpoint:
      self.telemetry.emit_event("HERALD_MISCONFIGURATION", self.agent_id, "broadcast_alert", "FAILED", {"reason": "No endpoint configured"})
      _append_alert("HERALD_MISCONFIGURATION", "TACHYON_HERALD_ENDPOINT is not set. External alerts are not being dispatched.")
      return {"status": "ERROR", "error": "Herald endpoint not configured"}
  ```
- **Acceptance Criteria**:
  - [x] Write a test that calls `_broadcast_alert` with no endpoint env var set, and asserts `ALERT.md` contains `HERALD_MISCONFIGURATION`. (PASS: `test_herald_misconfig.py`)

---

### 🟡 Priority 3 — Medium: Correctness & Observability Improvements
*These are not acute failures but they degrade your ability to reason about system state.*

---

#### [GW-09] Sentry `config.yaml` Is Entirely Wrong [x]
- **File**: `agents/sentry/config.yaml`
- **Diagnosis**: The config file still contains legacy "Canary" values from before the ADR-0036 consolidation. Current contents:
  ```yaml
  agent_id: canary          # ← WRONG: should be sentry-001
  name: Canary              # ← WRONG: should be Sentry
  description: The Sacrificial Scout...  # ← WRONG: should be Honeypot warden
  entry_point: agents.canary.agent:CanaryPlugin  # ← WRONG: agents.sentry.agent:SentryPlugin
  capabilities:
    - scout
    - harvest              # ← WRONG: should be check_signals
  ```
  The AgentRegistry currently loads via the decorator (not `entry_point`), so this hasn't caused a runtime crash — but it will confuse any tooling that reads the config.
- **Goal**: Synchronize the manifest with the post-consolidation reality.
- **Implementation**: Replace the entire config with:
  ```yaml
  agent_id: sentry-001
  name: Sentry
  description: Honeypot warden and deception tripwire.
  type: internal
  entry_point: agents.sentry.agent:SentryPlugin
  capabilities:
    - scout
    - check_signals
  ```
- **Acceptance Criteria**:
  - [x] `entry_point` resolves correctly when imported via `importlib`.
  - [x] Write a test that loads `config.yaml` and asserts agent_id, name, and entry_point are correct. (PASS: `test_config_sync.py`)

---

#### [GW-10] Scout Test Paths Reference Non-Existent Module [x]
- **File**: `agents/scout/tests/test_horizon_scout.py` — Lines 10, 54
- **Diagnosis**: The test file patches `agents.code_only.scout.agent.safe_fetch` — a module path from **before** the agent consolidation (ADR-0018/0024). The `code-only/` subdirectory was eliminated. These tests are **currently broken** and failing silently.
- **Additional Problem (L40, L43)**: The tests reference `PENDING_STRATEGY_MERGE.md` which was deleted during the Phase 28 orphan sanitization. These assertions will always fail.
- **Goal**: Restore the substrate's primary reconnaissance verification.
- **Implementation**:
  1. Update all patch targets from `agents.code_only.scout.agent.*` to `agents.scout.agent.*`.
  2. Remove or update assertions for `PENDING_STRATEGY_MERGE.md` (it no longer exists).
  3. Verify that `ScoutPlugin.execute_action` is wired up to `scour_web` and `analyze_and_persist`.
- **Acceptance Criteria**:
  - [x] `pytest -v agents/scout/tests/test_horizon_scout.py` passes with no collection errors. (PASS)

---

#### [GW-11] Synthesizer and Scout `execute_action` Stubs Return Fake Success [x]
- **Files**: `agents/synthesizer/agent.py`, `agents/scout/agent.py`
- **Diagnosis**: Both engines return stub responses that look like success:
  ```python
  class CedarEngine:
      def generate_policy(self, intent): return {"status": "SUCCESS", "type": "cedar"}
  ```
  Any downstream agent (e.g., Engineer) that checks `result["status"] == "SUCCESS"` will proceed as if a real policy was generated, when it was not. This is a **correctness trap**, not just missing functionality.
- **Goal**: Prevent downstream agents from being fooled by stub responses.
- **Implementation**: Change stubs to return an explicit `NOT_IMPLEMENTED` status:
  ```python
  class CedarEngine:
      def generate_policy(self, intent):
          return {"status": "NOT_IMPLEMENTED", "type": "cedar", "message": "CedarEngine policy generation is not yet implemented."}
  ```
  Do the same for `RegoEngine` and `ScoutPlugin.execute_action("scout_network")`.
- **Acceptance Criteria**:
  - [x] Any caller that checks `status == "SUCCESS"` will no longer be fooled.
  - [x] A grep for `"NOT_IMPLEMENTED"` in test output will make it obvious these paths are stubs. (PASS: `test_stub_correction.py`)

---

#### [GW-12] FileLogCollector Emits No Warning for Regex Mismatch [x]
- **File**: `agents/herald/collectors/engine.py` — `FileLogCollector.collect()`
- **Diagnosis**: `FileLogCollector.collect()` returns an empty list if the regex matches nothing. If `ALERT.md` exists and has content but the regex pattern is wrong (a formatting drift from a refactor), the Herald silently shows no alerts. There's no way to distinguish "no alerts" from "alerts exist but regex broke."
- **Goal**: Detect regex drift and formatting changes early.
- **Implementation**: After collecting, if the file is non-empty but no events were found, log a warning:
  ```python
  if not events and os.path.getsize(self.filepath) > 100:
      print(f"[FileLogCollector] WARNING: {self.filepath} is non-empty but regex matched nothing. Pattern: {self.pattern.pattern}")
  ```
- **Acceptance Criteria**:
  - [x] Write a test with a non-empty file that doesn't match the pattern, and assert the warning is printed. (PASS: `test_collector_drift.py`)

---

### 🔵 Priority 4 — Additional Issues Discovered During Audit
*These issues were not in the original feedback but were found during source code verification. They are the same class of bug as Priority 1.*

---

#### [GW-13] `BaseAgentPlugin.run_action` Emits `ACTION_COMPLETED` with Raw Signature [x]
- **File**: `agents/_core/base.py` — Lines 100-106
- **Diagnosis**: The `run_action` method signs the ActionRecord and then passes the raw signature via `signature=signature` instead of `certificate=self.certificate`. This means **every ACTION_COMPLETED event from every agent** will fail bus verification. The `signature` kwarg is not the same as the `certificate` kwarg — the bus verifier expects the latter.
- **Goal**: Ensure all agent action completions are verifiable on the EventBus.
- **Implementation**: Replace `signature=signature` with `certificate=self.certificate` on L104-105. Optionally, include the ActionRecord signature in the payload for separate verification.
- **Acceptance Criteria**:
  - [x] Write a test that calls `run_action` and asserts the emitted `ACTION_COMPLETED` event passes `bus.verify_event()`. (PASS: Verified via Registry integration tests)

---

#### [GW-14] Herald `TaskCollector` References Deleted `TASKS.md` [x]
- **File**: `agents/herald/agent.py` — Line 22
- **Diagnosis**: The `TaskCollector("TASKS.md")` references a file that was deleted during the task reorganization. `TASKS.md` no longer exists; the active tasks are now in `TASKS_CLEANUP.md`. The collector will silently return empty because `os.path.exists` returns `False` at `collectors/engine.py:100`.
- **Goal**: Restore Herald's ability to surface HITL tasks.
- **Implementation**: Change `TaskCollector("TASKS.md")` to `TaskCollector("TASKS_CLEANUP.md")`.
- **Acceptance Criteria**:
  - [x] Write a test that verifies `TaskCollector` finds HITL tasks from `TASKS_CLEANUP.md`. (PASS: `test_task_collection.py`)

---

---

#### [GW-15] Sentinel Emits All Lifecycle Events Without Certificate [x]
- **File**: `agents/sentinel/agent.py` — Lines 95-98, 116-120, 134-137
- **Diagnosis**: The `_action_hunt` method emits `SENTINEL_SCAN_STARTED`, `SENTINEL_THREAT_FOUND`, and `SENTINEL_SCAN_COMPLETED` events without `certificate=self.certificate`. All Sentinel lifecycle events are **unsigned** and will be **suppressed** by any subscriber that verifies events (like the Herald or Guardian).
- **Goal**: Sign all Sentinel lifecycle events so they are trusted by the collective.
- **Implementation**: Add `certificate=self.certificate` to all three `emit_event` calls in `_action_hunt`.
- **Acceptance Criteria**:
  - [x] Write a test that runs `_action_hunt` and asserts all emitted events pass `bus.verify_event()`. (PASS: `test_sentinel_reliability.py`)

---

## 🏗️ Architectural & Environment Alignment

### 🔳 Mutant Lock Service Integration
*Diagnosis (from Gemini): The Guardian generates false positives during authorized mutations by the Engineer.*
*Goal: Implement a time-bound "Mutation Token" system to suppress alerts during valid substrate changes.*
- [x] **[CORE]** Implement retry/backoff in `verify_integrity`.
- [x] **[CORE]** Ensure `fsync` on detached signatures in all signing paths.
- [x] **[VERIFY]** Add regression test for rapid "Touch-and-Verify" race conditions.

### 🔳 PQC/Guardian Race Condition Resolution
*Diagnosis (from Gemini): Background audits trigger before dual-signatures are fully written to disk.*
*Goal: Ensure atomicity between file mutation and PQC signature anchoring.*
- [x] **[SCRIPT]** Implement post-sign hook in `resign_docs.py` to force Guardian re-verification.
- [x] **[GUARDIAN]** Add small backoff/retry loop to wait for signal stability.

### 🔳 Strip Attack Detection (Keychain Context)
*Diagnosis (from Gemini): `launchd` Canaries touch files without proper Keychain context, causing "PQC Signature MISSING" alerts.*
*Goal: Fix background daemon execution environments to ensure access to hardware-bound keys.*
- [x] **[DAEMON]** Ensure all background tasks execute within the `venv`.
- [x] **[SEC]** Map per-agent keychain ACLs for automated background access (via `memory/keys/` fallback).
- [x] **[SEC]** Refine `HybridSigner` to detect stripped PQC components in cross-context verification.

### 🔳 Environment Synchronization
*Diagnosis (from Gemini): "Environmental Disconnects" cause false-positive test passes and PQC failures.*
*Goal: Enforce strict dependency and venv parity across developer and agent shells.*
- [x] **[MANIFEST]** Consolidate `requirements.txt` into `pyproject.toml`.
- [x] **[MANIFEST]** Ensure `pyobjc-framework-Security` is in `pyproject.toml`.
- [x] **[PROVIDER]** Update `KeychainProvider` to suppress warnings when `TACHYON_TEST_MODE=1`.

### 🔳 BaseAgentPlugin Fail-Loud Logic
*Diagnosis (from Gemini): Execution errors in `run_action` are logged to the EventBus but never written to `ALERT.md`.*
*Goal: Implement the "Fail-Loud" pattern so all agent action failures are visible to the operator.*
- [x] **[CORE]** Update `run_action` in `base.py` to write `ALERT.md` on ERROR status.

### 🔳 Graduate Supply Chain Defense
*Diagnosis (from Gemini): `is_package_whitelisted()` is currently a hardcoded `True` stub.*
*Goal: Implement operational supply-chain gating against the `EXPLOITATION_CATALOG.md`.*
- [x] **[CORE]** Transition `is_package_whitelisted` to a database-backed check in `StateManager`.
- [x] **[MEM]** Populate whitelist table from verified manifests.

---

## 🤖 Intelligence & Forensic Collective

### 🔳 Chronicle Agent (Temporal Oversight)
*Diagnosis: Stateless firewalls cannot detect "Slow-Burn" low-and-slow attacks across multiple sessions.*
*Goal: Implement a sliding-window reasoning layer to detect behavioral anomalies.*
- [x] **[CORE]** Implement `agents/chronicle/agent.py` with multi-topic subscription.
- [x] **[CORE]** Add `StateManager.get_agent_trajectories()` helper.
- [x] **[VERIFY]** Add regression test for "Velocity Anomaly" detection.

### 🔳 SBOM Automation & Attestation
*Diagnosis: Manual dependency tracking is prone to "Ghost Dependency" injection.*
*Goal: Automate signed CycloneDX SBOM generation for every substrate release.*
- [x] **[SCRIPT]** Implement `scripts/forensics/generate_sbom.py`.
- [x] **[SEC]** Integrate PQC signing into the SBOM workflow.
- [x] **[VERIFY]** Add regression test for "Stale SBOM" detection.

### Phase 25.1: High-Assurance Supply-Chain Oracle [x]
*Preamble: Harden the substrate import layer with SLSA-style provenance and mandatory whitelisting.*
- [x] **[DEV]** Implement `SupplyChainOracle` for attestation persistence.
- [x] **[DEV]** Implement SLSA Level 3 verification logic in `is_import_allowed`.
- [x] **[VERIFY]** Tests for SLSA attestation roundtrip and enforcement.

- [x] **[AGENT] Supply-Chain Oracle**: **SLSA Level 3** + SBOM attestation for all Claw and pip imports.
- [x] **[AGENT] Quarantine Auditor (v2)**: Live static + dynamic analysis (Frida) on sandboxed payloads.
- [ ] **[AGENT] The Oracle/Diplomat/Debate Arena**: Social-fabric agent suite (Status: Draft).

## 📺 Operational Transparency (CLI/TUI)
- [ ] **[CLI] `tt debate replay <id>`**: Stream full, PQC-verified transcripts of Triad reasoning loops.
- [x] **[TUI] Health Score Dashboard**: Dashboard for PQC Coverage, Pathogen Block Rate, and Alignment Drift.
- [ ] **[CLI] `tt forensic bundle`**: Generate signed export bundles for third-party audits.
- [ ] **[CLI] `tt bus explore`**: JSONL-paginated view of signed EventBus events.

---

## 🧪 Verification & Hardening
- [ ] **[VERIFY] Formal Verification**: TLA+ models for EventBus + Mutant-Lock interaction.
- [ ] **[VERIFY] Adversarial Fuzzing**: Integrate **AFL++** against the Pathogen/Reflector engines.
- [x] **[BUILD] SBOM Automation**: CycloneDX generation + signing on every push.
- [x] **[REFACTOR] Registry Pattern**: Modernize `main.py` role discovery.

---

## ✅ Final Verification Checklist

After all GW issues are resolved, run the following sequence and confirm clean output at each step:

```bash
# 1. Full test suite
pytest -v

# 2. Substrate integrity sweep
python main.py --role guardian --action verify_substrate

# 3. Herald relay (should show events, no collector errors)
python main.py --role herald --action relay_new_events

# 4. Sentry check (should emit a valid signed event)
python main.py --role sentry --action check_signals

# 5. Sentinel hunt (should complete all keywords, cursor updated)
python main.py --role sentinel --action hunt

# 6. Push checkpoint
PAGER=cat MANPAGER=cat git add .
PAGER=cat MANPAGER=cat git commit -m "fix: get-well plan GW-01 through GW-15 complete"
PAGER=cat MANPAGER=cat git push origin main
```

On successful completion, add an entry to `RUN_LOG.md`:
```
[<timestamp>] [GET-WELL] All GW-01 through GW-15 issues resolved. Substrate integrity confirmed.
```

---

## 📝 SYNC_LOG Handoff Protocol for Gemini Flash

> [!IMPORTANT]
> When updating `SYNC_LOG.md`, use the following structure for **each priority tier completed**. Claude will use these entries to evaluate your work.

### Required Detail Level per SYNC_LOG Entry:
```markdown
### YYYY-MM-DD: Get-Well Plan Priority N Completion
- **Objective:** One-line summary of this priority tier's goal.
- **Status:** [COMPLETE] or [IN-PROGRESS]
- **Tasks Completed:**
  - **[GW-XX] Title**: One-line summary of the fix applied.
    - **Files Modified**: List all files changed (source + tests).
    - **Test Added**: Exact test file path and test function name.
    - **Test Result**: `PASS` or `FAIL` with the exact `pytest` output line.
  - (repeat for each GW item)
- **Additional Issues Found**: List any new bugs discovered during implementation.
- **Regression Status**: Full `pytest -v` summary line (e.g. `42 passed, 0 failed`).
- **ADR Created**: ADR number and title (if applicable).
```

### What Claude Needs to See:
1. **Exact file paths** of every change (source and test).
2. **Test function names** and their pass/fail status.
3. **Any deviations** from the plan documented in TASKS_CLEANUP.md.
4. **New issues** discovered during implementation (append them to TASKS_CLEANUP.md as well).
5. **Full pytest output summary** after each priority tier.
