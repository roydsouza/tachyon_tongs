---
name: airlock
description: Manage the Tachyon Tongs Airlock patch staging area (list, inspect, approve, deny).
---

# 🔒 Airlock Management Skill (HITL Patch Oversight)

## Intent
To provide a secure, human-in-the-loop (HITL) gateway for reviewing and applying autonomous patches to the Tachyon Tongs substrate. This skill ensures that no code mutation is applied without forensic inspection and cryptographic re-signing.

## ⚖️ Operational Protocols

### 1. Discovery (`airlock-list`)
Enumerate all pending patches staged in the `/tmp/tachyon_airlock` directory.
- **Action**: `python3 scripts/airlock_cli.py --list`

### 2. Forensic Inspection (`airlock-inspect <id>`)
Analyze the proposed changes, including CVE metadata and file deltas.
- **Action**: `python3 scripts/airlock_cli.py --inspect <id>`

### 3. Execution (`airlock-approve <id>`)
Apply the patch and update the substrate's integrity state.
- **Action**: `python3 scripts/airlock_cli.py --approve <id>`

### 4. Rejection (`airlock-deny <id>`)
Discard risky or incorrect patches.
- **Action**: `python3 scripts/airlock_cli.py --deny <id>`

## 📜 Constraints
- **Backup Mandatory**: The `airlock_cli.py` Must create `.bak` files for all modified assets (Enforced by CLI logic).
- **Atomic Re-Sign**: Every approval MUST trigger a substrate re-sign via `IntegrityManager`.
- **Forensic Audit**: All Airlock actions are logged to `memory/strategic/CHANGE_CONTROL.md`.
