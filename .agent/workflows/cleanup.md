---
description: Perform a safe substrate cleanup (Sync to GitHub then Clear Artifacts)
---

# 🧼 Substrate Cleanup Workflow (/cleanup)

This workflow ensures your work is backed up to GitHub before purging local test artifacts and temporary files.

### Steps:

1. **Safety Sync**: Runs `git push` for all outstanding changes.
2. **Purge Root**: Removes stale `test_*.db*`, `*.log`, and other root clutter.
3. **Clear Tmp**: Empties the `tmp/` directory.

### Commands:

// turbo
1. Run the safe cleanup script:
```bash
python3 scripts/safe_cleanup.py
```

---
*Status: [OPERATIONAL]*
