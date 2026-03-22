---
description: Test-Driven Agent Development (TDAD) Workflow
---

# Test-Driven Agent Development Workflow

This workflow should be executed whenever you are asked to implement a new feature, component, or complex fix mapping to an established specification in Tachyon Tongs. It anchors code generation to deterministic reliability.

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

## Step 6: Determinism & Static Analysis (Refactor Phase)
1. Run syntax verification, type hints validation, and code scans.
2. (Optional but recommended) Run tests a second time to ensure outputs and generation states do not fluctuate across separate processes.
3. Review code to ensure no implicit behavior remains.
