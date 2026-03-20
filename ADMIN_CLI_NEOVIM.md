# ⌨️ Event-Horizon Command Bridge: Operator Reference

> The CLI is not tooling — it is the *control surface of the organism*.

This document is the definitive reference for operating the Tachyon Tongs substrate via the **Event-Horizon Command Bridge** — a unified CLI/TUI/NeoVIM interface optimized for **Ghostty** on Apple Silicon.

---

## 1. Quick Start

```bash
# Install the Command Bridge (from the tachyon_tongs root)
pip install -e .

# Verify
tt --version

# Launch the TUI Dashboard
tt dash

# Or use NeoVIM
nvim
:TachyonDash
```

---

## 2. Architecture: Three Tiers of Control

The Command Bridge follows a **NeoVIM-first, CLI-forward** philosophy with three complementary tiers:

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1: CLI (`tt`)                                      │
│  • UNIX-composable commands, scriptable, JSON output     │
│  • Source of truth for all substrate interactions         │
├─────────────────────────────────────────────────────────┤
│  Tier 2: TUI (`tt dash`)                                 │
│  • Real-time situational awareness (Textual framework)   │
│  • Vi-style navigation, live agent/log streaming         │
├─────────────────────────────────────────────────────────┤
│  Tier 3: NeoVIM Plugin (`tachyon.nvim`)                  │
│  • Deep inspection, code-level patch review              │
│  • Telescope integration, Rego LSP, debate syntax        │
└─────────────────────────────────────────────────────────┘
```

---

## 3. CLI Command Reference

### Entry Point

```
tt <command> [subcommand] [flags]
```

### Global Flags

| Flag | Description |
|------|-------------|
| `--config PATH` | Custom config file (default: `~/.config/tt/config.toml`) |
| `--json` | Machine-readable JSON output |
| `--no-color` | Disable color output |
| `-v`, `-vv`, `-vvv` | Verbose logging levels |

### Core Commands

| Command | Description |
|---------|-------------|
| `tt dash` | Launch interactive TUI dashboard |
| `tt status` | Quick substrate health summary |
| `tt health` | Diagnostic health check |

### Agent Management

```bash
tt agent list                    # List all agents with status
tt agent list --running          # Only running agents
tt agent run <name>              # Start an agent
tt agent run sentinel --harvest  # Start with specific mode
tt agent stop <name>             # Graceful shutdown (SIGTERM)
tt agent kill <name>             # Force kill (SIGKILL)
tt agent restart <name>          # Stop + start
tt agent inspect <name>          # Detailed view (TUI)
tt agent tail <name>             # Live log tail
```

### Airlock (Patch Review)

```bash
tt airlock list                  # List pending patches
tt airlock show <id>             # View patch details + debate
tt airlock approve <id>          # Approve (with confirmation)
tt airlock deny <id>             # Deny (prompts for reason)
tt airlock test <id>             # Dry-run in local sandbox
```

### Logs & Observability

```bash
tt logs                          # Interactive log viewer (TUI)
tt logs tail                     # Tail EVOLUTION.md (default)
tt logs tail --source alert      # Tail ALERT.md
tt logs tail --source canary     # Tail CANARY_LOG.md
tt logs tail --source run        # Tail RUN_LOG.md
tt logs search <pattern>         # Search across all logs
tt logs export <file>            # Export filtered logs
```

### Threat Intelligence

```bash
tt catalog                       # Browse catalog (TUI)
tt catalog search <query>        # Search threats
tt catalog show <cve-id>         # Show CVE details
tt catalog export                # Export as JSON/markdown
```

### Substrate Operations

```bash
tt verify                        # Run Guardian substrate audit
tt report                        # Generate health report
tt ritual verify-substrate       # High-assurance pre-flight check
```

---

## 4. TUI Dashboard Layout

The TUI provides five **Active Manifolds** — resizable panels for real-time situational awareness.

```
╔══════════════════════════════════════════════════════════════════════════╗
║ TACHYON SUBSTRATE DASHBOARD                        [Press ? for help]   ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║ ┌─ SUBSTRATE HEALTH ──────────────────────────────────────────────────┐ ║
║ │ Status: 🟢 OPERATIONAL    Uptime: 3d 14h 22m    Mode: HITL          │ ║
║ │ Integrity: ✓ VERIFIED     Last Audit: 2m ago    Merkle: a3f92c...   │ ║
║ └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║ ┌─ ACTIVE AGENTS ──────────────────────────────────────────────────────┐ ║
║ │ 🔵 sentinel      │ Running  │ Last scan: 18s ago  │ Threats: 3/245  │ ║
║ │ 🟢 guardian      │ Running  │ Last audit: 2m ago  │ Status: OK      │ ║
║ │ 🟡 canary        │ Idle     │ Next scout: 4h 12m  │ Intel: 12 logs  │ ║
║ │ ⚫ pathogen      │ Stopped  │ Last run: 6h ago    │ Block: 100%     │ ║
║ │ 🔵 engineer      │ Running  │ Staging: 2 patches  │ Airlock: 2/8    │ ║
║ └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║ ┌─ RECENT ACTIVITY ────────────────────────────────────────────────────┐ ║
║ │ [07:12:34] 🔵 Sentinel cataloged CVE-2026-0042 (Critical)           │ ║
║ │ [07:10:15] 🟢 Guardian verified substrate integrity                 │ ║
║ │ [07:08:22] 🟡 Engineer staged patch for CVE-2026-0042               │ ║
║ │ [06:55:10] 🟢 Airlock: patch-a3f92c approved by operator            │ ║
║ └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║ ┌─ AIRLOCK QUEUE ──────────────────────────────────────────────────────┐ ║
║ │ 🟡 patch-b4e3a1  │ CVE-2026-0042 │ +42/-3 lines │ Debate: Complete  │ ║
║ │ 🟡 patch-c7d982  │ CVE-2026-0043 │ +18/-8 lines │ Debate: In prog.  │ ║
║ └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║ [r]efresh [a]gents [l]ogs [i]nspect [:]cmd [q]uit                       ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### TUI Keybindings (Vi-Style)

| Key | Context | Action |
|-----|---------|--------|
| `j` / `k` | Global | Navigate up/down |
| `Ctrl+d` / `Ctrl+u` | Global | Page down/up |
| `r` | Dashboard | Force refresh |
| `a` | Dashboard | Jump to agents panel |
| `l` | Dashboard | Jump to logs panel |
| `i` | Dashboard | Inspect selected item |
| `:` | Global | Command palette |
| `q` | Global | Quit (with confirmation) |
| `?` | Global | Help overlay |
| `/` | Logs | Open filter prompt (regex) |
| `f` | Logs | Toggle follow mode |
| `p` | Logs | Pause/resume streaming |
| `1`–`8` | Logs | Quick filter presets |
| `a` | Airlock | Approve patch |
| `d` | Airlock | Deny patch |
| `v` | Airlock | View full diff in NeoVIM |
| `b` | Airlock | View debate transcript |
| `t` | Airlock | Test patch locally |
| `n` / `p` | Airlock | Next/previous patch |
| `Tab` | Agents | Cycle through agents |
| `s` | Agents | Stop agent |
| `e` | Agents | Edit config in NeoVIM |

---

## 5. NeoVIM Plugin: `tachyon.nvim`

### Installation (lazy.nvim)

```lua
{
  'roydsouza/tachyon.nvim',
  dependencies = {
    'nvim-lua/plenary.nvim',
    'nvim-telescope/telescope.nvim',
    'neovim/nvim-lspconfig',
  },
  config = function()
    require('tachyon').setup({
      substrate_url = 'http://localhost:60461',
      auto_refresh = true,
      refresh_interval = 2000,
      keybindings = {
        dashboard  = '<leader>td',
        agents     = '<leader>ta',
        airlock    = '<leader>tl',
        logs       = '<leader>to',
        catalog    = '<leader>tc',
        status     = '<leader>ts',
      },
    })
  end,
}
```

### Commands

| Command | Description |
|---------|-------------|
| `:TachyonDash` | Open floating dashboard |
| `:TachyonAgents` | Agent management panel |
| `:TachyonAirlock` | Airlock patch review (3-way split: debate \| diff \| controls) |
| `:TachyonLogs` | Live log viewer buffer |
| `:TachyonCatalog` | Browse exploitation catalog |
| `:TachyonStatus` | Quick status in statusline |
| `:TachyonRun <agent>` | Run a specific agent |
| `:TachyonKill <agent>` | Stop a specific agent |
| `:Telescope tachyon agents` | Fuzzy-find agents |
| `:Telescope tachyon debates` | Fuzzy-find debate transcripts |
| `:Telescope tachyon catalog` | Fuzzy-find threat catalog |

### Keybinding Reference

| Key | Command | Description |
|-----|---------|-------------|
| `<leader>td` | `:TachyonDash` | Open dashboard |
| `<leader>ta` | `:TachyonAgents` | Agent manager |
| `<leader>tl` | `:TachyonAirlock` | Airlock review |
| `<leader>to` | `:TachyonLogs` | Log viewer |
| `<leader>tc` | `:TachyonCatalog` | Threat catalog |
| `<leader>ts` | `:TachyonStatus` | Quick status |
| `<leader>tr` | `:TachyonRun` | Run agent (prompts) |
| `<leader>tk` | `:TachyonKill` | Stop agent (prompts) |
| `<leader>aa` | (Airlock buf) | Approve patch |
| `<leader>ad` | (Airlock buf) | Deny patch |

### Custom File Types

The plugin auto-detects Tachyon-specific files:
- `*/debates/*.md` → `debate` filetype (custom syntax highlighting)
- `*/agents/*/SKILL.md` → `skillmd` filetype
- `*.sig` → `signature` filetype
- `*.rego` → `rego` filetype (with Rego LSP integration)

---

## 6. Ghostty Configuration

```conf
# ~/.config/ghostty/config — Tachyon Tongs Profile

# Performance
gpu-renderer = true
repaint-delay = 0
vsync = true

# Font (use a Nerd Font for icons)
font-family = "JetBrainsMono Nerd Font"
font-size = 12

# Tachyon Substrate Color Palette
background = 0a0e14
foreground = e6e6e6
palette = 0=1a1a2e     # Black (backgrounds)
palette = 1=f07178     # Red (alerts, denials)
palette = 2=c3e88d     # Green (success, approvals)
palette = 3=ffcb6b     # Yellow (warnings, pending)
palette = 4=82aaff     # Blue (info, agent activity)
palette = 5=c792ea     # Magenta (debates, reasoning)
palette = 6=89ddff     # Cyan (highlights)
palette = 7=d6deeb     # White (text)

# Quick Access Keybindings
keybind = ctrl+shift+t=new_tab:tt dash
keybind = ctrl+shift+a=new_tab:tt airlock list
keybind = ctrl+shift+l=new_tab:tt logs tail
```

### Recommended Layout

```
┌──────────────────────────────────────┬────────────────────────┐
│                                      │  tt logs tail          │
│  NeoVIM (editing)                    │  (live streaming)      │
│                                      ├────────────────────────┤
│                                      │  tt dash               │
│                                      │  (substrate health)    │
└──────────────────────────────────────┴────────────────────────┘
```

---

## 7. Operator Workflows

### Workflow 1: Morning Substrate Check

```bash
# 1. Launch dashboard in Ghostty
tt dash

# 2. Quick visual scan:
#    - All agents running? ✓
#    - Integrity verified? ✓
#    - Airlock queue? 2 patches pending

# 3. Review patches in NeoVIM
nvim → :TachyonAirlock
# Approve/deny patches → :wq

# 4. Return to dashboard, verify patches applied
```

### Workflow 2: Zero-Day Response

```bash
# 1. Notification: "🔴 CRITICAL threat cataloged"
tt catalog show CVE-2026-9999

# 2. Verify Engineer staged a patch
tt airlock list

# 3. Review full debate transcript
tt airlock show patch-xyz789

# 4. Test locally before deploying
tt airlock test patch-xyz789

# 5. Approve
tt airlock approve patch-xyz789

# 6. Run Pathogen stress test
tt agent run pathogen --mutate CVE-2026-9999
```

### Workflow 3: Investigating an Alert

```bash
# 1. Dashboard shows red alert
tt dash → press 'l' for logs

# 2. Filter for errors
# Press '2' (Errors Only filter)

# 3. Deep investigation in NeoVIM
nvim → :TachyonLogs → /STATE_COMPROMISED

# 4. Resolution
:terminal tt verify
# Status: 🟢 OPERATIONAL
```

---

## 8. Configuration File

```toml
# ~/.config/tt/config.toml

[substrate]
url = "http://localhost:60461"
timeout = 30
retry_attempts = 3

[dashboard]
auto_refresh = true
refresh_interval = 2000  # ms
show_memory = true
show_cpu = true

[airlock]
auto_test_patches = true
require_confirmation = true
default_editor = "nvim"

[logs]
default_source = "evolution"
follow_mode = true
max_lines = 1000
syntax_highlight = true

[ui]
theme = "dark"
use_nerd_fonts = true
animations = true
vim_bindings = true

[notifications]
desktop_alerts = true
alert_on_patch = true
alert_on_integrity_failure = true

[neovim]
plugin_enabled = true
auto_open_dashboard = false
keybinding_prefix = "<leader>t"
```

---

## 9. Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| CLI Framework | Typer | Industry standard, composable, auto-help |
| TUI Framework | Textual | Async-native, rich widgets, Ghostty-optimized |
| API Client | httpx | Async HTTP/2, connection pooling |
| NeoVIM Plugin | Pure Lua | No rebuild, fast, native RPC/LSP |
| NeoVIM Deps | plenary.nvim, telescope.nvim | HTTP client, fuzzy finding |
| Real-time | WebSocket + SSE | Low-latency log/agent streaming |
| Config | TOML | Human-readable, standard |

---

## 10. Security Considerations

- **Read-only by default**: CLI commands are read-only unless explicitly mutating.
- **Confirmation gates**: All Airlock approvals require interactive confirmation.
- **Audit trail**: Every CLI command is logged to `CHANGE_CONTROL.md`.
- **Network isolation**: CLI connects only to `localhost` by default.
- **Substrate gating**: All `tt run` commands pass through the `ToolRouter` + Singularity Meta-PDP.
