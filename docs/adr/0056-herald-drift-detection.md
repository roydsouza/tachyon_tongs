# ADR-0056: Herald Log Collector Drift Detection

## Status
Accepted

## Context
The Herald agent's `FileLogCollector` uses regular expressions to extract structured security events from markdown logs like `ALERT.md`. During the Get-Well audit (Priority 3), we identified a critical observability risk: if the formatting of `ALERT.md` drifts (e.g., due to a change in another agent's reporting logic) such that the regex no longer matches, the collector silently returns an empty list. 
For an operator, an empty relay run is indistinguishable from a "perfectly secure" system state. This "False Silence" is a major security blindspot, as it hides active threats behind a broken parser.

## Decision
1. Implement a diagnostic check in `FileLogCollector.collect()`.
2. If the target file exists and is significantly non-empty (currently >100 bytes) but the parser returns zero events, emit a high-signal warning to the console.
3. Include the failed regex pattern in the warning to facilitate rapid forensic debugging of the parser drift.

## Consequences
- **Positive**: Eliminates the "False Silence" blindspot by distinguishing between "no events" and "no matches".
- **Positive**: Enables faster recovery from breaking changes in log formatting.
- **Negative**: May occasionally trigger false-positive warnings if a log file contains only non-event boilerplate (addressed by the 100-byte threshold).


## Integrity Attestation

```json
{
  "adr_id": "ADR-0056",
  "hash": "sha256:f7d915324c94aded713311ae264c11ad53e9aec0279f3f3bc1552bfb19b871a0",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
