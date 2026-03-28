# ADR-0075: Type-Safe TachyonResult Monad for Agentic Actions

## Status
Proposed

## Context
Tachyon Tongs agents previously used inconsistent return patterns (None, Booleans, or raw Dicts) for their `execute_action` methods. This led to `AttributeError` and `TypeError` in the backplane when processing results, and made it difficult for the Auditor agent to quantify security outcomes. We need a standardized, type-safe result container.

## Decision
We will implement a `TachyonResult` monad (Pydantic-based) that encapsulates:
1. **Status**: A `TachyonStatus` enum (SUCCESS, DENIED, ERROR, NOT_IMPLEMENTED).
2. **Payload**: A structured dictionary of result data.
3. **Metadata**: Performance timing and agent identity.
4. **Error Info**: Detailed error messages for non-success states.

All agents MUST return a `TachyonResult` from `execute_action`.

## Consequences
- **Observability**: Improved tracking of security denials vs platform errors.
- **Resilience**: The backplane can now safely handle failures without crashing.
- **Type Safety**: IDEs and linters can now verify result handling.
