# ADR-0035: The Herald Aggregator Pattern

## Status
Proposed

## Context
The operator currently has to monitor multiple files (`ALERT.md`, `EVOLUTION.md`, `TASKS.md`, `RUN_LOG.md`) and the **Airlock** staging area to understand the substrate's health and identify Human-in-the-Loop (HITL) requirements. 

## Decision
We will designate **The Herald** as the central high-assurance aggregator with a modular plugin architecture:

1.  **Code-Only Implementation**: Deterministic, high-reliability monitoring.
2.  **Modular Collectors**:
    - `FileCollector`: Scans `ALERT.md`, `EVOLUTION.md`, `TASKS.md`.
    - `AirlockCollector`: Queries the `patches` table in `StateManager` for `PENDING` status.
3.  **Modular Dispatchers**:
    - `ConsoleDispatcher`: Powers the `tt herald tail` CLI.
    - `SignalDispatcher`: Existing peer-to-peer messaging.
    - `WebhookDispatcher`: Extensible for Slack, Discord, etc.
4.  **CLI Interface**:
    - `tt herald summary`: On-demand substrate health report.
    - `tt herald tail`: Real-time streaming of new alerts and HITL events.
5.  **Deduplication**: Uses `StateManager` to track `last_relayed_id` per dispatcher.
6.  **Failure Analysis**: Herald will provide structured context for `Agent Failure` events, including "Implications" and "Remediation" hints.

## Consequences
- **Positive**: Single point of failure notification.
- **Positive**: Zero LLM cost/latency for monitoring.
- **Requirement**: Any changes to log formats or locations must be synchronized with the Herald's parser.
