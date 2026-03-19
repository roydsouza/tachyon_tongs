# ADR-0016: Aggregate Security Hardening & Substrate Rationalization

- **Status**: Accepted
- **Date**: 2026-03-18
- **Author**: AntiGravity Agent
- **Tags**: #security #integrity #sanitization #cleanup

## Context

Following a comprehensive feedback cycle from Grok, OpenAI, and Claude (03-18), several critical security vulnerabilities and architectural inefficiencies were identified in the Tachyon Tongs substrate. These included a state integrity data-corruption loop, a lack of input sanitization, potential TOCTOU race conditions in state mutations, and significant directory/documentation debt.

## Decision

We have implemented a multi-layered security and operational sweep:

1.  **Durable State Integrity**: Integrated `f.flush()` and `os.fsync()` into the `StateManager` to ensure Markdown exports of the exploitation catalog are physically written to disk before cryptographic signing.
2.  **Atomic State Access**: Implemented mandatory file-level locking (`fcntl.LOCK_EX`) for the `EXPLOITATION_CATALOG.md` to prevent TOCTOU bypasses during high-concurrency agent execution.
3.  **Input Sanitization Layer**: Deployed a new `InputSanitizer` (NFKC normalization + regex scrubbing) as a mandatory gate for all external data ingress.
4.  **Substrate Rationalization**: Consolidated redundant `_agent` and `_agents` directories into a single canonical `.agent/` source and established a structured `docs/INDEX.md` map.

## Consequences

- **Pros**: Elimination of false-positive `STATE_COMPROMISED` alerts, hardened resistance to prompt injection, guaranteed atomicity for forensic records, and significantly improved documentation navigability.
- **Cons**: Minor overhead in file I/O due to sync/locking.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0016",
  "hash": "sha256:ee55bb07ffa23293250cfadf2da1eceff516333fbb1e53580257d97ed5591b8a",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
