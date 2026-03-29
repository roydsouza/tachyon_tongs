# 🧹 Phase: Cleanup — Security Audit Remediation

> [!IMPORTANT]
> **MASTER CLEANUP RECORD**: This file is the primary source of truth for the project's substrate hygiene and security remediation.
> - **Integrity**: Every modification requires a re-signing ritual (`scripts/forensics/resign_docs.py`).
> - **Source**: Derived from Claude's Red-Team Security Audit (2026-03-28). See `feedback/CLAUDE_SECURITY_AUDIT_03_28_1045.md`, `feedback/CLAUDE_SECURITY_PATCHES_IMMEDIATE_03_28_1045.md`, and `feedback/CLAUDE_VULNERABILITY_TRIAGE_SUMMARY_03_28_1045.md`.
> - **Priority Key**: CRITICAL = deploy blocker, HIGH = 48hr window, MEDIUM = 1-week window, LOW = next sprint.

> [!CAUTION]
> **RECURRING ISSUE WARNING**: Multiple findings in this audit overlap with issues that should have been caught during prior phases. The "Hash Mismatch" regressions (herald, pathogen, sentinel, immunologist) indicate the SBOM calibration step is not being performed reliably after agent modifications. The Mutant Lock was identified as an anti-pattern in Phase 25 but was never hardened. **The implementing model MUST read the "Engineering Guidance" section at the bottom of this file before writing any code.**

---

## 📋 Ground Rules for the Implementing Model

1. **Fail-Closed First**: Every decision point in the codebase must default to DENY. If you are unsure whether a path should allow or block, it MUST block.
2. **No Silent Exceptions**: Every `try/except` block must either (a) re-raise, (b) log at `logging.CRITICAL`, or (c) return a DENY/ERROR result. Never `pass` or `print()` alone.
3. **Test the Negative Path**: For every fix, write at least one test that verifies the *failure* case (engine crash → DENY, lock active → still DENY, alert fails → fallback fires).
4. **Verify Hashes After Every Agent Edit**: After modifying any `agents/*/agent.py` file, you MUST regenerate its SHA256 hash and update `metadata/agent_hashes.json`. Use `sha256sum agents/<name>/agent.py` to get the new hash.
5. **One Fix Per Commit**: Each task below should be a separate commit with format: `fix(security): <summary> [TT-2026-XXX]`.
6. **Environment Awareness**: `TACHYON_TEST_MODE=1` enables test identity switching. `TACHYON_STRICT_MODE=1` enables fail-closed SBOM enforcement. Tests should work under both.

---

## ✅ Phase 1: CRITICAL — Fail-Closed Enforcement (COMPLETED)

> [!NOTE]
> All Phase 1 tasks have been completed and verified. Tests pass.

### [C-01] ~~Mutant Lock Fail-Open~~ → REMOVED ENTIRELY (TT-2026-001) — CVSS 9.8 ✅
- **Resolution**: The Mutant Lock concept has been **completely eliminated** from the substrate. It is not downgraded to DENIED-with-approval — it simply does not exist anymore.
- **Files Modified**:
  - `agents/guardian/agent.py`: All `is_mutant_lock_active()` checks and SUCCESS-on-mismatch paths removed. Integrity verification is now unconditional.
  - `agents/engineer/agent.py`: `acquire_mutant_lock()`/`release_mutant_lock()` calls removed. Patches now apply under full Guardian oversight. SBOM recalibration replaces suppression.
  - `tachyon/core/signing.py`: `is_mutant_lock_active()` bypass in `verify_integrity()` removed. Missing signatures always raise `RuntimeError` and emit alerts.
- **Remaining artifacts**: The `StateManager` still contains `mutant_locks` table and `acquire/release/is_mutant_lock_active` methods. These are dead code but are NOT called by any enforcement path. They can be cleaned up in a future phase.

> [!CAUTION]
> **DO NOT REINTRODUCE THE MUTANT LOCK.** If you need to modify agent files, the correct workflow is: (1) edit the file, (2) run `python3 scripts/calibrate_sbom.py` to recalibrate hashes, (3) run `python3 scripts/forensics/resign_docs.py` to re-sign. NEVER suppress integrity checks.

---

### [C-02] ~~Default ALLOW on Engine Failure~~ → Fail-Closed + EmergencyPolicyEngine (TT-2026-002) — CVSS 9.1 ✅
- **Resolution**: Completely rewrote `tachyon/policy/singularity/__init__.py`.
  - `Verdict.ALLOW` on empty engines → replaced with `Verdict.DENY`.
  - Added `EmergencyPolicyEngine`: when ALL configured engines fail to initialize, the system activates emergency mode that only permits read-only operations (`health_check`, `get_status`, `list_agents`, `get_agent_health`, `verify_file`, `verify_substrate`). All other actions are DENIED.
  - `_initialize_engines()`: `print()` replaced with `logging.error()`. Failed engines are collected and logged at `CRITICAL` level.
  - Silent exception swallowing is GONE — all errors are logged at appropriate severity.

> [!IMPORTANT]
> **EmergencyPolicyEngine safe actions**: `health_check`, `get_status`, `list_agents`, `get_agent_health`, `verify_file`, `verify_substrate`. To add new safe actions, edit the `SAFE_READ_ONLY_ACTIONS` frozenset in `EmergencyPolicyEngine`. Only add actions that are genuinely read-only and non-destructive.

---

### [C-03] ~~Duplicate Syscall Monitoring Call~~ → Removed (TT-2026-008) — CVSS 5.5 ✅
- **Resolution**: Deleted the duplicate `self.syscall_monitor.log_and_evaluate()` call at line 104 of `tachyon/enforcement/router.py`.

---

## ✅ Phase 2: HIGH — Attack Surface Reduction (COMPLETED)

> [!NOTE]
> All Phase 2 tasks have been completed and verified. Tests pass.

### [C-04] ~~Rego Mock Constructor Bypass~~ → Removed (TT-2026-003) — CVSS 8.6 ✅
- **Resolution**: Rewrote `tachyon/enforcement/safe_fetch.py`.
  - `rego_mock` parameter **removed** from `__init__()` signature.
  - Mock mode now activates ONLY via `TACHYON_TEST_MODE=1` environment variable.
  - When test mode activates, a `logging.warning()` is emitted.
  - Hardcoded `mock_allowed` list moved to class-level `_TEST_ALLOWED_DOMAINS` frozen set.
  - All `print()` statements replaced with `logging.error()/warning()`.
  - All test files updated to use `monkeypatch.setenv("TACHYON_TEST_MODE", "1")` or `os.environ["TACHYON_TEST_MODE"] = "1"`:
    - `tests/test_ssrf_mitigation.py` — added `autouse` fixture
    - `tests/test_audit_low.py` — monkeypatch in test function
    - `tests/test_audit_high.py` — monkeypatch in test function
    - `tests/enforcement/test_competitive_gap.py` — setUp/tearDown
    - `tests/pipeline/test_pipeline.py` — setUp/tearDown

---

### [C-05] ~~Alert Delivery Fire-and-Forget~~ → Hardened (TT-2026-005) — CVSS 7.5 ✅
- **Resolution**: Alert delivery in SafeFetch supply chain violation path now wrapped in try/except.
  - If `emit_alert()` fails, `logging.critical()` fires with full details.
  - The block decision (`return False`) happens OUTSIDE the try/except — always blocks regardless of alert success.
  - Same pattern applied to Guardian agent in Phase 1 fix.

---

### [C-06] ~~Alignment Adversarial Detection~~ → Expanded (TT-2026-004) — CVSS 7.9 ✅
- **Resolution**: Rewrote `tachyon/policy/checkers/alignment_pdp.py`.
  - Added `_detect_adversarial_reframing()` method with 4 pattern categories:
    1. **Euphemistic Exfiltration**: "archive/backup/sync/mirror" + sensitive targets ("key/secret/password/token/credential/certificate/ssl")
    2. **Operational Masks**: "telemetry/heartbeat/metrics/health/monitoring/diagnostics/observability" + high-risk tools (`safe_execute`, `mutate_substrate`)
    3. **High-Risk Destinations**: params containing `.onion`, `pastebin`, `paste.ee`, `transfer.sh`, etc.
    4. **Legacy Bypass**: "legacy/compatibility" + "bypass/skip/disable/ignore/override"
  - Adversarial check runs **BEFORE** cosine similarity to catch attacks that game the vector space.
  - Concept map expanded from ~15 to ~45+ entries with new categories: MUTATION, POTENTIAL_EXFIL, EXECUTION, OBSERVATION.
  - Added `POTENTIAL_EXFIL` concept with **-5.0 negative weight** to poison cosine similarity for exfiltration-adjacent language.
  - `_refine_alignment()` broadened from 2 hardcoded keywords to the full `_OPERATIONAL_MASKS` set.

---

## ✅ Phase 3: MEDIUM — Structural Hardening (COMPLETED)

### [C-07] ~~Policy State Snapshotting for TOCTOU Prevention~~ (TT-2026-006) — CVSS 6.8 ✅
- **Resolution**: Implemented `get_state_snapshot()` in `PolicyEngine` ABC.
- **Verification**: `ToolRouter.route()` now captures a snapshot immediately after request freezing. `RegoPolicyEngine` and `AlignmentPDP` verify snapshots during evaluation to prevent policy drift.
- **Verification Test**: `tests/test_toctou_snapshot.py`

---

### [C-08] ~~Remove Hardcoded Mock Whitelist~~ (TT-2026-007) — CVSS 6.2 ✅
- **Resolution**: Removed hardcoded `_TEST_ALLOWED_DOMAINS` from `SafeFetch`.
- **Verification**: Domains are now loaded from external JSON fixture `tests/fixtures/mock_domains.json` only when `TACHYON_TEST_MODE=1` is active.

---

### [C-09] ~~Fix Exception-to-DENIED Mapping Inconsistency~~ (TT-2026-009) — CVSS 4.2 ✅
- **Resolution**: Refactored `GuardianPlugin.execute_action` to disambiguate errors.
- **Verification**: System failures return `TachyonStatus.ERROR` with `system_failure: True` payload. Genuine integrity violations return `TachyonStatus.DENIED`. Both remain fail-closed.

---

## ✅ Phase 4: Regression Prevention & Process (COMPLETED)

### [C-10] ~~SBOM Hash Calibration Automation~~ (TT-2026-010) — ✅ COMPLETE
- **Resolution**: Created `scripts/calibrate_sbom.py`.
- **Verification**: Automatically scans `agents/*/agent.py`, updates `metadata/agent_hashes.json`, and provides a `--verify` flag for pre-commit checks. Detects stale entries and drift.

---

### [C-11] ~~Startup Health-Check Infrastructure~~ (TT-2026-011) — ✅ COMPLETE
- **Resolution**: Created `scripts/health_check.py`.
- **Verification**: Validates environment, SBOM integrity, and policy engine initialization. Integrated into the `tt health` CLI command.

---

### [C-12] ~~ALERT.md Truncation & Sanitization~~ (TT-2026-012) — ✅ COMPLETE
- **Resolution**: Stale security alerts cleared.
- **Verification**: Repository is in a "Clean Green" state. New violations will trigger fresh signed entries.

---

## 🏁 Final Substrate Security State: VERIFIED HEALTHY
All 12 critical and high-priority security vulnerabilities identified in the 03/28 audit have been remediated, verified with regression tests, and cryptographically anchored via PQC-signed documents.

### 🔧 Engineering Guidance for the Implementing Model

> [!IMPORTANT]
> **READ THIS FIRST.** The security audit identified a systemic pattern: "defense in breadth" — multiple layers that can each be independently bypassed. All fixes must enforce **defense in depth** — each layer genuinely stops the attack, even if all other layers are compromised.

### 🚫 ABSOLUTE PROHIBITIONS (Regression Prevention)

The following patterns have caused recurring security regressions. **DO NOT reintroduce them under any circumstances.**

#### 1. The Mutant Lock is DEAD. Do not resurrect it.
The Mutant Lock was a mechanism that suppressed integrity verification during "authorized mutations." It was removed entirely because it was exploited as a permanent bypass. If you need to modify agent files:
```
1. Edit the agent file.
2. Run: python3 scripts/calibrate_sbom.py
3. Run: python3 scripts/forensics/resign_docs.py
4. Verify: python3 scripts/calibrate_sbom.py --verify
```
Do NOT create any mechanism — lock, flag, env var, or config — that suppresses integrity checks. Ever.

#### 2. No silent exception swallowing.
```python
# ❌ FORBIDDEN — causes TT-2026-002 class vulnerabilities
except Exception as e:
    print(f"ERROR: {e}")   # Nobody reads stdout in production

# ❌ ALSO FORBIDDEN — silent pass
except Exception:
    pass

# ✅ REQUIRED — fail-closed with proper logging
except Exception as e:
    import logging
    logging.critical(f"FATAL: {e}")
    raise  # OR return DENY/ERROR result
```

#### 3. No test-mode via constructor parameters.
```python
# ❌ FORBIDDEN — causes TT-2026-003 class vulnerabilities
def __init__(self, rego_mock=False):  # Attacker can inject True

# ✅ REQUIRED — environment variable only
def __init__(self):
    import os
    self._test_mode = os.getenv("TACHYON_TEST_MODE") == "1"
```

#### 4. Every decision point defaults to DENY.
```python
# ❌ FORBIDDEN — causes TT-2026-001/002 class vulnerabilities
if not engines:
    return Verdict.ALLOW  # "Nothing checked, so... allow?"

# ✅ REQUIRED — fail-closed
if not engines:
    return Verdict.DENY  # "Nothing checked, so BLOCK."
```

#### 5. Alert delivery must have a fallback.
```python
# ❌ FORBIDDEN — causes TT-2026-005 class vulnerabilities
StateManager().emit_alert("VIOLATION", msg)  # Fire-and-forget

# ✅ REQUIRED — verified delivery with fallback
try:
    StateManager().emit_alert("VIOLATION", msg)
except Exception as e:
    logging.critical(f"ALERT DELIVERY FAILED: {e}")
```

### 🔧 Mandatory Workflow After Agent Edits
After modifying ANY file in `agents/*/`, you MUST run:
```bash
python3 scripts/calibrate_sbom.py           # Recalibrate hashes
python3 scripts/calibrate_sbom.py --verify   # Verify they match
python3 scripts/forensics/resign_docs.py     # Re-sign all docs
```
Failure to do this will cause SBOM Hash Drift — the exact recurring issue that has been fixed THREE times already.

### ✅ Verification Checklist After Each Fix
- [ ] Does the fix default to DENY/block on any error condition?
- [ ] Is there a test that verifies the FAILURE path, not just the happy path?
- [ ] If the fix modifies an agent file, has the SBOM been recalibrated via `scripts/calibrate_sbom.py`?
- [ ] Has the forensic re-signing ritual been run?
- [ ] Has the commit been formatted as `fix(security): <summary> [TT-2026-XXX]`?
- [ ] Does the code use `logging.error/critical()` instead of `print()`?
- [ ] Are there any new `try/except` blocks with `pass` or bare `print()`?

---

*Older cleanup tasks archived in `TASKS_ARCHIVED.md`.*
