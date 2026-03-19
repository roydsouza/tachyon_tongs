# ADR-0021: Immutable Actions & TOCTOU Hardening

## Status
Proposed -> **Accepted** (2026-03-19)

## Context
The `ImmutableToolRequest` was designed to prevent Time-of-Check to Time-of-Use (TOCTOU) vulnerabilities by freezing tool parameters before policy evaluation. However, the initial implementation used a mutable Python `dict` for `params`, allowing downstream logic or malicious agents to modify the request after it was allegedly frozen.

## Decision
We will enforce deep immutability for the `params` field.
1.  **Recursive Freeze**: Implement a `recursive_freeze` helper that converts dictionaries to `types.MappingProxyType` and lists to `tuple`.
2.  **Post-Init Enforcement**: Use `object.__setattr__` in the frozen dataclass's `__post_init__` to overwrite the mutable input with its frozen counterpart.

## Consequences
- **Security**: Parameters are now guaranteed to be identical between the policy check and the actual tool execution.
- **Performance**: Negligible overhead for small parameter sets; prevents accidental state corruption.
- **Developer Experience**: Developers must treat `request.params` as read-only.
