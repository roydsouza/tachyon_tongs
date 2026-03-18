# ADR-0011: Immutable Actions & TOCTOU-Resistant Routing

## Status
Proposed

## Context
In the previous `ToolRouter` implementation, tool parameters were passed as mutable dictionaries. This created a Time-of-Check to Time-of-Use (TOCTOU) vulnerability window: an agent could potentially mutate the parameters between the time the `PolicyEngine` approved the action and the time the `AppleSandbox` executed it. 

To achieve high-assurance, we must guarantee that the action being executed is identical to the one that was authorized.

## Decision
We will refactor the enforcement pipeline to use `ImmutableToolRequest` (a frozen Python dataclass) starting from the point of policy evaluation.

1. **Frozen Dataclasses**: Tool requests are encapsulated in `ImmutableToolRequest` which prevents attribute modification after instantiation.
2. **Early Freezing**: The `ToolRouter` creates the immutable request BEFORE calling `pdp.is_action_allowed`.
3. **Execution Integrity**: The `execute` phase of the router uses the frozen request object exclusively.

## Consequences
- **Security**: Neutralizes parameter-mutation TOCTOU attacks.
- **Performance**: Negligible overhead for dataclass instantiation.
- **Developer UX**: Developers must now interact with the `ImmutableToolRequest` object rather than raw dicts at the execution layer.
- **Modularity**: Clearly separates the "Intent" from the "Execution" state.
