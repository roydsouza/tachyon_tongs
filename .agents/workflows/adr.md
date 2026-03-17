---
description: Create a new Architecture Decision Record (ADR)
---
# Workflow: Create Architecture Decision Record (/adr)

// turbo-all
1. **Analyze Context**: Identify the architectural decision being made and its background.
2. **Determine Sequence**: Run `ls docs/adr/` to find the next sequential number (e.g., `0004`).
3. **Generate ADR**: Create a file `docs/adr/[NUMBER]-[SLUG].md` using the following template:

```markdown
# ADR-[NUMBER]: [Title]

## Status
Proposed / Accepted / Superseded

## Context
[Describe the problem and background]

## Decision
[Describe the chosen path]

## Consequences
- **Positive**: [Benefit]
- **Negative**: [Trade-off]
```

4. **Update Logs**: Update `TASKS.md` or `memory/evolution.md` to reflect the decision.
5. **Notify**: Inform the user about the new ADR via `notify_user`.
