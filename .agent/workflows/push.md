---
description: Update SYNC_LOG.md and push all changes to GitHub.
---

# /push Workflow (The Checkpoint Ritual)

Follow these steps to safely synchronize the mission state:

1. **Update SYNC_LOG.md**: Ensure a new entry is added to `~/antigravity/tachyon_tongs/SYNC_LOG.md` summarizing the session's achievements and decisions.
2. **Commit Changes**: Use the `run_command` tool to stage and commit all changes.
// turbo
3. **Execute Push**: Push the committed changes to the remote repository.
```bash
git add .
git commit -m "Checkpoint: [Brief Summary of Work]"
git push origin main
```
4. **Verify Sync**: Ensure the remote repository reflects the local state.
