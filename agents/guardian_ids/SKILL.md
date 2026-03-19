# Skill: Guardian IDS Verification Protocol

> [!IMPORTANT]
> **Forensic Audit Trigger**: Use this skill to initiate a full-substrate integrity check when a security anomaly is suspected or as part of a routine high-assurance audit.

## Purpose
The **Guardian IDS** verifies the integrity of the Tachyon Tongs architectural substrate by cross-referencing embedded signatures, external sidecars, and the cumulative Merkle Root.

## Protocol: `/verify-signatures`

To initiate a forensic audit, run the following command:

```bash
python3 tachyon/agents/guardian_ids.py
```

### Response Interpretation

| Status | Interpretation | Required Action |
| :--- | :--- | :--- |
| **SECURE** | Substrate integrity is verified across all layers. | None. Continue operations. |
| **WARNING** | Minor issues detected (e.g., missing .sig sidecar). | Regenerate signatures via the push workflow. |
| **CRITICAL** | Integrity violation in a specific file. | Halt substrate immediately. Perform forensic diff. |
| **COMPROMISED** | Merkle Root mismatch detected. | Repository supply chain may be compromised. Restore from OOB backup. |

## Administrative Gating
This skill is reserved for the **Administrator** persona. Agents may trigger a read-only audit but cannot modify the MANIFEST or signatures.
