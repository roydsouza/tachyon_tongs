# 🛠️ Tachyon Tongs: Administrative Command Center

This document serves as the primary operational guide for managing the Tachyon Tongs substrate and its autonomous security agents.

---

## 🛰️ Sentinel Operations (Blue Team)
The Sentinel agent is responsible for continuous threat intelligence and substrate hardening.

### `sentinel.py`
**Description**: The primary entry point for the Sentinel agent.
**Usage**:
- `python3 sentinel.py --manual`: Trigger an immediate scanning run.
- `python3 sentinel.py --verbose 2`: Run with maximum reasoning transparency (see the Analyst's thoughts).
- `python3 sentinel.py --cron`: Standard scheduled execution (used by `launchd`).

---

## 📦 Airlock Management (Governance)
When the Sentinel identifies a potential zero-day, it stages proposed patches in the Airlock for human review.

### `scripts/airlock_cli.py`
**Description**: The CLI for inspecting, approving, or denying staged security patches.
**Usage**:
- `python3 scripts/airlock_cli.py --list`: List all pending patches in `/tmp/tachyon_airlock/`.
- `python3 scripts/airlock_cli.py --inspect <CVE_ID>`: View the proposed code changes for a threat.
- `python3 scripts/airlock_cli.py --approve <CVE_ID>`: Apply the patch to the source tree and re-sign the state.
- `python3 scripts/airlock_cli.py --deny <CVE_ID>`: Reject the patch and purge it from staging.

---

## ⚡ Security Drills (Red Team)
Continuous validation of the substrate's defensive ceiling.

### `scripts/zero_day_drill.py`
**Description**: Orchestrates simulated adversarial attacks to test the Pathogen and Sentinel interaction.
**Usage**:
- `python3 scripts/zero_day_drill.py`: Execute a full mutation-defense drill.
- Results are logged to `docs/zero_day_drills.md`.

---

## 🛡️ State & Integrity (Substrate)
Manual controls for the cryptographic security layer.

### `IntegrityManager` (via Python)
**Description**: Tools for manually signing or verifying critical state files (e.g., `intelligence/tachyon_state.db` or `EXPLOITATION_CATALOG.md`).
**Usage**:
```python
# Re-sign the exploitation catalog manually
from tachyon.core.state import StateManager
sm = StateManager()
sm.integrity.sign_document("EXPLOITATION_CATALOG.md")
```

---

> [!NOTE]
> **Project Hygiene**: Visual assets are located in `assets/` and test configurations in `configs/`.

---

> [!IMPORTANT]
> **Operational Protocol**: Always check [ALERT.md](file:///Users/rds/antigravity/tachyon_tongs/ALERT.md) before performing administrative tasks. If a `STATE_COMPROMISED` alert is active, verify the physical files before re-signing.
