---
description: Manage the Tachyon Tongs Airlock patch staging area (list, inspect, approve, deny).
---

# 🔒 Airlock Management Workflow (HITL)

Use this workflow to review and authorize autonomous patch proposals.

## 1. 📦 List Pending Patches
Enumerate all patches currently staged in the `/tmp/tachyon_airlock` directory.
- Run: `python3 scripts/airlock_cli.py --list`

## 2. 🔍 Inspect a Patch
Review the specific code deltas and CVE metadata for a given patch ID.
- Run: `python3 scripts/airlock_cli.py --inspect <patch_id>`

## 3. ✅ Approve and Apply
Authorize the patch, apply the changes, and re-sign the substrate state.
- Run: `python3 scripts/airlock_cli.py --approve <patch_id>`

## ❌ Deny and Discard
Reject a risky or incorrect patch and purge it from staging.
- Run: `python3 scripts/airlock_cli.py --deny <patch_id>`

---
> [!IMPORTANT]
> All approve/deny actions are forensicly logged to `memory/strategic/CHANGE_CONTROL.md`.
