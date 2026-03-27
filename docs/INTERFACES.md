# Human-Substrate Interface Architecture (HSI)

This document establishes the official architectural layers, components, design principles, and forensic presentation channels for human interaction with the **Tachyon Tongs** security substrate.

> [!IMPORTANT]
> **Living Document**: This file must be kept in sync with the actual implementation. After any UX task, update §3 (Component Audit) and §5 (Implementation Status). Governed by `.agent/rules/UX-001.md`.

---

## 🏗️ 1. The Multi-Tier Interface Model

The Tachyon Substrate utilizes a three-layer interaction model to balance direct control, operational visibility, and remote accessibility.

### 🟢 Layer 1: CLI (Direct Command Plane)
The **CLI** is the primary entry point for low-latency engineering tasks and cryptographic governance. It is designed for POSIX-compliant terminal environments and follows the "Fail-Loud" principle.
- **Entry Point**: `python3 -m tachyon.cli.main` (aliased as `tt`)
- **Framework**: [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/)
- **Primary Commands**: `ritual`, `dash`, `status`, `airlock`, `immune`, `keys`, `agent`
- **Planned Commands**: `bus explore` (EventBus browser), `traffic` (Transit traffic inspector)

### 🔵 Layer 2: TUI (Operational Dashboard — "Single Pane of Glass")
The **TUI** (Textual User Interface) provides a persistent, high-fidelity view of the substrate's internal state. It is used for real-time monitoring of PQC coverage, alignment drift, agent health, and transit traffic.
- **Component**: `TachyonDash`
- **Engine**: [Textual](https://github.com/Textualize/textual)
- **Deployment**: Integrated directly into the `tt dash` command.
- **Layout**: Quad-pane grid (see §2.1 below)
- **Data Source**: Polls `StateBridge` via `/api/v1` (REST) and receives real-time updates via WebSocket (`/api/v1/logs/stream`).

### 🟡 Layer 3: StateBridge (Remote API & Bridge)
The **StateBridge** enables external visibility and remote command relay. It acts as a post-quantum encrypted gateway between the local substrate and remote dashboards or HITL (Human-In-The-Loop) interfaces.
- **Protocol**: FastAPI (REST) + WebSockets (Real-time).
- **Port**: 60461 (configurable via `TACHYON_PORT`).
- **Security**: Mandatory hybrid signature verification for all inbound commands (ADR-0067).

---

## 🎨 2. Design Principles (SPOG Architecture)

To establish a "Single Pane of Glass" (SPOG) management interface, all interface components must adhere to the following fundamental principles:

1. **Ambient Awareness**: Critical information (health, alerts, PQC status, governance mode) must be visible at a glance without requiring user interaction, in a persistent header bar.
2. **Progressive Disclosure**: Detailed information should be available on-demand (e.g., clicking an agent node) without cluttering the primary operational views.
3. **Zero-Latency Control**: High-risk actions, such as policy hot-swapping and agent action overrides, must be implemented with a latency target of **<100ms**.
4. **Forensic Completeness**: Every manual and automated interaction via any interface tier must be traceable, auditable, and cryptographically anchored in `forensics.db`.
5. **Multi-Modal Interaction**: Interaction models must prioritize keyboard-first workflows (TUI/CLI) while maintaining secondary accessibility for mouse/web-based stakeholders.

### 2.1. Quad-Pane TUI Layout

```
┌─ HEADER: version | daemon status | Merkle root | PQC ✓ | HITL ─────────┐
├──────────────────────────┬───────────────────────────────────────────────┤
│ 📊 AGENT HEARTBEAT (N)   │ 🚨 LIVE ALERT STREAM                        │
│  ✓ Sentinel    [███▓░]   │  14:23:15  HIGH  [T] Alignment drift        │
│  ✓ Guardian    [█████]   │  14:23:12  MED   Cache miss spike            │
│  ⚠ Scout       [█░░░░]   │  14:23:10  INFO  Policy hot-swapped         │
│  ...auto-discovered...   │  [T] = transit (external agent traffic)      │
├──────────────────────────┼───────────────────────────────────────────────┤
│ 🔁 INTER-AGENT TRAFFIC   │ 📈 POLICY ENFORCEMENT METRICS               │
│  (topology / flow graph) │  ████████░░ ALLOW 82%  ███░░ DENY 14%       │
│                          │  Internal: 86% | Transit: 14%                │
│                          │  Req/s: ~247 | P50: 2.3ms | P99: 23ms       │
├──────────────────────────┴───────────────────────────────────────────────┤
│ 💬 Command: tt airlock approve CVE-2026-9999  [Enter]                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2. Visual Semantics

| Element | Internal Agent | Transit (External) Agent |
|---------|---------------|-------------------------|
| **Badge** | (none) | `[T]` prefix in cyan |
| **Row Color** | Default white | Cyan tint |
| **Severity: HIGH** | Bold red | Bold red + `[T]` |
| **Severity: INFO** | Dim white | Dim cyan |

### 2.3. Extensibility Contract

- **Agent Discovery**: The TUI MUST use `AgentRegistry.list_plugins()` for agent enumeration — never hardcode agent names.
- **Event Topics**: New event topics from future agents are automatically rendered in the Alert Stream.
- **Widget Plugin Pattern**: Each TUI pane is a self-contained `Widget` subclass in `tachyon/cli/tui/widgets/`, making it easy to add new panes.

---

## 🔍 3. Interface Component Audit (2026-03-27)

The following files constitute the primary implementation of the HSI:

| Component | Path | Status | Description |
|-----------|------|--------|-------------|
| **CLI Loader** | `tachyon/cli/main.py` | ✅ Active | Typer-based entry point. Added `bus explore` and `traffic` commands. |
| **TUI App** | `tachyon/cli/tui/app.py` | ✅ Active | Quad-pane SPOG dashboard with real-time telemetry polling. |
| **TUI Widgets** | `tachyon/cli/tui/app.py` | ✅ Active | TacticalOverview, AgentInventory, HeraldLog, AirlockQueue. |
| **Bridge Server** | `tachyon/api/server.py` | ✅ Active | FastAPI + WebSocket (polling fallback). |
| **Bridge Routes** | `tachyon/api/routes.py` | ✅ Active | Endpoints: /status, /agents, /airlock, /forensics, /relay, /traffic/summary. |
| **API Schemas** | `tachyon/api/schema.py` | ✅ Active | Unified ToolRequest/Response. PQC-SignedCommand. |
| **StateBridge** | `tachyon/core/state_bridge.py` | ✅ Active | Dynamic agent state discovery via AgentRegistry. |
| **EventBus** | `tachyon/core/bus.py` | ✅ Active | SQLite-WAL pub/sub with PQC signature verification. |
| **TelemetryBus** | `tachyon/core/telemetry.py` | ✅ Active | JSONL + ForensicStore dual-write. Hardened for 1000+ EPS. |
| **ForensicStore** | `tachyon/core/forensics.py` | ✅ Active | PQC-signed SQLite ledger. Hardened for concurrent high-load. |
| **Terminal Config** | `docs/ghostty.conf` | ✅ Active | Ghostty terminal optimization. |
| **Web Dashboard** | `dashboard/src/App.tsx` | ⚠️ Scaffold | React+Vite. Future Phase. |

---

## 🛡️ 4. Forensic File Presentation

The substrate presents "Human-Readable Forensic Records" to ensure that the operator (and external auditors) can reconstruct the project's state without specialized tools.

### 🔴 ALERT.md (High-Signal Alerts)
A "Loud" append-only log located in the root directory. It contains critical security events (Intrusion Detection, Integrity Failures, Daemon Crashes) that require immediate human intervention.

### 🔄 SYNC_LOG.md (The Engineering Pulse)
A session-level engineering audit log. Every achievement, architectural decision, and implementation detail is recorded here and anchored to a specific timestamp and git commit.

### 🔲 TASKS_*.md (The Master Records)
Phased master task lists (`BOOTSTRAP`, `CLEANUP`, `ENHANCEMENTS`, `INTERFACES`). These files are the **ground truth** for the project's roadmap and engineering backlog.

### 📊 forensics.db (Structured Audit Ledger)
A high-assurance SQLite database containing the formal record of all `ActionRecord` objects, `DelegationCertificates`, and `TelemetryEvents`. Every entry is PQC-signed.

---

## ✅ 5. Implementation Status

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Foundation & Data Layer (INT-01 to INT-05) | ✅ 100% COMPLETE |
| **Phase 2** | TUI Dashboard — Read-Only SPOG (INT-10 to INT-15) | ✅ 100% COMPLETE |
| **Phase 3** | Remote Access & CLI Enhancements (INT-20 to INT-23) | ✅ 100% COMPLETE |
| **Phase 4** | Verification & Hardening (INT-30 to INT-33) | ✅ 100% COMPLETE |

---

## 🔒 6. Integrity Mandate

Every interface component MUST:
1. **Display Cryptographic Status**: All presented events must indicate if they were PQC-verified.
2. **Enforce Default-Deny**: Any command received via the StateBridge without a valid hybrid signature must be rejected.
3. **Log to the Ledger**: All human-initiated actions via any tier must be recorded in `forensics.db`.
4. **Distinguish Traffic Origin**: All events must carry a `source` field (`internal` | `transit`) and the UI must visually distinguish them.

> [!IMPORTANT]
> **AUDIT NOTE**: This document is cryptographically anchored to the substrate's Root of Trust and must be re-signed after any structural modification.
