# Sentinel Agent Skill

## Metadata
- **Agent ID:** Sentinel
- **Type:** Monitoring / Enforcement
- **Version:** 1.0.0
- **Description:** Autonomous web-born threat analyzer and enforcement supervisor.

## Capabilities
- `safe_fetch`: Sanitized web crawling with Guardian Triad oversight.
- `safe_execute`: Isolated shell command execution via Apple Tier-0 Sandbox.
- `threat_analysis`: LLM-based semantic threat detection.

## Intent Mapping
- **RESEARCH:** `["arxiv.org", "nvd.nist.gov", "github.com", "owasp.org", "huntr.ml", "lmsys.org"]`
- **SECURITY:** `["cisa.gov", "cert.org", "mitre.org"]`
- **DEFAULT:** `[]`

## Behavioral Constraints
- **Max Reasoning Steps:** 5
- **Syscall Drift Threshold:** 3.0
- **Sanitization Level:** High (Deep verification enabled)

## Safety Policies
- OPA-driven domain whitelisting.
- Prophylactic pipeline for all external web content.
- Cryptographically signed exploitation catalog.
