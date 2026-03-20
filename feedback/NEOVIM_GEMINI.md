# Question

I am interested in a design for a clean CLI that I can use to monitor
and manage Tachyon Tongs, to run agents, to view their progress and outputs,
using Ghostty and perhaps adding close NeoVIM integration
(perhaps optionally through a new plug-in - do I need to build a new
NeoVIM that supports Python?). Could you please give me a detailed
markdown file I could use with AntiGravity for this design and implementation?

# Gemini:

This design document outlines the implementation of the **Event-Horizon Command Bridge**, a high-performance CLI/TUI designed for **Ghostty** and **NeoVim**. It serves as the primary tactical interface for your **Tachyon Tongs** agentic firewall.

To answer your technical question first: **No, you do not need to build a new NeoVim.** Modern NeoVim (v0.10+) uses Lua as its primary configuration language but supports Python integration seamlessly via the `pynvim` client. We will leverage this for the integration.

---

# 🛸 ARCHITECTURE DECISION RECORD: ADR-0012
## Title: The Event-Horizon Command Bridge (CLI/TUI)
**Status:** Proposed | **Target:** Event-Horizon (M5)

### 1. Intent
To provide a low-latency, "single-pane-of-glass" monitoring system for Tachyon Tongs. The bridge must allow Roy to launch the Sentinel/Pathogen agents, view the "Doom Ticker" in real-time, and manage the Accretion Archive without leaving the terminal.

### 2. The Toolkit
* **Host Terminal:** **Ghostty** (utilizing its fast GPU-rendering for high-frequency logs).
* **Logic Substrate:** **Python 3.12** with the **Textual** framework (for the TUI).
* **Integration:** **Lua-based NeoVim Plugin** (`tongs.nvim`) acting as a remote client to the `substrate_daemon.py`.

---

### 📂 File Structure Update
AntiGravity should scaffold these new directories:
```text
~/antigravity/tachyon_tongs/
├── scripts/
│   └── bridge.py             # The main TUI logic (Textual app)
├── .agents/
│   └── skills/
│       └── bridge-manager/   # AntiGravity skill to manage the TUI
└── plugin/
    └── tongs.nvim/           # Lua/Python bridge for NeoVim
```

---

### 📜 Implementation Plan: `bridge-design.md`

#### Phase 1: The TUI (The Command Bridge)
The TUI will be built using Python's `Textual` library. It will have three primary "Views":
1.  **🛰️ Tactical Overview:** A dashboard showing the status of the `substrate_daemon` and active agents.
2.  **💀 Doom Ticker:** A live-streamed feed of `RUN_LOG.md` and `verified_traffic.json`.
3.  **🪐 Archive Explorer:** A query interface for the **Accretion Archive** (NotebookLM).

**Ghostty Optimization:** Configure a Ghostty "Project Profile" that launches `bridge.py` in a split-pane layout alongside your coding environment.

#### Phase 2: NeoVim Integration (`tongs.nvim`)
Instead of a heavy Python-rebuild, we will use a **Lua-first** approach:
* **The Telemetry Window:** A floating window (buffer) in NeoVim that toggles with `<leader>tt`.
* **Action Handshake:** Highlight a block of code in NeoVim and press a key-chord to send it to the **Airlock** for a "Pathogen Audit."
* **Python Provider:** Ensure Roy has `pip install pynvim` in his global environment to allow NeoVim to communicate with the `substrate_daemon`.

#### Phase 3: AntiGravity Skill (`bridge-manager`)
Create a skill that allows your AntiGravity agents to "Talk to the Bridge":
* **Intent:** "Roy wants to see the current threat level."
* **Action:** The agent executes a tool call to `bridge.py --status --json` and summarizes the result.

---

### 🛠️ The AntiGravity Implementation Task
Paste this prompt into your AntiGravity session to begin the build:

> **"Roy here. Using the AC/DC methodology, design and implement the 'Event-Horizon Command Bridge'.**
>
> 1. **Scaffold `scripts/bridge.py`** using the **Textual** library. It must have a split-pane layout for the 'Doom Ticker' and 'Agent Status'.
> 2. **Create a `tongs.nvim` plugin** in Lua that creates a floating terminal window running the bridge.
> 3. **Reference `ROY_PREFERENCES.md`** for the visual aesthetic: high-density, technical, and optimized for the M5's Metal 4 rendering in Ghostty.
> 4. **Do not modify `src/substrate_daemon.py`** until you have a failing test in `tests/test_bridge_connection.py`."

---

### 🚫 Constraints & Safety
* **Verification:** The Bridge must require a **YubiKey Hardware Touch** before allowing an "Agent Mutation" command (e.g., changing Sentinel's system prompt).
* **Privacy:** The TUI must never display raw private keys, only the public key fingerprints and algorithm types (ECC/RSA).

**Would you like me to generate the initial Python code for the `bridge.py` (Textual) application so you can begin the first "Agentic TDD" loop?**

