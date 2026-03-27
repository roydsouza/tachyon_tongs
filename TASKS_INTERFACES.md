# 🖥️ Phase: Interfaces & Remote Access [ ] IN-PROGRESS

> [!IMPORTANT]
> **MASTER TASK RECORD**: This file is the primary source of truth for the project's interface engineering state.
> - **Pre-Work**: Always synchronize internal agent state from this file before starting work. Read `docs/INTERFACES.md` before touching any UI code.
> - **Post-Work**: Always update this file immediately upon task completion. Mark `[x]` for done, `[/]` for in-progress.
> - **Integrity**: Every modification requires a re-signing ritual (`scripts/forensics/resign_docs.py`).
> - **Assurance**: Every UI/Interface change MUST include exhaustive regression tests and a signed ADR.
> - **Commits**: One fix per commit. Format: `feat(interface): <one-line summary> [INT-<N>]`
> - **Workflow**: Follow the `/ux-interface` workflow (`.agent/workflows/ux-interface.md`) and the TDAD loop (`.agent/workflows/tdad.md`).
> - **UX Protocol**: Follow `UX-001` (`.agent/rules/UX-001.md`) — read `docs/INTERFACES.md` FIRST, then implement, then update it.

---

## 🎯 Vision & Objectives

Tachyon Tongs is a **post-quantum agentic firewall** that routes, filters, and cryptographically signs all tool-use by autonomous AI agents. The human operator needs a **world-class "Single Pane of Glass" (SPOG)** to:

1. **See everything at a glance**: Agent health, policy verdicts, transit traffic from external agents, forensic alerts — all in one persistent view.
2. **Act instantly**: Hot-swap policies (<100ms), override agent decisions, pause/resume agents — with zero restart latency.
3. **Trust the data**: Every event displayed must show its PQC verification status. The interface is the cryptographic proof surface.
4. **Scale with new agents**: The UI must auto-discover and present new agents without code changes. The current agent roster (sentinel, engineer, guardian, pathogen, herald, scout, auditor, chronicle, healer, sentry, synthesizer, administrator) will grow.
5. **Monitor transit traffic**: External agents that connect through the firewall generate "transit" events that must be visually distinct from internal agent activity.

**Reference Design**: `feedback/CLAUDE_UI_UX_DESIGN_03_27.md` — the canonical SPOG design specification.
**Architecture**: `docs/INTERFACES.md` — the living architecture document (must stay synchronized).

---

## 📋 Ground Rules for the Implementing Agent

> [!CAUTION]
> **MANDATORY PROTOCOL — READ BEFORE EVERY TASK**
> 1. **Architecture Sync**: Read `docs/INTERFACES.md` before starting any UX task. Follow its Design Principles (§2).
> 2. **Forensic First**: Every user-facing change must have a corresponding test in `tests/integration/test_interfaces.py` and a signed ADR in `docs/adr/`.
> 3. **UX-001 Protocol**: Follow `.agent/rules/UX-001.md` (Pre-Implementation Ritual → TDAD Loop → Post-Implementation Alignment).
> 4. **State Integrity**: After completing a task, update `docs/INTERFACES.md` §3 (Component Audit) to reflect the new state.
> 5. **Extensibility Mandate**: Agent-facing UI components MUST use `AgentRegistry.list_plugins()` for dynamic discovery — never hardcode agent lists.
> 6. **Transit Traffic Mandate**: The PEP layer routes external agent requests. Any dashboard showing traffic MUST distinguish `internal` vs `transit` origin.
> 7. **Commit Discipline**: One task per commit. Format: `feat(interface): <summary> [INT-<N>]`.
> 8. **SYNC_LOG Update**: After each task, add a detailed entry to `SYNC_LOG.md` using the Handoff Protocol at the bottom of this file.
> 9. **Re-sign**: Run `python3 scripts/forensics/resign_docs.py` after every document modification.
> 10. **Push**: `PAGER=cat MANPAGER=cat git push origin main` after every commit.

---

## 🏗️ Current Codebase Inventory (What Exists Today)

Understanding what you're building on top of:

| Component | Path | Status |
|-----------|------|--------|
| **CLI (`tt`)** | `tachyon/cli/main.py` | ✅ Functional. Typer-based. Commands: `ritual`, `dash`, `status`, `airlock`, `immune`, `keys`, `agent`. |
| **TUI (`TachyonDash`)** | `tachyon/cli/tui/app.py` | ⚠️ Scaffold. 4-pane Static grid. No interactivity. Polls `/api/v1` every 2s. Offline fallback via `StateManager`. |
| **API Server** | `tachyon/api/server.py` | ✅ FastAPI + WebSocket (`/api/v1/logs/stream`). Port 60461. |
| **API Routes** | `tachyon/api/routes.py` | ✅ Endpoints: `/status`, `/agents`, `/airlock`, `/forensics`, `/action`. |
| **StateBridge** | `tachyon/core/state_bridge.py` | ⚠️ Functional but `get_agents()` hardcodes 4 roles. Must use `AgentRegistry`. |
| **EventBus** | `tachyon/core/bus.py` | ✅ SQLite-WAL pub/sub. Topics, signatures, certificate validation. |
| **TelemetryBus** | `tachyon/core/telemetry.py` | ✅ JSONL + ForensicStore dual-write. `emit_event()` / `get_events()`. |
| **ForensicStore** | `tachyon/core/forensics.py` | ✅ PQC-signed SQLite ledger. `log_event()` / `query_latest()` / `verify_ledger_integrity()`. |
| **PEP Layer** | `tachyon/api/pep.py` | ✅ Policy enforcement for tool actions (safe_fetch, PROPOSE_PATCH, etc.). |
| **API Schemas** | `tachyon/api/schema.py` | ⚠️ Pydantic models exist but `ToolRequest.parameters` has `Dict[str, Any]` (missing import). |
| **Web Dashboard** | `dashboard/src/App.tsx` | ⚠️ React+Vite scaffold. Not yet wired to live API. |
| **Agent Registry** | `agents/_core/registry.py` | ✅ Dynamic plugin discovery from `agents/` directory. |
| **Ghostty Config** | `docs/ghostty.conf` | ✅ Terminal color/font optimization. |

---

## 🔳- **Phase 1: Foundation & Data Layer** (COMPLETE)
## 🖥️- **Phase 2: TUI Dashboard (Rich Experience)** (COMPLETE)
## 🌐- **Phase 3: Remote Access & Signed Relay** (COMPLETE)

### [INT-01] StateBridge: Dynamic Agent Discovery [x]
- **Goal**: Replace hardcoded agent list in `StateBridge.get_agents()` with dynamic discovery via `AgentRegistry`.
- **Why**: The current implementation hardcodes `["sentinel", "engineer", "guardian", "canary"]` which is stale (12+ agents exist). Every new agent added would require a code change.
- **Files to Modify**:
  - `tachyon/core/state_bridge.py`: Refactor `get_agents()` to use `AgentRegistry.discover_plugins()` + `AgentRegistry.list_plugins()`.
  - `tachyon/api/schema.py`: Fix `Dict[str, Any]` import error (add `from typing import Any`).
- **Implementation Notes**:
  - `AgentRegistry` lives at `agents/_core/registry.py`. Call `AgentRegistry.discover_plugins(agents_dir)` then `AgentRegistry.list_plugins()`.
  - The `agents/` directory contains: administrator, auditor, chronicle, engineer, guardian, healer, herald, pathogen, scout, sentinel, sentry, synthesizer.
  - Each agent plugin has a `SKILL.md` in its directory.
- **Acceptance Tests**:
  - [x] `test_statebridge_dynamic_agents`: Assert `StateBridge.get_agents()` returns ≥10 agents (not 4).
  - [x] `test_statebridge_new_agent_visibility`: Create a mock agent directory, verify it appears in `get_agents()`.
  - [x] `test_schema_import_integrity`: Assert `ToolRequest` can be instantiated without `ImportError`.
- **ADR**: ADR-0068: Dynamic Agent Discovery in StateBridge.
| INT-01 | Dynamic Agent Discovery | COMPLETE | StateBridge uses AgentRegistry |
| INT-02 | Transit Traffic Identification | COMPLETE | `source` field in Forensics/DB |
| INT-03 | API: WebSocket Event Stream | COMPLETE | Background broadcaster in server.py |
| INT-04 | API: Agent Heartbeat | COMPLETE | `/api/v1/agents/{name}/health` |
| INT-05 | API: Traffic Summary | COMPLETE | `/api/v1/traffic/summary` |
| --- | --- | --- | --- |
| INT-06 | Base TUI Layout | COMPLETE | Quad-pane grid in `tui/app.py` |
| INT-07 | Real-Time Herald Alert List | COMPLETE | Infinite scroll logging |
| INT-08 | Transit Visibility Widget | COMPLETE | Red `[T]` badges for external traffic |
| INT-10 | Secure Command Shell | COMPLETE | Integrated Input bar at dashboard bottom |

### [INT-02] Transit Traffic: External Agent Identification [x]
- **Goal**: Add a `source` field (`internal` | `transit`) to telemetry and forensic events so the UI can visually distinguish local agent activity from external agent requests routed through the firewall.
- **Why**: When Tachyon Tongs filters traffic from external AI agents, the operator must immediately see which traffic is "theirs" vs. which is passing through.
- **Files to Modify**:
  - `tachyon/api/schema.py`: Add `source: str = "internal"` to `ForensicAlert` and `LogEntry` models.
  - `tachyon/core/telemetry.py`: Add `source` parameter to `emit_event()`.
  - `tachyon/core/forensics.py`: Add `source` column to `forensic_log` table schema.
  - `tachyon/api/pep.py`: Tag requests from external tenants with `source="transit"` using `tenant_id`.
- **Implementation Notes**:
  - `ToolRequest` already has `tenant_id: Optional[str] = "default"`. If `tenant_id != "default"`, the event should be tagged `source="transit"`.
  - The `ForensicStore.log_event()` and `TelemetryBus.emit_event()` both need the new `source` parameter.
  - Database migration: Use `ALTER TABLE forensic_log ADD COLUMN source TEXT DEFAULT 'internal'` with a try/except for idempotency.
- **Acceptance Tests**:
  - [ ] `test_transit_tagging`: Submit a `ToolRequest` with `tenant_id="external-agent-001"` and verify the forensic event has `source="transit"`.
  - [ ] `test_internal_default`: Submit a `ToolRequest` with default `tenant_id` and verify `source="internal"`.
  - [ ] `test_forensic_store_source_column`: Query `forensic_log` table and verify `source` column exists.
- **ADR**: ADR-0069: Transit Traffic Identification Protocol.

### [INT-03] API: WebSocket Real-Time Event Stream [ ]
- **Goal**: Replace the empty WebSocket heartbeat loop in `server.py` with a real event stream that pushes `TelemetryBus` events to connected clients.
- **Why**: The current `/api/v1/logs/stream` WebSocket does nothing (just `asyncio.sleep(1)`). The TUI and web dashboard both need real-time push.
- **Files to Modify**:
  - `tachyon/api/server.py`: Implement event polling from `TelemetryBus.get_events()` with cursor tracking.
  - `tachyon/core/telemetry.py`: Add `get_events_after(last_id: int)` for incremental polling.
- **Implementation Notes**:
  - Use a polling interval of 500ms. Track `last_seen_id` per WebSocket connection.
  - Each broadcast message should include the event's `source` field (from INT-02).
  - The `ConnectionManager` class already handles multiple WebSocket connections and broadcasting.
- **Acceptance Tests**:
  - [ ] `test_websocket_event_delivery`: Connect a test WebSocket client, emit a telemetry event, verify it arrives within 2 seconds.
  - [ ] `test_websocket_cursor_tracking`: Emit 3 events, connect late, verify only new events are received.
- **ADR**: Not required (incremental improvement to existing endpoint).

### [INT-04] API: Agent Heartbeat & Health Endpoint [ ]
- **Goal**: Add a `/api/v1/agents/{name}/health` endpoint that returns per-agent health metrics (last heartbeat, CPU/memory if available, last action timestamp).
- **Why**: The TUI's "Agent Heartbeat" pane needs per-agent drill-down data beyond the flat list.
- **Files to Modify**:
  - `tachyon/api/routes.py`: Add new route.
  - `tachyon/core/state_bridge.py`: Add `get_agent_health(name: str)` method.
  - `tachyon/api/schema.py`: Add `AgentHealth` Pydantic model.
- **Implementation Notes**:
  - Query `forensic_log` for the agent's last event timestamp. Use `TelemetryBus.get_events()` filtered by `agent_id`.
  - CPU/Memory can return 0.0 for now (real monitoring is a future task).
- **Acceptance Tests**:
  - [ ] `test_agent_health_endpoint`: GET `/api/v1/agents/sentinel/health` returns valid `AgentHealth` JSON.
  - [ ] `test_agent_health_unknown`: GET `/api/v1/agents/nonexistent/health` returns 404.
- **ADR**: Not required.

### [INT-05] API: Transit Traffic Summary Endpoint [x]
- **Goal**: Add `/api/v1/traffic/summary` endpoint returning verdict distribution (ALLOW/DENY/ERROR counts) and per-source breakdown (internal vs transit).
- **Why**: The TUI's "Policy Enforcement Metrics" pane needs this aggregated data.
- **Files to Modify**:
  - `tachyon/api/routes.py`: Add new route.
  - `tachyon/core/state_bridge.py`: Add `get_traffic_summary()` method.
  - `tachyon/api/schema.py`: Add `TrafficSummary` Pydantic model.
- **Implementation Notes**:
  - Query `forensic_log` with `GROUP BY status, source` for the last 60 seconds.
  - Return structure: `{ "total": N, "allow": N, "deny": N, "error": N, "internal": N, "transit": N }`.
- **Acceptance Tests**:
  - [ ] `test_traffic_summary_endpoint`: Seed 10 events (mix of internal/transit, allow/deny), verify summary counts.
  - [ ] `test_traffic_summary_empty`: Verify endpoint returns zeros when no events exist.
- **ADR**: Not required.

---

## 🖥️ Phase 2: TUI Dashboard (Read-Only SPOG) [INT-10 through INT-15]

_Goal: Transform the scaffold `TachyonDash` into a production-quality, 4-pane monitoring dashboard._

**Reference**: `feedback/CLAUDE_UI_UX_DESIGN_03_27.md` §2.1 (Quad-Pane Master View).

### [INT-10] TUI: Quad-Pane Layout with Textual Widgets [x]
- **Goal**: Replace the 4 `Static` widgets with proper Textual `Widget` subclasses that support rich rendering, scrolling, and focus.
- **Why**: `Static` widgets cannot scroll, accept focus, or handle click events. Every pane needs to be interactive.
- **Files to Modify**:
  - `tachyon/cli/tui/app.py`: Complete rewrite of `compose()` and data refresh.
  - `tachyon/cli/tui/widgets/` [NEW]: Create widget subclasses.
- **Implementation Notes**:
  - Create a `tachyon/cli/tui/widgets/` package with:
    - `overview.py`: `TacticalOverview(Widget)` — Status bar, health, PQC status, Merkle root. Color: green=healthy, yellow=degraded, red=compromised.
    - `agents.py`: `AgentHeartbeat(Widget)` — Scrollable list of agents with status bars (use Rich progress bars). Must use `AgentRegistry` data (from INT-01).
    - `alerts.py`: `AlertStream(Widget)` — Auto-scrolling, filterable event feed. Color HIGH=red, MEDIUM=yellow, INFO=dim. Mark `transit` events with a `[T]` prefix badge.
    - `metrics.py`: `PolicyMetrics(Widget)` — Verdict distribution (text-based bar chart), request rate, latency stats.
  - The main app CSS should use Textual's grid layout: `grid-size: 2 2;` with proper `height: 1fr` for responsive sizing.
  - Use the SPOG design's color scheme: background `#0a0e14`, borders `#82aaff`, alerts `#f07178`.
- **Acceptance Tests**:
  - [ ] `test_tui_has_four_panes`: Assert `TachyonDash` has exactly 4 widget panes (overview, agents, alerts, metrics).
  - [ ] `test_tui_widget_types`: Assert each pane is a proper `Widget` subclass, not `Static`.
  - [ ] `test_tui_css_grid`: Assert the CSS includes `grid-size: 2 2`.
- **ADR**: ADR-0070: TUI Widget Architecture.

### [INT-11] TUI: Header Bar with Ambient Status [x]
- **Goal**: Add a persistent header showing: version, daemon status (OPERATIONAL/OFFLINE), Merkle root hash, PQC verification status, and governance mode (HITL/HOTL/HOOTL).
- **Why**: This is the "Ambient Awareness" principle — critical state must be visible without interaction.
- **Files to Modify**:
  - `tachyon/cli/tui/widgets/header.py` [NEW]: `SubstrateHeader(Widget)`.
  - `tachyon/cli/tui/app.py`: Replace `Header()` with `SubstrateHeader()`.
- **Implementation Notes**:
  - Reference: `feedback/CLAUDE_UI_UX_DESIGN_03_27.md` line 76: `⏰ 14:23:17 UTC | 📡 Daemon: OPERATIONAL | 🔐 Merkle: 8a3f4b2e | 🔑 PQC: ✓`
  - Update every 2 seconds via the same refresh cycle.
  - Show the first 8 chars of the Merkle root for compactness.
- **Acceptance Tests**:
  - [ ] `test_header_shows_pqc_status`: Assert the header widget contains "PQC" text.
  - [ ] `test_header_shows_daemon_status`: Assert header contains "OPERATIONAL" or "OFFLINE".
- **ADR**: Not required.

### [INT-12] TUI: Agent Heartbeat Pane (Dynamic) [x]
- **Goal**: The agent heartbeat pane must dynamically list all registered agents with their health status, using data from the INT-01 dynamic discovery.
- **Why**: Operators need to see at-a-glance which agents are healthy, degraded, or crashed — and this list must grow automatically.
- **Files to Modify**:
  - `tachyon/cli/tui/widgets/agents.py` [NEW or from INT-10].
- **Implementation Notes**:
  - Use Rich `ProgressBar` widgets for each agent's "load" indicator.
  - Color: Green (RUNNING), Yellow (IDLE), Red (CRASHED/STOPPED).
  - Each agent row should be clickable (future: drill into Agent Control Panel, INT-20+).
  - Show agent count: "📊 AGENT HEARTBEAT (12)".
- **Acceptance Tests**:
  - [ ] `test_heartbeat_shows_all_agents`: Assert ≥10 agent names are rendered.
  - [ ] `test_heartbeat_color_coding`: Assert RUNNING agents get green styling.
- **ADR**: Not required.

### [INT-13] TUI: Alert Stream with Transit Badges [x]
- **Goal**: The forensic feed pane must show a live, auto-scrolling stream of events with severity coloring AND transit badges.
- **Why**: The operator must instantly distinguish "our agents did this" from "an external agent triggered this through the firewall."
- **Files to Modify**:
  - `tachyon/cli/tui/widgets/alerts.py` [NEW or from INT-10].
- **Implementation Notes**:
  - Auto-scroll to bottom on new events. Add a SPACE keybinding to pause/resume auto-scroll.
  - Severity coloring: CRITICAL/HIGH = bold red, MEDIUM = yellow, INFO = dim white.
  - Transit badge: prefix external events with `[T]` in cyan. Internal events have no prefix.
  - Show timestamp, severity, short message. Truncate long messages with "…".
  - Maximum render: last 100 events (configurable).
- **Acceptance Tests**:
  - [ ] `test_alert_stream_transit_badge`: Emit a transit event, verify `[T]` prefix appears.
  - [ ] `test_alert_stream_severity_colors`: Emit HIGH and INFO events, verify different styling.
  - [ ] `test_alert_stream_auto_scroll`: Emit 50 events, verify the last event is visible.
- **ADR**: Not required.

### [INT-14] TUI: Policy Metrics Pane [x]
- **Goal**: Display aggregated policy enforcement metrics: verdict distribution, request rate, top blocked actions.
- **Why**: The operator needs to see if the firewall is behaving normally or experiencing a spike in denials.
- **Files to Modify**:
  - `tachyon/cli/tui/widgets/metrics.py` [NEW or from INT-10].
- **Implementation Notes**:
  - Use the `/api/v1/traffic/summary` endpoint (from INT-05).
  - Render verdict distribution as a text-based horizontal bar: `████████░░ ALLOW 82%`.
  - Show transit vs internal split: `Internal: 86% | Transit: 14%`.
  - If no data, show "No traffic data yet" in dim text.
- **Acceptance Tests**:
  - [ ] `test_metrics_pane_renders`: Assert the metrics widget renders without error.
  - [ ] `test_metrics_shows_verdict_distribution`: With seeded data, verify ALLOW/DENY percentages appear.
- **ADR**: Not required.

### [INT-15] TUI: Hotkey Navigation & Command Bar [x]
- **Goal**: Implement keyboard navigation: Tab to cycle panes, `q` to quit, `r` to refresh, `/` to search, `` ` `` to toggle command bar.
- **Why**: Terminal operators expect keyboard-first interaction. Mouse is secondary.
- **Files to Modify**:
  - `tachyon/cli/tui/app.py`: Add `BINDINGS` and key handlers.
  - `tachyon/cli/tui/widgets/command_bar.py` [NEW]: `CommandBar(Widget)` with autocomplete.
- **Implementation Notes**:
  - Reference: `feedback/CLAUDE_UI_UX_DESIGN_03_27.md` §2.3 (Navigation Model).
  - Hotkeys: `1`=Dashboard, `2`=Forensic Timeline (future), `3`=Policy Editor (future), `q`=Quit, `r`=Refresh, `Space`=Pause alerts.
  - Command bar: simple text input at the bottom. Typing `tt airlock approve CVE-2026-9999` should work.
  - Use Textual's built-in `Input` widget for the command bar.
- **Acceptance Tests**:
  - [ ] `test_hotkey_quit`: Simulate `q` keypress, verify app exits cleanly.
  - [ ] `test_hotkey_refresh`: Simulate `r` keypress, verify data refresh is triggered.
  - [ ] `test_command_bar_toggle`: Simulate `` ` `` keypress, verify command bar appears/hides.
- **ADR**: Not required.

---

## 🌐 Phase 3: Remote Access & CLI Enhancements [INT-20 through INT-23]

_Goal: Enable secure remote interaction and improve CLI observability._

### [INT-20] CLI: `tt bus explore` — EventBus Browser [x]
- **Goal**: Add a `tt bus explore` command that displays recent EventBus events in a Rich table with JSONL pagination.
- **Why**: Operators need a quick CLI way to inspect the event stream without launching the full TUI.
- **Files to Modify**:
  - `tachyon/cli/main.py`: Add `bus` command group with `explore` subcommand.
  - `tachyon/core/bus.py`: Add `fetch_recent(limit)` method.
- **Implementation Notes**:
  - Display columns: ID, Timestamp, Topic, Agent, Status, Source (internal/transit).
  - Use Rich `Table` with pagination (default 20 events, `--limit N` flag).
  - Color `transit` rows in cyan, `internal` rows in default white.
- **Acceptance Tests**:
  - [ ] `test_bus_explore_command`: Invoke `tt bus explore --limit 5` and verify tabular output.
  - [ ] `test_bus_explore_empty`: Verify graceful "No events" message when bus is empty.
- **ADR**: Not required.

### [INT-21] CLI: `tt traffic` — Transit Traffic Inspector [x]
- **Goal**: Add a `tt traffic` command showing real-time transit traffic summary and recent external agent requests.
- **Why**: Operators need to quickly assess firewall throughput and what external agents are doing.
- **Files to Modify**:
  - `tachyon/cli/main.py`: Add `traffic` command.
- **Implementation Notes**:
  - Show: total requests (last 60s), verdict breakdown, top 5 blocked external agents.
  - Use Rich `Table` + `Panel`.
- **Acceptance Tests**:
  - [ ] `test_traffic_command_output`: Verify the command produces structured output.
- **ADR**: Not required.

### [INT-22] Remote Access: Signed Command Relay [x]
- **Goal**: Implement the signed command relay protocol defined in ADR-0067.
- **Why**: Remote operators must be able to issue commands with cryptographic non-repudiation.
- **Files to Modify**:
  - `tachyon/api/routes.py`: Add `/api/v1/relay` endpoint.
  - `tachyon/api/schema.py`: Add `SignedCommand` model (nonce, certificate, payload, hybrid_signature).
  - `tachyon/core/state_bridge.py`: Add `execute_signed_command()` with nonce validation.
- **Implementation Notes**:
  - Reference: `docs/adr/0067-signed-remote-access.md`.
  - Nonce must be monotonically increasing (store last-seen nonce in `forensics.db`).
  - Verify hybrid signature (Ed25519 + ML-DSA-65) before execution.
  - Log every relay attempt (success or failure) to `ForensicStore`.
- **Acceptance Tests**:
  - [ ] `test_signed_relay_valid`: Submit a properly signed command, verify execution.
  - [ ] `test_signed_relay_replay`: Reuse a nonce, verify DENY with "REPLAY_DETECTED" error.
  - [ ] `test_signed_relay_forged`: Submit with invalid signature, verify DENY.
- **ADR**: ADR-0067 already exists.

### [INT-23] Remote Access: WebSocket Authentication [x]
- **Goal**: Add certificate-based authentication to the `/api/v1/logs/stream` WebSocket endpoint.
- **Why**: Unauthenticated WebSocket connections are a security risk.
- **Files to Modify**:
  - `tachyon/api/server.py`: Add certificate validation on WebSocket connect.
- **Implementation Notes**:
  - Client sends a signed handshake message on connect. Server validates signature before accepting.
  - Invalid handshakes get disconnected immediately with a 4403 close code.
- **Acceptance Tests**:
  - [ ] `test_websocket_auth_valid`: Connect with valid certificate, verify accepted.
  - [ ] `test_websocket_auth_invalid`: Connect without certificate, verify rejected (4403).
- **ADR**: ADR-0071: WebSocket Authentication Protocol.

---

## 🧪 Phase 4: Verification & Hardening [INT-30 through INT-33]

### [INT-30] Stress Test: TUI Under High Event Load [x]
- **Goal**: Saturate the EventBus with 1000 events/sec and verify TUI stability (no crashes, no memory leaks, render latency <16ms).
- **Acceptance Tests**:
  - [ ] `test_tui_stress_1000_eps`: Emit 1000 events in 1 second, verify TUI does not crash and memory stays <100MB.

### [INT-31] Security: Negative Auth Tests [x]
- **Goal**: Comprehensive negative testing of all authenticated endpoints.
- **Acceptance Tests**:
  - [ ] `test_relay_expired_certificate`: Verify expired certificates are rejected.
  - [ ] `test_relay_revoked_certificate`: Verify revoked certificates (in CRL) are rejected.

### [INT-32] Accessibility: Colorblind-Safe Palette [x]
- **Goal**: Ensure all severity indicators are distinguishable without relying solely on red/green color.
- **Implementation Notes**:
  - Add text labels alongside colors: `✓ OK`, `⚠ WARN`, `✗ FAIL`.
  - Use shapes/icons as secondary indicators.
- **Acceptance Tests**:
  - [ ] `test_accessibility_labels`: Verify all status indicators have text labels, not just colors.

### [INT-33] Documentation: Full INTERFACES.md Sync [x]
- **Goal**: After all phases are complete, perform a comprehensive audit of `docs/INTERFACES.md` to ensure it perfectly reflects the implemented state.
- **Acceptance Tests**:
  - [ ] `test_interfaces_md_component_count`: Parse `docs/INTERFACES.md` and verify the component table has ≥8 rows (matching actual file count).

---

## ✅ Final Verification Checklist

After all Interface tasks are resolved, run the following sequence:

```bash
# 1. Full interface integration tests
pytest -v tests/integration/test_interfaces.py

# 2. Forensic re-signing
python3 scripts/forensics/resign_docs.py

# 3. Final Push
PAGER=cat MANPAGER=cat git add .
PAGER=cat MANPAGER=cat git commit -m "feat: interface stabilization phase complete"
PAGER=cat MANPAGER=cat git push origin main
```

---

## 📝 SYNC_LOG Handoff Protocol for Agentic Models

> [!IMPORTANT]
> When updating `SYNC_LOG.md`, use the following structure for **each task completed**.

### Required Detail Level per SYNC_LOG Entry:
```markdown
### YYYY-MM-DD: Task INT-XX Completion
- **Objective**: One-line summary of the interface enhancement.
- **Status**: [COMPLETE]
- **Tasks Completed**:
  - **[INT-XX] Title**: Summary of the implementation.
    - **Files Modified**: List all source and test files changed.
    - **Files Created**: List all new files.
    - **Test Added**: Exact test file path and test function name.
    - **Test Result**: `PASS` or `FAIL` with pytest summary.
- **Regression Status**: Full `pytest tests/integration/test_interfaces.py` summary line.
- **ADR Created**: ADR number and title (or "N/A").
- **docs/INTERFACES.md Updated**: Yes/No — describe what was updated.
```

### Commit Message Format:
```
feat(interface): <one-line summary> [INT-<N>]
```
