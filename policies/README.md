# 🛡️ Tachyon Tongs: Policy Governance

This directory contains the multi-engine policy definitions for the security substrate.

## Structure

- **`shared/`**: Common data assets (e.g., `denylists.json`) shared across engines.
- **`rego/`**: [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) Rego policies.
  - `manual/`: Human-authored governance rules (e.g., `governance.rego`).
  - `autonomous/`: Sentinel-generated threat mitigations and dynamic blocks.
- **`cedar/`**: [AWS Cedar](https://www.cedarpolicy.com/) policies for fine-grained authorization.
  - `manual/`: User-defined permissions.
  - `autonomous/`: AI-generated policy updates.

## Update Policy
- **Manual**: Edits to files in `manual/` take precedence and are strictly governed by the Operator.
- **Autonomous**: Agents (Sentinel, Engineer) append to files in `autonomous/` following the AC/DC cycle.
