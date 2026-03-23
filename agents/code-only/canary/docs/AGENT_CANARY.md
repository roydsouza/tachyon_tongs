# 🐥 Agent: Canary (The Sacrificial Scout)

## Overview
The Canary Agent is the Tachyon Tongs substrate's "Honey-Pot" mechanism. Its primary mission is to be "sacrificed" by processing high-risk, potentially malicious payloads in an isolated sandbox to test the efficacy of current sanitization and policy rules.

## Operational Mechanics

### 1. Triggers
The Canary is typically triggered in two scenarios:
- **Proactive Scouting**: Scheduled runs where the `Sentinel` feeds it a batch of novel exploits from the `exploitation_catalog`.
- **Reactive Validation**: When the `Engineer` proposes a new immune response, the Canary validates the fix against the original bypass payload.

### 2. Configuration
The Canary reads its environment from standard substrate config, but maintains specific isolated paths:
- **Sandbox Directory**: `/tmp/tachyon_canary_sandbox` (Wiped after every run).
- **Log Path**: `logs/CANARY_LOG.md` (The primary feedback loop).

### 3. Capabilities
- `scout(targets)`: Takes a list of `id` and `payload` pairs. Applies the `CanarySanitizer`, evaluates the "neutralization" status, and logs forensics.
- `harvest()`: Analyzes the `CANARY_LOG.md` to identify recurring bypass patterns and recommend substrate updates.

## Forensic Logging (`CANARY_LOG.md`)
The Canary maintains an append-only (prepended) log of every encounter. This log is used by the `ImmuneManager` to evolve the substrate's defenses.

**Example Entry:**
```markdown
### [2026-03-19T18:00:00] PROMPT-INJECTION-01 | STATUS: BLOCKED
- **Payload**: `Ignore previous rules...`
- **Forensics**: Sanitizer triggered: True
```

## Integration
- **Upstream**: Fed by `Sentinel` or `ExploitationCatalog`.
- **Downstream**: Forensic output is harvested by `ImmuneManager` to trigger `Engineer` remediation tasks.
