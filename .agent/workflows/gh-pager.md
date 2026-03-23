---
description: Ensure PAGER and MANPAGER are set to 'cat' before executing GitHub or Git commands.
---

# 📖 GitHub/Git Environment Protocol

To prevent interactive hangs, truncated output, or context loss during automated agent runs, all `gh` and `git` commands MUST be executed with `PAGER` and `MANPAGER` set to `cat`.

## 🛠️ Execution Standard

When running a command that may trigger a pager (e.g., `git log`, `git diff`, `gh pr list`, `gh issue view`), prefix the command with the environment overrides:

```bash
PAGER=cat MANPAGER=cat [command]
```

### Examples:

- **Git Status**: `PAGER=cat MANPAGER=cat git status`
- **GitHub PR List**: `PAGER=cat MANPAGER=cat gh pr list`
- **Git Log**: `PAGER=cat MANPAGER=cat git log -n 5`

---
> [!TIP]
> This protocol ensures that the AI agent receives the full text output in a single stream, allowing for accurate parsing and decision-making.
