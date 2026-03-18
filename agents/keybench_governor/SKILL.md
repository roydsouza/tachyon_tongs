# 🗝️ Keybench Governor Skill

## Description
This skill ensures that `docs/KEYS.md` remains the single source of truth for Tachyon Tongs' cryptographic posture. It mandates documentation updates for any security-layer mutation.

## Core Rules
1. **Sync on Mutation**: Whenever changes are made to `tachyon/core/signing.py` or any script involving key generation (e.g., `sign_adrs.py`), you MUST review and update `docs/KEYS.md`.
2. **Audit Disclosure**: If a new key is added to the substrate, it must be added to the "Key Registry" table in `docs/KEYS.md`.
3. **Hygiene Enforcement**: Ensure all scripts and tests follow the "Environment Injection" rule. HARDCODED KEYS ARE CAUSE FOR SUBSTRATE REJECTION.

## Trigger Workflow
- **Before Commit**: Run a scan for new `os.environ.get()` calls related to secrets and consolidate them into `KEYS.md`.
