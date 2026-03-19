# 🛠️ Tachyon Tongs: Substrate Change Control

This file is the single source of truth for **every** substrate mutation (code, policy, config, or core documentation). It provides forensic traceability via unified diffs.

---

## 📅 Change Log

### 🔵 Change: 2026-03-18 – P0 Security Sweep & Forensic Re-Sign
**Type**: Structural / Security
**Agent**: AntiGravity
**Summary**: Fixed the state integrity corruption loop, implemented input sanitization, established atomic file-level locking for the catalog, and upgraded the entire ADR substrate to High-Assurance HVAC signatures.

**Files Affected**:
- `tachyon/core/state.py`
- `tachyon/core/signing.py`
- `tachyon/core/sanitizer.py`
- `tachyon/agents/base.py`
- `tachyon/agents/guardian_ids.py`
- `scripts/sentinel.py`
- `docs/adr/0016-aggregate-security-hardening.md`
- `docs/adr/MANIFEST.json`

**Diff Summary**:
- Added `f.flush()` and `os.fsync()` to all Markdown exports in `StateManager` and `IntegrityManager`.
- Wrapped `export_catalog` in an exclusive `fcntl` lock using `EXPLOITATION_CATALOG.md.lock`.
- Injected `InputSanitizer` (NFKC + regex) into `BaseTachyonAgent` and `sentinel.py`.
- Re-signed ADRs 0001-0016 with HVAC (HMAC) sidecars.

---

### 🔴 Change: 2026-03-18 – Neutralization of Rogue Patch 'CVE'
**Type**: Security / Intervention
**Agent**: AntiGravity
**Summary**: Detected and denied a malicious/suboptimal patch proposal (`CVE`) that attempted to inject an unsafe `eval()` endpoint into `tachyon/enforcement/daemon.py`. 

**Action taken**:
- Hardened `scripts/airlock_cli.py` to handle structural variance in patch JSON.
- Forensicly inspected the patch and identified the `eval()` injection.
- Formally denied the patch, purging it from the `/tmp/tachyon_airlock` staging area.
- Emitted a `PATCH_DENIED` alert to the substrate.

**Forensic Signature**: `json.decoder.JSONDecodeError` and `AttributeError` were triggered and resolved during inspection of the rogue payload.

---
*Next entry here.*
