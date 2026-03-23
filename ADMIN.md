# Tachyon Tongs: Administrative Oversight & Monitoring

This document provides protocols for monitoring the health and performance of the Tachyon Tongs security substrate.

## 🎺 0. High-Assurance Monitoring (The Herald)

**The Herald** is the primary interface for substrate oversight. Use it to consolidate alerts, evolution events, and Airlock tasks into a single view.

### Real-time Monitoring
To stream live security alerts and substrate mutations:
```bash
# Continuous real-time stream (Deduplicated)
bin/tt_herald tail
```

### Substrate Health Summary
To get an on-demand report of all critical events and pending HITL tasks:
```bash
# Unified report of Alerts + Evolution + Airlock
bin/tt_herald summary
```

### What to check in the Summary:
- **[SECURITY_ALERT]**: Immediate integrity violations or bypasses.
- **[AIRLOCK_PENDING]**: Patches awaiting your review in the Airlock.
- **[HITL_TASK]**: Manual actions required in `TASKS.md`.
- **[Agent Action]**: Structural changes to the substrate.

---

## 1. Monitoring the Immune System (Phase 22)

The Autonomous Immune Response is the substrate's self-healing layer. Monitor its efficacy via the following indicators:

### Evolution Ledger
- **Location**: `memory/strategic/EVOLUTION.md`
- **What to look for**: Check for "MUTATION_SYNTHESIZED" and "PATCH_STAGED" events. Frequent "REJECTED" events in the Airlock indicate the Immune System is over-fitting or hallucinating fixes.

### Fitness Scoring
- **Indicator**: The delta between `CANARY_LOG.md` bypasses and `AIRLOCK` proposals.
- **Target**: 100% neutralization (Blocked) of all previously seen bypass payloads.

### Sandbox Health
- **Location**: `/tmp/tachyon_canary_sandbox`
- **Protocol**: Ensure the sandbox is wiped every 4 hours. If persistent files remain, the Canary may have escaped its isolation.

## 2. Integrity Alerts

If the **Guardian** agent reports a `STATE_COMPROMISED` status:
1.  **Stop the Daemon**: `killall python3` (if running as a daemon).
2.  **Verify Manifest**: `python3 -m tachyon.main --role guardian --action verify_substrate`.
3.  **Audit Logs**: Check `memory/operational/audit.log` for anomalous tool calls.
4.  **Forensic Re-sign**: Only after a manual code audit, run `python3 scripts/forensic_resign.py` to restore the Merkle chain.

## 3. Airlock Backlog

Monitor the Airlock (`/tmp/tachyon_airlock/`) regularly. A growing backlog of unapproved patches indicates a bottleneck in Human-In-The-Loop oversight, potentially leaving the substrate vulnerable to known bypasses.
