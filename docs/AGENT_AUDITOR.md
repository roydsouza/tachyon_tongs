# 📝 Auditor Agent: The Compliance Sentinel

## Overview
The **Auditor Agent** is the substrate's primary governance authority. It ensures that all autonomous actions, policy evolutions, and telemetry signals align with established security frameworks (e.g., SOC2, NIST-CSF, MiCA). It transforms raw telemetry into signed, human-readable compliance attestations.

## Role & Responsibilities
- **Compliance Mapping:** Maps SingularityPDP events and GuardianIDS alerts to specific regulatory controls.
- **Attestation Generation:** Produces periodic, cryptographically signed reports detailing the substrate's security posture.
- **ADR Governance:** Verifies that all Architecture Decision Records are intact and follow the Merkle-manifest protocol.
- **Audit Ledgering:** maintains the long-term archival of `RUN_LOG.md` and `EVOLUTION.md` for forensic lookup.

## Operational Mechanics

### Attestation Generation
The Auditor scans the `StateManager` execution logs and maps them to control IDs.
```python
auditor.execute_role_logic("generate_compliance_report", {"framework": "SOC2"})
```

### Control Mapping (Examples)
| Control ID | Substrate Mechanism | Evidence |
|------------|---------------------|----------|
| **CC6.1** | SingularityPDP | ADR-0005, ADR-0010 |
| **CC7.1** | GuardianIDS / TelemetryBus | ADR-0029, ADR-0004 |
| **CC8.1** | Airlock / Engineer Seals | ADR-0013, ADR-0021 |

## Integration
- **Telemetry Bus:** Subscribes to `TOOL_CALL` and `INTEGRITY_CHECK` events.
- **Key Provider:** Uses a derived **Auditor Certificate** signed by the Hybrid Root for report attestation.
- **Airlock:** Feeds compliance summaries to the operator dashboard to highlight "Coverage Gaps."

---
*Signed by: Auditor Agent Genesis Certificate*
