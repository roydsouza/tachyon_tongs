# 🛡️ Agent: Guardian (The Substrate Sentry)

## Overview
The Guardian Agent is the internal security auditor of the Tachyon Tongs substrate. Its primary mission is to ensure the integrity of the substrate code and configuration through Merkle-tree verification and syscall compliance monitoring.

## Operational Mechanics

### 1. Triggers
The Guardian is typically triggered by:
- **Integrity Checkpoints**: Periodic or post-execution audits to verify no unauthorized changes were made to the core substrate.
- **PEP Enforcement**: When the `ToolRouter` detects a potential policy violation, it can trigger a Guardian audit.
- **Post-Consolidation Verification**: Ensuring directory structures match the signed ADR manifest.

### 2. Configuration
The Guardian operates in the `tachyon/agents/guardian/` directory:
- **IDS Engine**: Delegates to `GuardianIDS` for deep file-system and configuration audits.
- **Merkle Roots**: Maintains the "Ground Truth" hashes for all substrate components.

### 3. Capabilities
- `verify_substrate()`: Performs a full hybrid-signature audit (Merkle + HMAC) across all protected paths.
- **Access Control Monitoring**: Validates that agentic tool-use adheres to the established capability-based security model.

## Integration
- **Upstream**: Orchestrates audits based on `ToolRouter` alerts or substrate state transitions.
- **Downstream**: Reports integrity violations to the `StateManager` and `RUN_LOG.md`, potentially triggering a lockdown or revert.
