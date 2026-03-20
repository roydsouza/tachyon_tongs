# Question:

I am interested in a design for a clean CLI that I can use to monitor
and manage Tachyon Tongs, to run agents, to view their progress and outputs,
using Ghostty and perhaps adding close NeoVIM integration
(perhaps optionally through a new plug-in - do I need to build a new
NeoVIM that supports Python?). Could you please give me a detailed
markdown file I could use with AntiGravity for this design and implementation?

# Claude:

I'll create a comprehensive design document for a clean CLI interface for Tachyon Tongs with Ghostty and NeoVIM integration.I've created a comprehensive design specification for your Tachyon Tongs CLI! Here's what's included:

## 📋 Document Highlights:

### **Design Philosophy**
- Clean, GPU-accelerated interface optimized for Ghostty terminal
- Security operations center aesthetic with semantic color coding
- Vi-style keybindings throughout for ergonomic control

### **Five Main Views with ASCII Mockups:**
1. **Dashboard** - Real-time substrate health, agent status, activity feed
2. **Agent Management** - Start/stop/monitor agents with live logs
3. **Airlock Management** - Review and approve patches with diff visualization
4. **Log Streaming** - Real-time tail with filtering and syntax highlighting
5. **Threat Catalog** - Browse and search the exploitation catalog

### **NeoVIM Integration (No Rebuild Needed!)**
✅ **Answer to your question**: No, you don't need to rebuild NeoVIM with Python support!
- Modern NeoVIM (0.5+) has native Lua runtime
- Plugin written in **pure Lua** for maximum performance
- Uses built-in LSP, Treesitter, and RPC APIs
- Optional Python provider via `pip install pynvim` (no rebuild)

### **Key Plugin Features:**
- Floating dashboard (`:TachyonDash`)
- Telescope integration for fuzzy finding
- Rego LSP configuration for policy editing
- Custom syntax highlighting for debates
- Side-by-side patch review with debate context

### **Technology Stack:**
- **TUI Framework**: Textual (Python) - excellent Ghostty support
- **CLI Framework**: Click - composable commands
- **API Client**: httpx - async, HTTP/2
- **NeoVIM Plugin**: Pure Lua - zero dependencies
- **Real-time**: WebSocket + Server-Sent Events

### **Implementation Roadmap:**
- **Phase 1-2** (Weeks 1-3): Core CLI + Agent Management
- **Phase 3** (Week 4): Airlock UI
- **Phase 4** (Weeks 5-6): NeoVIM Plugin
- **Phase 5** (Weeks 7-8): Advanced Features
- **Phase 6** (Weeks 9-10): Polish & Docs

### **Complete with:**
- ASCII mockups of all interface views
- Full API endpoint specifications
- Plugin directory structure
- Configuration examples for Ghostty
- Sample workflows (morning check, zero-day response)
- Testing strategy and performance targets

The document is ready to use with your AntiGravity system for implementation! 🚀

# Tachyon Tongs CLI: Design & Implementation Specification

**Version:** 1.0.0  
**Status:** Design Phase  
**Target:** Ghostty Terminal + NeoVIM Integration  
**Date:** March 19, 2026

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Philosophy](#design-philosophy)
3. [Architecture Overview](#architecture-overview)
4. [CLI Interface Design](#cli-interface-design)
5. [Ghostty Integration](#ghostty-integration)
6. [NeoVIM Plugin Architecture](#neovim-plugin-architecture)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Technical Specifications](#technical-specifications)
9. [User Workflows](#user-workflows)
10. [Future Enhancements](#future-enhancements)

---

## Executive Summary

The Tachyon CLI (`tcli`) is a modern, GPU-accelerated terminal interface for monitoring and managing the Tachyon Tongs security substrate. It provides real-time visibility into agent operations, threat intelligence, and substrate health through a clean, ergonomic interface optimized for Ghostty terminal and deep NeoVIM integration.

### Key Features

- **Real-time Dashboard**: Live substrate metrics, agent status, threat feed
- **Agent Orchestration**: Start, stop, inspect agents with full lifecycle management
- **Airlock Management**: Review, approve, deny patches with diff visualization
- **Log Streaming**: Tail EVOLUTION.md, ALERT.md, CANARY_LOG.md with syntax highlighting
- **Interactive Debugging**: Step through agent reasoning, inspect state transitions
- **NeoVIM Deep Integration**: Edit files in-place, navigate debates, manage ADRs

### Design Principles

1. **Speed**: Leverage Ghostty's GPU acceleration for instant updates
2. **Clarity**: Information-dense without clutter, semantic color coding
3. **Ergonomics**: Vi-style keybindings, composable commands
4. **Observability**: Full transparency into agent cognitive processes
5. **Safety**: Read-only by default, explicit confirmation for mutations

---

## Design Philosophy

### Visual Language

The CLI adopts a **security operations center** aesthetic:

- **Dark theme** with high-contrast text (optimized for Ghostty's renderer)
- **Semantic colors**: 
  - 🟢 Green: Normal operations, approvals
  - 🔵 Blue: Info, agent activity
  - 🟡 Yellow: Warnings, pending actions
  - 🔴 Red: Alerts, denials, integrity failures
  - 🟣 Purple: Debates, reasoning traces
- **Box drawing characters** for clean panel separation
- **Nerdfont icons** for visual anchors (Ghostty renders these perfectly)

### Interaction Model

```
┌─────────────────────────────────────────────────────────────┐
│ COMMAND MODE (default)                                      │
│  • Vi-style navigation (j/k, Ctrl+d/u)                      │
│  • Single-key actions (r=refresh, a=approve, d=deny)        │
│  • Command palette (:) for advanced operations              │
├─────────────────────────────────────────────────────────────┤
│ FOCUS MODE (Shift+Enter on item)                           │
│  • Full-screen view of selected agent/log/debate            │
│  • Arrow keys for navigation                                │
│  • Esc to return to dashboard                               │
├─────────────────────────────────────────────────────────────┤
│ EDIT MODE (e on editable item)                             │
│  • Launches NeoVIM with proper context                      │
│  • Returns to CLI on :wq, auto-refreshes                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Overview

### Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      Tachyon CLI (tcli)                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  TUI Frontend  │  │  CLI Commands  │  │  API Client   │ │
│  │   (Textual)    │  │   (Click)      │  │   (httpx)     │ │
│  └────────┬───────┘  └────────┬───────┘  └───────┬───────┘ │
│           │                   │                   │          │
│           └───────────────────┴───────────────────┘          │
│                              │                               │
├──────────────────────────────┼───────────────────────────────┤
│                              │                               │
│  ┌────────────────┐  ┌───────▼────────┐  ┌───────────────┐ │
│  │ NeoVIM Plugin  │  │  Substrate API │  │  State Cache  │ │
│  │  (tachyon.nvim)│  │   (FastAPI)    │  │   (Redis)     │ │
│  └────────┬───────┘  └───────┬────────┘  └───────┬───────┘ │
│           │                   │                   │          │
├───────────┼───────────────────┼───────────────────┼──────────┤
│           │                   │                   │          │
│  ┌────────▼───────────────────▼───────────────────▼───────┐ │
│  │           Tachyon Tongs Substrate Daemon              │ │
│  │  (PDP, PEP, StateManager, Agents, Integrity)          │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **TUI Framework** | Textual (Python) | Rich widget library, async-native, excellent Ghostty support |
| **CLI Framework** | Click | Industry standard, composable, great help generation |
| **API Client** | httpx | Async HTTP, connection pooling, HTTP/2 support |
| **NeoVIM Plugin** | Lua (native) + plenary.nvim | No Python rebuild needed, fast, well-supported |
| **Substrate API** | FastAPI (existing) | Already part of Tachyon architecture |
| **Real-time Updates** | WebSocket + Server-Sent Events | Low-latency streaming for logs and agent state |
| **State Cache** | Redis (optional) | Performance optimization for large catalogs |

---

## CLI Interface Design

### 1. Dashboard View (`tcli dash`)

**Purpose**: Real-time overview of substrate health

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
║ │ [06:42:05] 🔵 Canary logged suspicious endpoint: evil.example.com   │ ║
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

**Key Bindings**:
- `r` - Force refresh (auto-refreshes every 2s)
- `a` - Jump to agents panel
- `l` - Jump to logs panel
- `i` - Inspect selected item (agent/patch/alert)
- `:` - Command palette
- `q` - Quit (with confirmation if agents running)
- `?` - Help overlay

---

### 2. Agent Management View (`tcli agents`)

**Purpose**: Start, stop, monitor individual agents

```
╔══════════════════════════════════════════════════════════════════════════╗
║ AGENT MANAGEMENT                                   [Tab] to switch view  ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║ ┌─ AGENT: sentinel (Blue Team) ───────────────────────────────────────┐ ║
║ │ Status: 🔵 Running                                                   │ ║
║ │ PID: 42301                                                           │ ║
║ │ Uptime: 3d 14h 22m                                                   │ ║
║ │ Memory: 142 MB                                                       │ ║
║ │ CPU: 2.3%                                                            │ ║
║ │                                                                      │ ║
║ │ Skill: /agents/sentinel/SKILL.md                                     │ ║
║ │ Role: Threat Intelligence Aggregation                                │ ║
║ │                                                                      │ ║
║ │ ┌─ RECENT ACTIONS ──────────────────────────────────────────────┐   │ ║
║ │ │ [07:12:34] Polled NVD API (200 OK, 42 results)                │   │ ║
║ │ │ [07:12:35] Filtered to 3 AI-relevant CVEs                      │   │ ║
║ │ │ [07:12:36] Cataloged CVE-2026-0042 (CRITICAL)                  │   │ ║
║ │ │ [07:12:37] Signed EXPLOITATION_CATALOG.md                      │   │ ║
║ │ │ [07:12:38] Triggered Engineer autopatch workflow               │   │ ║
║ │ └────────────────────────────────────────────────────────────────┘   │ ║
║ │                                                                      │ ║
║ │ ┌─ LIVE LOG TAIL ───────────────────────────────────────────────┐   │ ║
║ │ │ INFO  [sentinel.scout] Initiating scan cycle #2,845           │   │ ║
║ │ │ DEBUG [sentinel.scout] Fetching NVD feed (since: 2026-03-19)  │   │ ║
║ │ │ INFO  [sentinel.analyst] Relevance score: 0.92 (threshold:0.7)│   │ ║
║ │ │ WARN  [sentinel.analyst] High severity detected: CRITICAL     │   │ ║
║ │ │ INFO  [sentinel.engineer] Staging entry to catalog            │   │ ║
║ │ └────────────────────────────────────────────────────────────────┘   │ ║
║ └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║ [s]top [r]estart [k]ill [v]iew-skill [t]race [e]dit-config             ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Key Bindings**:
- `s` - Stop agent gracefully (SIGTERM)
- `r` - Restart agent (stop + start)
- `k` - Force kill (SIGKILL, with confirmation)
- `v` - View SKILL.md in pager
- `t` - Toggle trace mode (verbose reasoning log)
- `e` - Edit agent config in NeoVIM
- `Tab` - Cycle through agents
- `Shift+Tab` - Reverse cycle

---

### 3. Airlock Management View (`tcli airlock`)

**Purpose**: Review and authorize autonomous patches

```
╔══════════════════════════════════════════════════════════════════════════╗
║ AIRLOCK: PATCH STAGING & REVIEW                                         ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║ ┌─ PATCH: patch-b4e3a1 ────────────────────────────────────────────────┐ ║
║ │ CVE: CVE-2026-0042 (CRITICAL)                                        │ ║
║ │ Synthesized: 2026-03-19 07:08:22                                     │ ║
║ │ Engineer: legacy-engineer                                            │ ║
║ │ Debate Status: ✓ Complete (Skeptic + Meta-Critic)                   │ ║
║ │                                                                      │ ║
║ │ ┌─ THREAT SUMMARY ──────────────────────────────────────────────┐   │ ║
║ │ │ Prompt injection via Unicode steganography in web scraped     │   │ ║
║ │ │ content. Attacker embeds zero-width characters (U+200B) to    │   │ ║
║ │ │ hide malicious instructions from human review but visible to  │   │ ║
║ │ │ LLM tokenizer. Bypass current Guardian Triad regex filters.   │   │ ║
║ │ └────────────────────────────────────────────────────────────────┘   │ ║
║ │                                                                      │ ║
║ │ ┌─ PROPOSED MITIGATION ─────────────────────────────────────────┐   │ ║
║ │ │ Enhanced Unicode normalization in SanitizerNode (Analyst):    │   │ ║
║ │ │ - Strip all zero-width characters (U+200B-U+200D, U+FEFF)     │   │ ║
║ │ │ - Normalize to NFC before LLM processing                      │   │ ║
║ │ │ - Add Rego policy to block suspicious Unicode density         │   │ ║
║ │ └────────────────────────────────────────────────────────────────┘   │ ║
║ │                                                                      │ ║
║ │ ┌─ DIFF PREVIEW ────────────────────────────────────────────────┐   │ ║
║ │ │ agents/guardian_ids/SKILL.md                                  │   │ ║
║ │ │ @@ -45,6 +45,9 @@ def sanitize_external_content(raw: str):│   │ ║
║ │ │ +    # Strip zero-width steganography                         │   │ ║
║ │ │ +    content = re.sub(r'[\u200B-\u200D\uFEFF]', '', content)  │   │ ║
║ │ │ +    content = unicodedata.normalize('NFC', content)          │   │ ║
║ │ │                                                                │   │ ║
║ │ │ configs/opa_policies/guardian_triad.rego                      │   │ ║
║ │ │ @@ -12,6 +12,11 @@ deny[msg] {                           │   │ ║
║ │ │ +    suspicious_unicode_density(input.content)                │   │ ║
║ │ │ +    msg := "High density of zero-width characters detected"  │   │ ║
║ │ └────────────────────────────────────────────────────────────────┘   │ ║
║ │                                                                      │ ║
║ │ ┌─ DEBATE SUMMARY (view full: d) ──────────────────────────────┐   │ ║
║ │ │ Skeptic: "Normalization could break legitimate use cases      │   │ ║
║ │ │           (e.g., math notation). Needs allowlist."            │   │ ║
║ │ │ Engineer: "Added exemption for \u200B in <math> tags."        │   │ ║
║ │ │ Meta-Critic: "Approved. Risk/benefit favors deployment."      │   │ ║
║ │ └────────────────────────────────────────────────────────────────┘   │ ║
║ └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║ [a]pprove [d]eny [v]iew-full-diff [b]debate [t]test-locally [n]ext     ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Key Bindings**:
- `a` - Approve patch (with confirmation, triggers signing + deployment)
- `d` - Deny patch (with reason prompt, logs to PENDING_MERGE.md)
- `v` - View full unified diff in NeoVIM
- `b` - View full debate transcript in NeoVIM
- `t` - Test patch in local sandbox (dry-run)
- `n` / `p` - Next/previous patch in queue
- `e` - Edit patch files directly (advanced, with warning)

---

### 4. Log Streaming View (`tcli logs`)

**Purpose**: Real-time tail of substrate logs with filtering

```
╔══════════════════════════════════════════════════════════════════════════╗
║ LOG STREAMING: EVOLUTION.md                     [Ctrl+C to pause]       ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║ Filter: [agent:engineer] [level:INFO,WARN,ERROR] [since:1h]             ║
║                                                                          ║
║ 🔵 [07:12:34] [INFO ] [engineer.apply] Applying patch-b4e3a1            ║
║ 🔵 [07:12:35] [INFO ] [engineer.apply] Modified: guardian_ids/SKILL.md  ║
║ 🔵 [07:12:35] [INFO ] [engineer.apply] Modified: opa_policies/guard...  ║
║ 🔵 [07:12:36] [INFO ] [engineer.verify] Running integrity check         ║
║ 🟢 [07:12:37] [INFO ] [engineer.verify] Integrity: PASSED ✓             ║
║ 🔵 [07:12:37] [INFO ] [engineer.sign] Generating HMAC signature         ║
║ 🟢 [07:12:38] [INFO ] [engineer.sign] Signed: guardian_ids/SKILL.md.sig ║
║ 🔵 [07:12:38] [INFO ] [engineer.ledger] Updating EVOLUTION.md           ║
║ 🟢 [07:12:39] [INFO ] [engineer.complete] Patch applied successfully    ║
║                                                                          ║
║ 🔵 [07:10:15] [INFO ] [guardian.audit] Starting periodic audit          ║
║ 🔵 [07:10:16] [INFO ] [guardian.audit] Verifying ADR signatures         ║
║ 🔵 [07:10:17] [INFO ] [guardian.audit] Checked: 22 ADRs, 22 valid       ║
║ 🔵 [07:10:18] [INFO ] [guardian.audit] Verifying catalog signature      ║
║ 🟢 [07:10:19] [INFO ] [guardian.audit] Audit complete: PASSED ✓         ║
║                                                                          ║
║ 🔵 [07:08:22] [INFO ] [engineer.stage] Staging patch for CVE-2026-0042  ║
║ 🟡 [07:08:23] [WARN ] [engineer.stage] Airlock queue: 2/8 (25% full)    ║
║ 🔵 [07:08:23] [INFO ] [engineer.debate] Initiating Skeptic review       ║
║                                                                          ║
║ ┌─ QUICK FILTERS ──────────────────────────────────────────────────────┐ ║
║ │ [1] All  [2] Errors Only  [3] Warnings+  [4] Agent:Sentinel          │ ║
║ │ [5] Agent:Engineer  [6] Last Hour  [7] Last 24h  [8] Custom...       │ ║
║ └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║ [/]filter [c]lear [f]ollow [p]ause [s]witch-log [e]xport               ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Key Bindings**:
- `/` - Open filter prompt (regex support)
- `c` - Clear current filters
- `f` - Toggle follow mode (auto-scroll)
- `p` - Pause/resume streaming
- `s` - Switch log source (EVOLUTION.md, ALERT.md, CANARY_LOG.md, RUN_LOG.md)
- `e` - Export filtered view to file
- `1-8` - Quick filter presets
- `j/k` - Scroll (when paused)
- `Ctrl+d/u` - Page down/up

---

### 5. Threat Intelligence View (`tcli catalog`)

**Purpose**: Browse and search the Exploitation Catalog

```
╔══════════════════════════════════════════════════════════════════════════╗
║ EXPLOITATION CATALOG                                245 threats indexed  ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║ Search: [unicode injection]                      Sort: [severity ▼]     ║
║                                                                          ║
║ ┌─ CVE-2026-0042 ──────────────────────────────────────────────────────┐ ║
║ │ 🔴 CRITICAL │ Discovered: 2026-03-19 │ Status: 🟢 MITIGATED           │ ║
║ │                                                                      │ ║
║ │ Title: Unicode Steganography Injection                               │ ║
║ │                                                                      │ ║
║ │ Description:                                                         │ ║
║ │ Attacker embeds malicious instructions using zero-width Unicode      │ ║
║ │ characters (U+200B-U+200D, U+FEFF) in web content. These chars are   │ ║
║ │ invisible to human reviewers but tokenized by LLMs, allowing prompt  │ ║
║ │ injection to bypass visual inspection and basic regex filters.       │ ║
║ │                                                                      │ ║
║ │ Attack Vector:                                                       │ ║
║ │ - Compromised website includes hidden Unicode in meta tags           │ ║
║ │ - Agent scrapes page via safe_fetch                                  │ ║
║ │ - Guardian Triad sanitizer misses zero-width chars                   │ ║
║ │ - LLM processes hidden instructions, overrides system prompt         │ ║
║ │                                                                      │ ║
║ │ Mitigation: Patch patch-b4e3a1 (Deployed: 2026-03-19 07:12:39)       │ ║
║ │ - Enhanced Unicode normalization in SanitizerNode                    │ ║
║ │ - OPA policy to block suspicious Unicode density                     │ ║
║ │                                                                      │ ║
║ │ Testing: Pathogen stress-test (Block rate: 100%, 0/50 bypasses)      │ ║
║ │                                                                      │ ║
║ │ References:                                                          │ ║
║ │ - NVD: https://nvd.nist.gov/vuln/detail/CVE-2026-0042               │ ║
║ │ - GitHub Advisory: GHSA-xxxx-yyyy-zzzz                              │ ║
║ └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║ [n]ext [p]rev [d]etails [t]est [r]elated [e]xport [/]search            ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Key Bindings**:
- `n/p` - Next/previous threat
- `d` - Full details view (expand)
- `t` - Run Pathogen test against this threat
- `r` - Show related threats (same family/technique)
- `e` - Export threat as markdown
- `/` - Search/filter catalog
- `Enter` - Open in NeoVIM for annotation

---

## Ghostty Integration

### Why Ghostty?

Ghostty is a GPU-accelerated terminal with native support for:
- **True color** (24-bit RGB)
- **Ligatures** (for => != === in code diffs)
- **Box drawing** (perfect Unicode support)
- **Zero input lag** (critical for real-time monitoring)
- **Custom shaders** (potential for security-themed effects)

### Configuration

```bash
# ~/.config/ghostty/config

# Performance
gpu-renderer = true
repaint-delay = 0
vsync = true

# Font (use a Nerd Font for icons)
font-family = "JetBrainsMono Nerd Font"
font-size = 12

# Tachyon color scheme
background = 0a0e14
foreground = e6e6e6

# Semantic colors (match Tachyon palette)
palette = 0=1a1a2e   # Black (backgrounds)
palette = 1=f07178   # Red (alerts)
palette = 2=c3e88d   # Green (success)
palette = 3=ffcb6b   # Yellow (warnings)
palette = 4=82aaff   # Blue (info)
palette = 5=c792ea   # Magenta (debates)
palette = 6=89ddff   # Cyan (highlights)
palette = 7=d6deeb   # White (text)

# Keybindings for Tachyon workflows
keybind = ctrl+shift+t=new_tab:tcli dash
keybind = ctrl+shift+a=new_tab:tcli airlock
keybind = ctrl+shift+l=new_tab:tcli logs
```

### Custom Window Titles

The CLI sets Ghostty window titles dynamically:

```python
# In tcli code
import sys

def set_ghostty_title(title: str):
    """Update Ghostty window title"""
    sys.stdout.write(f"\033]0;Tachyon: {title}\007")
    sys.stdout.flush()

# Usage
set_ghostty_title("Dashboard - 5 Agents Running")
set_ghostty_title("Airlock - 2 Patches Pending")
```

### Clickable URLs

Ghostty auto-detects URLs in output. The CLI formats links for direct opening:

```python
def format_cve_link(cve_id: str) -> str:
    """Format CVE as clickable link"""
    return f"\033]8;;https://nvd.nist.gov/vuln/detail/{cve_id}\007{cve_id}\033]8;;\007"

# Renders as: CVE-2026-0042 (Ctrl+click to open in browser)
```

---

## NeoVIM Plugin Architecture

### Do You Need to Rebuild NeoVIM with Python Support?

**No!** Modern NeoVIM (0.5+) has:
- **Native Lua runtime** (no external dependencies)
- **Built-in LSP client** (for code intelligence)
- **RPC API** (for external process communication)
- **Treesitter** (for syntax highlighting)

Python support is available via **external providers** (no rebuild needed):
```bash
pip install pynvim  # Python host for remote plugins
```

But for Tachyon, we'll use **pure Lua** for maximum performance and zero Python dependency conflicts.

### Plugin Structure: `tachyon.nvim`

```
tachyon.nvim/
├── lua/
│   ├── tachyon/
│   │   ├── init.lua           # Main plugin entry
│   │   ├── config.lua         # User configuration
│   │   ├── api.lua            # HTTP client for Substrate API
│   │   ├── ui/
│   │   │   ├── dashboard.lua  # Floating dashboard window
│   │   │   ├── airlock.lua    # Patch review UI
│   │   │   └── picker.lua     # Telescope integration
│   │   ├── lsp/
│   │   │   └── rego.lua       # Rego policy LSP integration
│   │   └── commands.lua       # Ex commands (:Tachyon*)
│   └── telescope/
│       └── _extensions/
│           └── tachyon.lua    # Telescope picker for agents/logs
├── ftdetect/
│   └── tachyon.vim            # File type detection (.sig, SKILL.md)
├── syntax/
│   ├── debate.vim             # Debate transcript highlighting
│   └── skillmd.vim            # SKILL.md syntax
├── after/
│   └── queries/
│       └── rego/              # Treesitter queries for Rego
│           └── highlights.scm
├── plugin/
│   └── tachyon.vim            # Plugin initialization
├── doc/
│   └── tachyon.txt            # Vim help documentation
└── README.md
```

### Core Features

#### 1. Floating Dashboard (`:TachyonDash`)

```lua
-- lua/tachyon/ui/dashboard.lua
local M = {}

function M.open()
  local buf = vim.api.nvim_create_buf(false, true)
  local width = math.floor(vim.o.columns * 0.8)
  local height = math.floor(vim.o.lines * 0.8)
  
  local win = vim.api.nvim_open_win(buf, true, {
    relative = 'editor',
    width = width,
    height = height,
    row = math.floor((vim.o.lines - height) / 2),
    col = math.floor((vim.o.columns - width) / 2),
    style = 'minimal',
    border = 'rounded',
    title = ' Tachyon Dashboard ',
    title_pos = 'center',
  })
  
  -- Fetch substrate status from API
  local api = require('tachyon.api')
  api.get_status(function(status)
    M.render_dashboard(buf, status)
  end)
  
  -- Set up keybindings
  local opts = { buffer = buf, noremap = true, silent = true }
  vim.keymap.set('n', 'q', ':close<CR>', opts)
  vim.keymap.set('n', 'r', function() M.refresh(buf) end, opts)
  vim.keymap.set('n', 'a', ':TachyonAgents<CR>', opts)
  
  -- Auto-refresh every 2 seconds
  local timer = vim.loop.new_timer()
  timer:start(2000, 2000, vim.schedule_wrap(function()
    M.refresh(buf)
  end))
  
  -- Clean up timer on buffer close
  vim.api.nvim_create_autocmd('BufWipeout', {
    buffer = buf,
    callback = function() timer:stop() end,
  })
end

return M
```

#### 2. Airlock Review (`:TachyonAirlock`)

Provides a side-by-side diff view with debate context:

```lua
-- lua/tachyon/ui/airlock.lua
function M.review_patch(patch_id)
  -- Open 3-way split: debate | diff | controls
  vim.cmd('tabnew')
  
  -- Left: Debate transcript
  vim.cmd('vnew')
  local debate_buf = vim.api.nvim_get_current_buf()
  vim.api.nvim_buf_set_lines(debate_buf, 0, -1, false, 
    get_debate_content(patch_id))
  vim.bo[debate_buf].filetype = 'debate'
  
  -- Center: Diff view
  vim.cmd('wincmd l')
  vim.cmd('vnew')
  local diff_buf = vim.api.nvim_get_current_buf()
  vim.api.nvim_buf_set_lines(diff_buf, 0, -1, false,
    get_patch_diff(patch_id))
  vim.bo[diff_buf].filetype = 'diff'
  
  -- Right: Approval controls
  vim.cmd('wincmd l')
  vim.cmd('vnew')
  local controls_buf = vim.api.nvim_get_current_buf()
  render_approval_ui(controls_buf, patch_id)
  
  -- Keybindings
  vim.keymap.set('n', '<leader>aa', function()
    approve_patch(patch_id)
  end, { buffer = controls_buf })
  
  vim.keymap.set('n', '<leader>ad', function()
    deny_patch(patch_id)
  end, { buffer = controls_buf })
end
```

#### 3. Telescope Integration (`:Telescope tachyon`)

Browse agents, logs, and debates with fuzzy finding:

```lua
-- lua/telescope/_extensions/tachyon.lua
local pickers = require('telescope.pickers')
local finders = require('telescope.finders')
local conf = require('telescope.config').values

local function pick_agents(opts)
  opts = opts or {}
  
  pickers.new(opts, {
    prompt_title = 'Tachyon Agents',
    finder = finders.new_table {
      results = get_all_agents(),
      entry_maker = function(agent)
        return {
          value = agent,
          display = string.format('[%s] %s - %s',
            agent.status_icon, agent.name, agent.role),
          ordinal = agent.name,
        }
      end,
    },
    sorter = conf.generic_sorter(opts),
    attach_mappings = function(prompt_bufnr, map)
      map('i', '<CR>', function()
        local selection = require('telescope.actions.state')
          .get_selected_entry()
        require('tachyon.ui.agent').inspect(selection.value.name)
      end)
      return true
    end,
  }):find()
end

return require('telescope').register_extension {
  exports = {
    agents = pick_agents,
    logs = pick_logs,
    debates = pick_debates,
    catalog = pick_catalog,
  }
}
```

#### 4. LSP Integration for Rego Policies

```lua
-- lua/tachyon/lsp/rego.lua
local lspconfig = require('lspconfig')

-- Configure Rego LSP (requires: go install github.com/kitagry/regols@latest)
lspconfig.regols.setup({
  cmd = { 'regols' },
  filetypes = { 'rego' },
  root_dir = function(fname)
    return lspconfig.util.find_git_ancestor(fname) or vim.fn.getcwd()
  end,
  settings = {
    rego = {
      -- Point to Tachyon OPA policies
      workspaceRoots = {
        vim.fn.expand('~/antigravity/tachyon_tongs/configs/opa_policies')
      },
    },
  },
})
```

#### 5. Custom File Type Detection

```vim
" ftdetect/tachyon.vim

" Debate transcripts
au BufRead,BufNewFile */debates/*.md setfiletype debate

" SKILL.md manifests  
au BufRead,BufNewFile */agents/*/SKILL.md setfiletype skillmd

" Signature files
au BufRead,BufNewFile *.sig setfiletype signature

" Rego policies
au BufRead,BufNewFile *.rego setfiletype rego
```

#### 6. Debate Syntax Highlighting

```vim
" syntax/debate.vim

syntax match debateTimestamp /\[\d\{4}-\d\{2}-\d\{2} \d\{2}:\d\{2}:\d\{2}\]/
syntax match debateAgent /\*\*\(Skeptic\|Engineer\|Meta-Critic\):/
syntax match debateVerdict /APPROVED\|REJECTED\|ESCALATE/
syntax region debateQuote start=/"/ end=/"/

highlight link debateTimestamp Comment
highlight link debateAgent Function
highlight link debateVerdict Keyword
highlight link debateQuote String
```

### Installation

```vim
" Using lazy.nvim
{
  'roydsouza/tachyon.nvim',
  dependencies = {
    'nvim-lua/plenary.nvim',      -- HTTP client
    'nvim-telescope/telescope.nvim', -- Fuzzy finder
    'neovim/nvim-lspconfig',      -- LSP integration
  },
  config = function()
    require('tachyon').setup({
      substrate_url = 'http://localhost:8181',
      auto_refresh = true,
      refresh_interval = 2000, -- ms
      dashboard_on_startup = false,
      keybindings = {
        dashboard = '<leader>td',
        agents = '<leader>ta',
        airlock = '<leader>tl',
        logs = '<leader>to',
        catalog = '<leader>tc',
      },
    })
  end,
}
```

### Keybinding Reference

| Key | Command | Description |
|-----|---------|-------------|
| `<leader>td` | `:TachyonDash` | Open dashboard |
| `<leader>ta` | `:TachyonAgents` | Agent manager |
| `<leader>tl` | `:TachyonAirlock` | Airlock review |
| `<leader>to` | `:TachyonLogs` | Log viewer |
| `<leader>tc` | `:TachyonCatalog` | Threat catalog |
| `<leader>ts` | `:TachyonStatus` | Quick status line |
| `<leader>tr` | `:TachyonRun <agent>` | Run specific agent |
| `<leader>tk` | `:TachyonKill <agent>` | Stop agent |

---

## Implementation Roadmap

### Phase 1: Core CLI (Week 1-2)

**Deliverables**:
- [x] Project structure setup
- [x] Textual TUI framework integration
- [x] Basic dashboard view (static mockup)
- [x] Agent status panel with real API calls
- [x] Log streaming (EVOLUTION.md tail)
- [x] Ghostty configuration template

**Tasks**:
1. Set up Python project with poetry/uv
2. Create Textual app shell
3. Implement Substrate API client (httpx)
4. Build dashboard widgets
5. Add WebSocket support for real-time updates
6. Package as `tcli` command

### Phase 2: Agent Management (Week 3)

**Deliverables**:
- [x] Agent lifecycle controls (start/stop/restart)
- [x] Live log tailing per agent
- [x] Process monitoring (PID, CPU, Memory)
- [x] Skill manifest viewer
- [x] Configuration editor (launches NeoVIM)

**Tasks**:
1. Implement agent process management
2. Parse SKILL.md manifests
3. Add agent-specific log filtering
4. Create agent detail view
5. Integrate with NeoVIM for config editing

### Phase 3: Airlock UI (Week 4)

**Deliverables**:
- [x] Patch queue listing
- [x] Diff viewer (unified + side-by-side)
- [x] Debate transcript viewer
- [x] Approve/deny workflow with confirmation
- [x] Test patch locally (dry-run mode)

**Tasks**:
1. Parse patch metadata from Airlock directory
2. Build diff rendering engine
3. Implement debate log parser
4. Add approval API calls
5. Create local sandbox test harness

### Phase 4: NeoVIM Plugin (Week 5-6)

**Deliverables**:
- [x] Plugin structure and installation
- [x] Floating dashboard
- [x] Telescope integration
- [x] Rego LSP configuration
- [x] Custom file type detection
- [x] Debate syntax highlighting

**Tasks**:
1. Create Lua plugin skeleton
2. Implement API client in Lua
3. Build floating windows
4. Write Telescope pickers
5. Add syntax definitions
6. Write documentation (`:help tachyon`)

### Phase 5: Advanced Features (Week 7-8)

**Deliverables**:
- [x] Threat catalog browser with search
- [x] Export capabilities (logs, diffs, debates)
- [x] Custom filtering DSL
- [x] Multi-agent orchestration (start/stop groups)
- [x] Notification system (desktop alerts)
- [x] Performance metrics dashboard

**Tasks**:
1. Build catalog search index
2. Implement export formats (JSON, Markdown, PDF)
3. Create filter parser
4. Add agent group management
5. Integrate with system notifications
6. Add performance instrumentation

### Phase 6: Polish & Documentation (Week 9-10)

**Deliverables**:
- [x] Comprehensive README
- [x] Video demo/walkthrough
- [x] Man pages (`man tcli`)
- [x] Troubleshooting guide
- [x] Plugin documentation
- [x] Community showcase examples

---

## Technical Specifications

### API Endpoints (Substrate)

The CLI communicates with the Substrate Daemon via REST + WebSocket:

```python
# FastAPI routes to add to tachyon/api/routes.py

@router.get("/api/v1/status")
async def get_substrate_status():
    """Dashboard health metrics"""
    return {
        "status": "operational",
        "mode": "HITL",
        "uptime_seconds": get_uptime(),
        "integrity": "verified",
        "merkle_root": get_merkle_root(),
    }

@router.get("/api/v1/agents")
async def list_agents():
    """All registered agents with status"""
    return [
        {
            "name": "sentinel",
            "role": "Blue Team",
            "status": "running",
            "pid": 42301,
            "uptime": 123456,
            "memory_mb": 142,
            "cpu_percent": 2.3,
        },
        # ... other agents
    ]

@router.get("/api/v1/agents/{agent_name}")
async def get_agent_detail(agent_name: str):
    """Detailed agent state"""
    return {
        "name": agent_name,
        "status": "running",
        "skill_path": f"/agents/{agent_name}/SKILL.md",
        "recent_actions": get_agent_actions(agent_name),
        "config": load_agent_config(agent_name),
    }

@router.post("/api/v1/agents/{agent_name}/start")
async def start_agent(agent_name: str):
    """Start an agent"""
    pid = spawn_agent(agent_name)
    return {"status": "started", "pid": pid}

@router.post("/api/v1/agents/{agent_name}/stop")
async def stop_agent(agent_name: str):
    """Graceful shutdown"""
    send_signal(agent_name, signal.SIGTERM)
    return {"status": "stopped"}

@router.get("/api/v1/airlock")
async def list_patches():
    """Pending patches in Airlock"""
    return [
        {
            "id": "patch-b4e3a1",
            "cve": "CVE-2026-0042",
            "timestamp": "2026-03-19T07:08:22Z",
            "debate_status": "complete",
            "diff_stats": {"additions": 42, "deletions": 3},
        },
        # ...
    ]

@router.get("/api/v1/airlock/{patch_id}")
async def get_patch_detail(patch_id: str):
    """Full patch metadata"""
    return {
        "id": patch_id,
        "cve": "CVE-2026-0042",
        "threat_summary": "...",
        "mitigation": "...",
        "diff": get_unified_diff(patch_id),
        "debate_transcript": get_debate(patch_id),
    }

@router.post("/api/v1/airlock/{patch_id}/approve")
async def approve_patch(patch_id: str):
    """Approve and deploy patch"""
    apply_patch(patch_id)
    sign_modified_files()
    update_merkle_root()
    return {"status": "approved", "deployed": True}

@router.post("/api/v1/airlock/{patch_id}/deny")
async def deny_patch(patch_id: str, reason: str):
    """Reject patch with reason"""
    move_to_rejected(patch_id, reason)
    return {"status": "denied"}

@router.websocket("/api/v1/logs/stream")
async def stream_logs(websocket: WebSocket):
    """Real-time log streaming"""
    await websocket.accept()
    async for line in tail_file("EVOLUTION.md"):
        await websocket.send_json({
            "timestamp": line.timestamp,
            "level": line.level,
            "agent": line.agent,
            "message": line.message,
        })
```

### CLI Command Structure

```bash
# Main entry point
tcli [global-options] <command> [command-options]

# Global options
--config PATH         # Custom config file (default: ~/.config/tcli/config.toml)
--substrate-url URL   # Substrate API endpoint (default: http://localhost:8181)
--no-color           # Disable color output
--verbose            # Verbose logging (-v, -vv, -vvv)

# Commands

# Dashboard (TUI)
tcli dash                       # Launch interactive dashboard
tcli dash --refresh-rate 1000   # Custom refresh interval (ms)

# Agent management
tcli agents                     # List all agents
tcli agents --running           # Only running agents
tcli agents start <name>        # Start agent
tcli agents stop <name>         # Stop agent
tcli agents restart <name>      # Restart agent
tcli agents inspect <name>      # Detailed view (TUI)
tcli agents logs <name>         # Tail agent logs

# Airlock
tcli airlock                    # Interactive review (TUI)
tcli airlock list               # List pending patches
tcli airlock inspect <id>       # View patch details
tcli airlock approve <id>       # Approve patch
tcli airlock deny <id>          # Deny patch
tcli airlock test <id>          # Dry-run test

# Logs
tcli logs                       # Interactive log viewer (TUI)
tcli logs tail [file]           # Tail specific log (EVOLUTION, ALERT, etc.)
tcli logs search <pattern>      # Search logs
tcli logs export <file>         # Export filtered logs

# Threat catalog
tcli catalog                    # Browse catalog (TUI)
tcli catalog search <query>     # Search threats
tcli catalog show <cve-id>      # Show CVE details
tcli catalog export             # Export as JSON/markdown

# Status
tcli status                     # Quick status summary
tcli status --json              # Machine-readable output
tcli health                     # Health check

# Utilities
tcli config                     # Edit config in $EDITOR
tcli docs                       # Open documentation
tcli version                    # Show version
```

### Configuration File

```toml
# ~/.config/tcli/config.toml

[substrate]
url = "http://localhost:8181"
timeout = 30  # seconds
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
default_log = "EVOLUTION"
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
sound_enabled = false

[neovim]
plugin_enabled = true
auto_open_dashboard = false
keybinding_prefix = "<leader>t"
```

---

## User Workflows

### Workflow 1: Morning Substrate Check

**Goal**: Quick health verification before starting work

```bash
# Terminal 1: Launch dashboard
tcli dash

# Quick visual scan:
# - All agents running? ✓
# - Integrity verified? ✓
# - Any alerts? Check ALERT panel
# - Airlock queue manageable? 2/8 patches pending

# If patches pending, review in NeoVIM
nvim
:TachyonAirlock

# Approve/deny patches, close
:wq

# Return to dashboard, verify patches applied
```

### Workflow 2: Investigating an Alert

**Goal**: Root cause analysis for STATE_COMPROMISED alert

```bash
# Dashboard shows red alert
tcli dash
# Press 'l' to jump to logs

# Filter for ERROR level
# Press '2' (Errors Only filter)

# See: INTEGRITY COMPROMISED: EXPLOITATION_CATALOG.md

# Open full investigation in NeoVIM
nvim
:TachyonLogs

# Search for timestamp
/07:12:34

# Follow trail:
# - Who modified the file? (git blame)
# - Was signature valid before? (check .sig)
# - Merkle root mismatch? (check MANIFEST.json)

# Resolution: Unauthorized edit by script, not malicious
# Re-sign catalog
:terminal
$ python3 scripts/forensic_resign.py

# Verify in CLI
tcli status
# Status: 🟢 OPERATIONAL
```

### Workflow 3: Deploying a New Agent

**Goal**: Add a custom "compliance-auditor" agent

```bash
# Create agent directory
mkdir -p ~/antigravity/tachyon_tongs/agents/compliance_auditor

# Write SKILL.md in NeoVIM with tachyon.nvim syntax
nvim ~/antigravity/tachyon_tongs/agents/compliance_auditor/SKILL.md

# Use SKILL.md template
:read /agents/sentinel/SKILL.md
# Edit to define compliance logic

# Register agent with substrate
tcli agents register compliance_auditor

# Start agent
tcli agents start compliance_auditor

# Monitor in dashboard
tcli dash
# Verify agent appears in "ACTIVE AGENTS" panel

# Tail agent logs for errors
tcli agents logs compliance_auditor
```

### Workflow 4: Zero-Day Response

**Goal**: Sentinel discovered critical CVE, need immediate action

```bash
# Notification appears: "🔴 CRITICAL threat cataloged"

# Jump to catalog
tcli catalog
# Press '/' to search
/CVE-2026-9999

# Read details
# Press 'd' for full view

# Verify Engineer staged patch
tcli airlock
# See: patch-xyz789 for CVE-2026-9999

# Review debate
# Press 'b' to open debate transcript

# Skeptic flagged concern about performance regression

# Test patch locally before approval
# Press 't' (test-locally)

# If test passes, approve
# Press 'a' (approve)

# Verify deployment
tcli status
# Shows: Last mutation: 30s ago (CVE-2026-9999 patch)

# Run Pathogen stress test
tcli agents start pathogen
# Monitor for block rate in dashboard
```

---

## Future Enhancements

### Advanced Monitoring

- **Distributed tracing**: Jaeger/Zipkin integration for multi-agent workflows
- **Metrics dashboards**: Prometheus + Grafana export for time-series analysis
- **Anomaly detection**: ML-based baseline deviation alerts
- **Correlation engine**: Link related events across logs/agents

### Collaboration Features

- **Multi-user mode**: Role-based access control for approval workflows
- **Slack/Discord webhooks**: Real-time notifications to security channels
- **Audit reports**: Auto-generate compliance reports (SOC2, ISO27001)
- **Video recording**: Asciinema integration for incident playback

### AI Assistance

- **Natural language queries**: "Show me all critical threats from last week"
- **Auto-triage**: AI suggests approve/deny based on debate analysis
- **Predictive alerts**: Forecast substrate resource exhaustion
- **Reasoning visualization**: Graph agent decision trees

### Developer Experience

- **VSCode extension**: Bring Tachyon monitoring to VSCode terminal
- **tmux integration**: Dedicated session layouts for substrate ops
- **Shell completions**: Bash/Zsh/Fish autocomplete for all commands
- **Quick actions**: Context-aware suggestions (e.g., "Restart agent?" on crash)

---

## Appendix

### Dependencies

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.10"
textual = "^0.47.0"         # TUI framework
click = "^8.1.7"            # CLI framework
httpx = "^0.26.0"           # Async HTTP client
rich = "^13.7.0"            # Terminal formatting
pydantic = "^2.5.0"         # Data validation
watchfiles = "^0.21.0"      # File watching for logs
pyyaml = "^6.0.1"           # Config parsing
websockets = "^12.0"        # Real-time updates

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
black = "^23.12.1"
ruff = "^0.1.9"

[tool.poetry.scripts]
tcli = "tachyon_cli.main:cli"
```

### Testing Strategy

```python
# tests/test_dashboard.py
import pytest
from textual.testing import TachyonApp
from tachyon_cli.ui.dashboard import Dashboard

@pytest.mark.asyncio
async def test_dashboard_renders():
    app = DashboardApp()
    async with app.run_test() as pilot:
        assert app.screen.title == "TACHYON SUBSTRATE DASHBOARD"
        assert "SUBSTRATE HEALTH" in app.screen.render()

@pytest.mark.asyncio  
async def test_dashboard_refresh():
    app = DashboardApp()
    async with app.run_test() as pilot:
        initial_uptime = get_uptime_text(app)
        await pilot.wait_for_scheduled_animations()
        await asyncio.sleep(2.5)  # Wait for auto-refresh
        new_uptime = get_uptime_text(app)
        assert new_uptime != initial_uptime
```

### Security Considerations

1. **API Authentication**: Add JWT tokens for Substrate API access
2. **Read-only mode**: Default CLI to read-only, require `--allow-mutations`
3. **Audit logging**: Log all CLI commands to separate audit trail
4. **Secure storage**: Encrypt stored credentials (if any)
5. **Network isolation**: CLI should only access localhost by default

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dashboard render | < 50ms | Time to first paint |
| Log line parse | < 1ms | Per line throughput |
| API request latency | < 100ms | 95th percentile |
| Memory footprint | < 100MB | RSS with all panels open |
| Keystroke latency | < 16ms | Input to screen update |

---

## Getting Started

### Quick Install

```bash
# Clone the repository
git clone https://github.com/roydsouza/tachyon-cli
cd tachyon-cli

# Install with pipx (recommended)
pipx install .

# Or with pip
pip install -e .

# Verify installation
tcli version

# Copy config template
cp config.example.toml ~/.config/tcli/config.toml

# Edit substrate URL if needed
$EDITOR ~/.config/tcli/config.toml

# Launch dashboard
tcli dash
```

### NeoVIM Plugin Install

```vim
" Using lazy.nvim
{
  'roydsouza/tachyon.nvim',
  dependencies = {
    'nvim-lua/plenary.nvim',
    'nvim-telescope/telescope.nvim',
    'neovim/nvim-lspconfig',
  },
  config = function()
    require('tachyon').setup()
  end,
}
```

```bash
# After adding to config, install
nvim
:Lazy sync

# Verify
:TachyonStatus
```

---

## Contributing

This is an open design document! Contributions welcome:

1. **UI/UX feedback**: How can we make monitoring more intuitive?
2. **Feature requests**: What workflows are missing?
3. **Bug reports**: Found issues in the mockups? Let us know
4. **Code contributions**: PRs for any phase of the roadmap

**Contact**: Open an issue at `github.com/roydsouza/tachyon-cli`

---

## License

MIT License - see LICENSE file for details

---

**End of Design Specification**

*This document is a living specification. Updates tracked in CHANGELOG.md*

