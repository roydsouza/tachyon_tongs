# Question:

I am interested in a design for a clean CLI that I can use to monitor
and manage Tachyon Tongs, to run agents, to view their progress and outputs,
using Ghostty and perhaps adding close NeoVIM integration
(perhaps optionally through a new plug-in - do I need to build a new
NeoVIM that supports Python?). Could you please give me a detailed
markdown file I could use with AntiGravity for this design and implementation?

# Grok:

**Tachyon Tongs CLI Design & Implementation Plan**  
**File**: `docs/CLI_DESIGN.md` (ready to drop into your AntiGravity workspace)

```markdown
# Tachyon Tongs CLI (tt-cli) – Unified Terminal Interface

> **Status**: Proposed → Phase 24 (Post-Phase 22 Immune System)  
> **Owner**: Roy D’Souza (Human-In-The-Loop approval required via Airlock)  
> **Target Terminal**: Ghostty (primary) + optional NeoVim deep integration  
> **Core Tech**: Textual (already in `pyproject.toml`) + Typer/Click hybrid + pynvim

## 1. Vision & Motivation

Tachyon Tongs already has:
- `airlock_cli.py` (list/approve/deny)
- `airlock_tui.py` (early Textual prototype)
- `CHEATSHEET.md` + slash commands in the agent layer
- `memory/strategic/*` logs, `EVOLUTION.md`, `RUN_LOG.md`, `ALERT.md`

We need **one clean, discoverable, fast interface** that:
- Runs any agent (`sentinel`, `canary`, `engineer`, `pathogen`, `guardian`)
- Shows live progress, logs, Airlock queue, substrate health
- Works beautifully in **Ghostty** (GPU-accelerated, ligatures, truecolor, kitty graphics)
- Optionally lives **inside NeoVim** (no new NeoVim build required)

## 2. Architecture Overview

```
tt-cli (entrypoint: tachyon/cli/main.py)
├── CLI mode (Typer)          → fast commands, scripting
├── TUI mode (Textual)        → dashboard, live tailing, interactive Airlock
├── NeoVim plugin (optional)  → :Tachyon or <leader>tt
└── Shared core
    ├── tachyon/core/state_manager.py (already exists)
    ├── tachyon/monitoring/execution_logger.py
    ├── scripts/airlock_cli.py (refactored into library)
```

**Single binary** installed via `pip install -e .` → `tt` command.

## 3. Ghostty-Specific Optimisations

Ghostty is the perfect host because:
- Native Metal rendering → zero lag on Textual animations
- Ligature + Nerd Font support out of the box
- Kitty graphics protocol → we can render live Mermaid diagrams or sandbox diagrams
- Config snippet you can add to `~/.config/ghostty/config`:

```conf
font-family = "JetBrainsMono NF"
font-size = 13
theme = "One Half Dark"
cursor-style = block
background-opacity = 0.95
keybind = ctrl+shift+t=toggle_tab_bar
```

## 4. NeoVim Integration (No Custom Build Needed)

**Standard NeoVim** (brew install neovim or nightly) already ships with Python 3 support.

**Two integration paths** (choose one or both):

**A. Simple terminal integration (zero code)**
```vim
" ~/.config/nvim/after/ftplugin/markdown.vim or in your init.lua
nnoremap <leader>tt :terminal tt dashboard<CR>
nnoremap <leader>ts :terminal tt sentinel<CR>
```

**B. Full pynvim plugin (recommended for Phase 24.5)**  
Create `~/.local/share/nvim/site/pack/plugins/start/tachyon-nvim/plugin/tachyon.vim` + Python glue.

The plugin will:
- `:Tachyon dashboard` → opens floating Textual window (via `nvim` + `termopen` + `pynvim`)
- `:Tachyon airlock` → opens Airlock TUI
- Live log tailing in a split (using `ExecutionLogger` events)
- `:Tachyon run sentinel --harvest` from inside any buffer

**No new NeoVim build** required — just `pip install pynvim` in your nvim Python venv.

## 5. Command Reference (CLI Mode)

```bash
tt --help
tt dashboard                  # live TUI (default in Ghostty)
tt run <role> [--action X]    # sentinel, canary, engineer, pathogen, guardian
tt airlock list|inspect|approve|deny
tt logs [evolution|run|alert|canary]
tt report                     # substrate health + Phase 22 immune stats
tt verify                     # guardian verify_substrate
tt sentinel --harvest         # one-shot intelligence sweep
tt pathogen --mutate CVE-TEST-999
```

All commands respect the same `TACHYON_DB_PATH`, `TACHYON_STRICT_MODE`, and Airlock gating.

## 6. TUI Dashboard Layout (Textual)

Four resizable panes (Ghostty + Textual shines here):

```
┌──────────────────────────────────────────────────────────────┐
│ Tachyon Tongs v1.4.2 – AIRLOCK ACTIVE │ Ghostty │ 127.0.0.1:3030 │
├───────────────┬──────────────────────────────────────────────┤
│ Live Agents   │  Logs (scrollable, searchable, color-coded)       │
│ • Sentinel    │  11:44:45 [STATE_COMPROMISED] …                  │
│ • Canary      │  11:44:45 [CONCURRENCY_TEST] …                   │
│ • Engineer    │  ─────────────────────────────────────────────── │
│ • Pathogen    │  EVOLUTION.md tail (last 20 entries)             │
├───────────────┼──────────────────────────────────────────────┤
│ Airlock Queue │  Substrate Health                                │
│ (3 pending)   │  • Integrity: SECURE                             │
│ CVE-TEST-999  │  • Immune Fitness: 100%                          │
│               │  • Sandbox: /tmp/tachyon_canary_sandbox          │
└───────────────┴──────────────────────────────────────────────┘
```

Keyboard shortcuts (Ghostty-friendly):
- `Ctrl+S` → Sentinel sweep
- `Ctrl+A` → Airlock focus
- `Ctrl+L` → Toggle logs
- `Ctrl+R` → Run selected agent
- `?` → help overlay

## 7. Implementation Roadmap (High-Assurance AC/DC style)

### Phase 24.0 – Core CLI Skeleton
- [ ] Create `tachyon/cli/__init__.py` + `main.py` (Typer)
- [ ] Refactor `scripts/airlock_cli.py` → `tachyon/cli/airlock.py` library
- [ ] Add `tt` console script in `pyproject.toml`

### Phase 24.1 – Textual Dashboard
- [ ] `tachyon/cli/tui/dashboard.py` (reuse existing `airlock_tui.py` widgets)
- [ ] Live widgets using `StateManager` + `ExecutionLogger` events
- [ ] Ghostty kitty graphics for mini Mermaid threat graph

### Phase 24.2 – NeoVim Plugin (optional but high-value)
- [ ] `tachyon-nvim/` directory with `plugin/tachyon.vim` + Python handler
- [ ] `:Tachyon` command family
- [ ] Log tailing buffer synced with `RUN_LOG.md`

### Phase 24.3 – Polish & Testing
- [ ] Add to `CHEATSHEET.md` and `ADMIN.md`
- [ ] New regression suite `tests/test_cli_tui.py`
- [ ] ADR-0023: Unified CLI & Terminal Integration
- [ ] Sign everything and push via `/push`

## 8. Dependencies (already satisfied or trivial)

- `textual` (already in pyproject.toml)
- `typer` or `click` (add to requirements.txt if needed)
- `pynvim` (only for NeoVim plugin)
- `rich` / `pygments` (for log highlighting)

## 9. Security & Airlock Gating

- Every `tt run` command goes through the existing `ToolRouter` + Singularity Meta-PDP.
- Airlock TUI **cannot** approve patches without Guardian signature verification.
- All CLI actions are logged to `memory/strategic/CHANGE_CONTROL.md`.

## 10. Next Steps (for you in AntiGravity)

1. Create this file: `docs/CLI_DESIGN.md` (copy-paste above)
2. Run the high-assurance ritual:
   ```bash
   tt run guardian --action verify_substrate
   ```
3. Create ADR-0023 from the template in `.agent/workflows/adr.md`
4. Start implementation with:
   ```bash
   python -m tachyon.cli --mode tui
   ```
   (stub that will become the dashboard)

Would you like me to also generate:
- The starter `tachyon/cli/main.py` skeleton?
- The NeoVim plugin boilerplate?
- Updated `CHEATSHEET.md` section?

Just say the word and we’ll push it through the Airlock together.
``` 

**Ready to save as `docs/CLI_DESIGN.md`** in your Tachyon Tongs root.  
Drop it into AntiGravity, run the Guardian verify, and we can start coding the TUI immediately.  

Let me know if you want the starter code files generated next!

