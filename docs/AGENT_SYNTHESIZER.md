# 🧬 Agent: Synthesizer (The Policy Architect)

## Overview
The Synthesizer Agent is the intellectual core of the Tachyon Tongs defense-in-depth model. Its primary mission is to autonomously translate analyzed vulnerabilities (from the `Sentinel`) into executable security policies (OPA-Rego or Cedar).

## Operational Mechanics

### 1. Triggers
The Synthesizer is typically triggered by:
- **New Vulnerability Harvest**: When the `Sentinel` catalogs a new CVE, the Synthesizer is invoked to draft a preventative policy.
- **Canary Discovery**: When the `Canary` identifies a bypass, the Synthesizer generates a more restrictive rule to close the gap.
- **Policy Refresh**: Periodic re-evaluation of current policies against evolving threat intel.

### 2. Configuration
The Synthesizer operates in the `tachyon/agents/synthesizer/` directory:
- **Language Engines**: Specialized sub-agents for different target platforms:
  - `rego_synth.py`: For OPA-based enforcement.
  - `cedar_synth.py`: For AWS Cedar-based authorization.
- **Template Library**: Maintains a set of high-assurance policy patterns for common threat vectors.

### 3. Capabilities
- `synthesize_policy(vulnerability_data, target_format)`: Generates a signed, syntactically correct policy based on NVD descriptions and payload analysis.
- **Validation Loop**: Verifies the synthesized policy's logic before passing it to the `Engineer` for staging.

## Integration
- **Upstream**: Receives structured vulnerability data from the `Sentinel`.
- **Downstream**: Passes synthesized policies to the `Engineer` for deployment and the `Airlock` for human review.
