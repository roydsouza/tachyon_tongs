---
description: Test-Driven Agent Development (TDAD) Workflow
---

# Test-Driven Agent Development Workflow

This workflow should be executed whenever you are asked to implement a new feature, component, or complex fix mapping to an established specification in Tachyon Tongs. It anchors code generation to deterministic reliability.

## Step 0: Synchronize with Master Task File (Pre-Work)
Read `TASKS_CLEANUP.md` and synchronize your internal state with the master backlog.
Mark the task you are about to work on as `[/]` (in-progress) in `TASKS_CLEANUP.md`.
// turbo

## Step 1: Formulate Specifications
Ensure you have a complete technical specification containing requirements, acceptance criteria, test strategies, and interface constraints.
If absent, ask the human operator for validation of your synthesized specification.

## Step 2: Generate the Test Suite (Red Phase)
Write comprehensive unit tests ensuring all acceptance criteria and constraints in the specification are modeled.
`pytest` is the default standard.

## Step 3: Run Baseline Verification (Witness Failure)
Execute the specific test file to definitively prove the implementation is missing or flawed.
```bash
# Example (adjust target accordingly)
pytest -v path/to/tests/test_feature.py
```
*You must observe these tests fail before moving forward.*

## Step 4: Generate Implementation (Green Phase)
Write the strict, strongly-typed, implementation code designed completely to pass the previously defined test suite. 

## Step 5: Verification and Validation (Pass tests)
Execute the tests against the new implementation. 
// turbo
```bash
pytest -v path/to/tests/test_feature.py
```

## Step 6: Determinism & Hygiene (Refactor Phase)
1.  **Hygiene Compliance**: Verify that NO test artifacts (e.g., `.db`, `.wal`, `.shm`) have leaked into the root directory. ALL transient data must be in `tests/tmp/`.
2.  **Static Analysis**: Run syntax verification, type hints validation, and code scans.
3.  **Determinism**: (Optional but recommended) Run tests a second time to ensure outputs do not fluctuate.
4.  **Review**: Ensure no implicit behavior remains.

## Step 7: Commit & Synchronize (Post-Work)
1. Mark the completed task as `[x]` in `TASKS_CLEANUP.md`.
2. **Forensic Ritual**: Execute the mandatory substrate anchoring:
   - `python3 scripts/calibrate_sbom.py`
   - `python3 scripts/forensics/resign_docs.py`
3. Commit with format: `fix(<agent>): <one-line summary> [GW-<N>]`
4. After completing a full priority tier, update `SYNC_LOG.md` with the detail level specified in the Handoff section of `TASKS_CLEANUP.md`.
// turbo
```bash
python3 scripts/calibrate_sbom.py
python3 scripts/forensics/resign_docs.py
PAGER=cat MANPAGER=cat git add .
PAGER=cat MANPAGER=cat git commit -m "fix(<agent>): <summary> [GW-<N>]"
```
