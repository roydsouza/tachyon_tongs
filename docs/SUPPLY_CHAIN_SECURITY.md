# Supply Chain Security in Tachyon Tongs 🛡️📦

Tachyon Tongs provides high-fidelity protection against software supply chain attacks targeting autonomous agents, specifically focusing on the "Hallucination Squatting" and "Dependency Confusion" vectors.

## 1. The Threat Model
Autonomous agents often use tools to install missing dependencies or fetch libraries from the internet. This introduces several risks:
- **Hallucination Squatting**: An agent "hallucinates" a non-existent package name. An attacker proactively registers this name on PyPI with a malicious payload.
- **Dependency Confusion**: An agent fetches a malicious public package that shadows a private internal one.
- **Vulnerable Upstreams**: Legitimate packages may contain known CVEs that could be used for Remote Code Execution (RCE).

## 2. Implementation Architecture

### A. Integrity Gating Agent (`src/agents/integrity_agent.py`)
The **Integrity Agent** acts as a middleman for all library-related operations. It intercepts:
- `pip install` commands.
- Dynamic `import` calls (via the Substrate Proxy).

### B. Vulnerability Scanning
The system integrates with `pip-audit` and `safety` to perform real-time scans against the **Python Packaging Advisory Database**.
- If a package has a known CRITICAL CVE, the Substrate Daemon rejects the capability token.

### C. Deterministic Capability Binding
Agents are prohibited from requesting arbitrary packages. All dependencies must be:
1.  Defined in the agent's `SKILL.md`.
2.  Verified against a **Cryptographic Hash Registry** in `src/state_manager.py`.

## 3. Validation & Verification

### Running Automated Checks
To verify the integrity of the current environment, run:
```bash
# Audit all installed dependencies
source venv/bin/activate
pip-audit
```

### Regression Testing
The `tests/test_supply_chain_integrity.py` suite simulates:
- **Typo-squatting detection**: Attempting to install `requessts` instead of `requests`.
- **Vulnerability interception**: Attempting to load a known-vulnerable package version.

## 4. State of the Art Comparison
Unlike traditional CI/CD scanners, Tachyon Tongs provides **Runtime Supply Chain Security**. We don't just scan at build time; we intercept the agent's intent *at the moment of execution*, preventing compromised or "hallucinated" code from ever entering the Tier-0 sandbox.
