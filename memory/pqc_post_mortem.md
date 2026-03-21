# Phase 25.3: Post-Mortem Diagnosis (Environmental Disconnect #2)

## 🚨 The Failure
The PQC Genesis ceremony failed with a `TypeError` during the Shamir split:
`TypeError: split_secret() got an unexpected keyword argument 'num_shares'`

## 🔍 Root Cause
- **Parameter Mismatch**: The implementation in `tachyon/core/sss.py` uses the parameter name `shares_count` (or similar), but the call in `operations.py` used `num_shares`.
- **Mocking Paradox**: I relied on my internal memory of the SSS implementation instead of re-verifying the actual source code before writing the `pqc_genesis_ceremony` function.
- **Verification Gap**: I ran a "Link Status" check for `liboqs`, but I did NOT run a full dry-run of the `split_secret` logic with the 64-byte PQC seed size.

## 🛡 Prevention Strategy (The "Source-First" Mandate)
1. **Source over Memory**: I must NEVER assume a function signature (`split_secret(x, y, z)`) based on previous turns or common patterns. I MUST `view_file` the source for any internal utility before every invocation.
2. **SEC-001 (E2E First)**: I will now run a silent dry-run script (e.g., `tests/test_pqc_dry_run.py`) on the ACTUAL environment BEFORE asking the user to run any command.
3. **Mocking Paradox**: I recognize that my internal training may suggest "standard" parameter names (like `num_shares`) that conflict with the "actual" local code (`total_shares`). Local code is the sole source of truth.
4. **Signature Checklist**: Every new crypto ceremony must include a `tests/verify_<name>.py` artifact that I execute and verify in the terminal.

## 🛠 Action Plan
1. Fix `tachyon/core/keys/operations.py` with the correct `shares_count` argument.
2. Create `tests/test_pqc_ceremony_e2e.py` to verify the exact flow on M5.
3. Successfully run the check.
4. Repent and invite the user to execute the final, verified ceremony.
