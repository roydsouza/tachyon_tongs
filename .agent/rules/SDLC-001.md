# Deterministic Generation & Robust SDLC (SDLC-001)

## Philosophy
To combat LLM flakiness resulting from context drift, non-deterministic generation, and implicit assumptions, Tachyon Tongs mandates a strictly deterministic, test-driven approach during generation and implementation phases.

## Constraints

1. **Specification-First Development**:
   You must establish and agree upon explicit technical specifications before any code is generated. All requirements must include machine-verifiable acceptance criteria and test strategies.

2. **Test-Driven Agent Development (TDAD)**:
   You must NEVER write implementation code without first generating tests to verify it.
   - You must execute the test suite and verify it *fails* before writing any code.
   - You must verify the test suite *passes* after implementation.
   - You should endeavor to explicitly check for deterministic reproducibility via multiple executions when flakiness is suspected.
   
3. **Zero-Implicit Behavior**:
   - Use strict type-hinting for all implementations (`mypy`-compliant).
   - Ensure you use contract-first interface designs (using `typing.Protocol` or equivalent boundaries).

4. **Multi-Stage Validation**:
   When proposing or writing large blocks of code, ensure you factor in:
   - Syntax validation
   - Type Checking (e.g., static analysis)
   - Security Validation (e.g., using `bandit` or checking against `EXPLOITATION_CATALOG.md`)
   - Pre-commit verification

> **Note**: Enforce the usage of the `/tdad` workflow when tasked with developing comprehensive features or components.
