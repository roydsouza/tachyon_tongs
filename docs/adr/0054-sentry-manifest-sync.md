# ADR-0054: Sentry Agent Manifest Synchronization

## Status
Accepted

## Context
Following the agent consolidation (ADR-0036), the `SentryPlugin` was established as the primary honeypot warden and deception tripwire, absorbing the roles of various legacy "Canary" agents. However, the `agents/sentry/config.yaml` manifest was not correctly updated to reflect this new identity. It continued to use `agent_id: canary` and referenced the non-existent `agents.canary.agent:CanaryPlugin` entry point. This caused logical drift in the `AgentRegistry` and would lead to failures in any automated orchestration that relied on declarative manifest truth.

## Decision
1. Synchronize `agents/sentry/config.yaml` with the agent's post-consolidation reality.
2. Update `agent_id` to `sentry-001`.
3. Update `name` to `Sentry`.
4. Update `entry_point` to `agents.sentry.agent:SentryPlugin`.
5. Update `capabilities` to include `check_signals`.

## Consequences
- **Positive**: Restores declarative integrity to the Sentry agent's manifest.
- **Positive**: Enables correct agent discovery and capability mapping by the `AgentRegistry`.
- **Positive**: Eliminates confusing legacy nomenclature from the configuration layer.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0054",
  "hash": "sha256:8d56f8486e0b81df1b957390d592544e98984fee2bcb74db83257d0ce9c19616",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
