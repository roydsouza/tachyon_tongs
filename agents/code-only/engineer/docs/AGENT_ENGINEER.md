# 🛠️ Agent: Engineer (The Automated Remediator)

## Overview
The Engineer Agent is the surgical limb of the Tachyon Tongs organism. Its primary mission is to autonomously synthesize remediation patches, evolve security policies (Rego/Cedar), and verify fixes through automated regression tests.

## Operational Mechanics

### 1. Triggers
The Engineer is typically triggered by:
- **Synthesizer Request**: When a new policy is synthesized, the Engineer applies it to the substrate.
- **Canary Failure**: When a Canary scout identifies a bypass, the Engineer attempts to patch the vulnerability.
- **Manual Intervention**: Triggered by a human operator through the Airlock to remediate a known issue.

### 2. Configuration
The Engineer operates in the `tachyon/agents/engineer/` directory:
- **Surgical Tools**: Uses `MetalAccelerator` for patch synthesis and policy evolution.
- **Verification Loop**: Integrates with `pytest` to ensure patches do not break existing substrate functionality.

### 3. Capabilities
- `apply_and_test(patch_files, test_code, cve_id)`: Orchestrates the full remediation lifecycle—branching, patching, and verification.
- `evolve_policy(context)`: Generates and stages OPA-Rego or Cedar policies to mitigate specific threat vectors identified by the analysis triad.

## Integration
- **Upstream**: Receives remediation targets from the `Synthesizer` or `Canary` forensic logs.
- **Downstream**: Submits proposed patches and policies to the `Airlock` for human-in-the-loop (HITL) review.
