# 🎺 The Herald Agent (Signal Messenger)

**Role**: High-Assurance Notification Proxy
**Identity**: `HeraldRole`

## Overview
The Herald is the substrate's voice to the outside world. It follows the **Asymmetric Trust** principle: while it has network access to reach Signal, it has **zero** capabilities to modify the substrate, ADRs, or policies.

## Operational Mechanics
1. **Trigger**: Consumes `SECURITY_ALERT` events from the `TelemetryBus`.
2. **Action**: Forwards formatted alerts to the operator via Signal.
3. **Control**: Receives signed incoming Signal commands (future phase) and parses them into internal events.

## Configuration
- `TACHYON_SIGNAL_RECIPIENT`: The phone number or group ID to notify.
- `SIGNAL_CLI_PATH`: Path to the `signal-cli` binary.

## Security Boundaries
- **Network**: Only authorized to communicate with Signal servers.
- **Substrate**: Read-only access to `TelemetryBus`; no write access to code or identity blocks.
