# Human-Substrate Interface Architecture (HSI)

This document establishes the official architectural layers, components, and forensic presentation channels for human interaction with the **Tachyon Tongs** security substrate.

---

## 🏗️ 1. The Multi-Tier Interface Model

The Tachyon Substrate utilizes a three-layer interaction model to balance direct control, operational visibility, and remote accessibility.

### 🟢 Layer 1: CLI (Direct Command Plane)
The **CLI** is the primary entry point for low-latency engineering tasks and cryptographic governance. It is designed for POSIX-compliant terminal environments and follows the "Fail-Loud" principle.
- **Entry Point**: `python3 -m tachyon.main` (aliased as `tt`)
- **Primary Roles**: Key management (`keys`), Agent recruitment (`sentinel`, `engineer`, etc.), and forensic auditing.

### 🔵 Layer 2: TUI (Operational Dashboard)
The **TUI** (Textual User Interface) provides a persistent, high-fidelity view of the substrate's internal state. It is used for real-time monitoring of PQC coverage, alignment drift, and the EventBus stream.
- **Component**: `TachyonDash`
- **Engine**: [Textual](https://github.com/Textualize/textual)
- **Deployment**: Integrated directly into the `tt dash` command.

### 🟡 Layer 3: StateBridge (Remote API & Bridge)
The **StateBridge** enables external visibility and remote command relay. It acts as a post-quantum encrypted gateway between the local substrate and remote dashboards or HITL (Human-In-The-Loop) interfaces.
- **Protocol**: FastAPI (REST) + WebSockets (Real-time).
- **Security**: Mandatory hybrid signature verification for all inbound commands.

---

## 🎨 2. Design Principles (SPOG Architecture)

To establish a "Single Pane of Glass" (SPOG) management interface, all interface components must adhere to the following fundamental principles:

1.  **Ambient Awareness**: Critical information (health, alerts, PQC status) must be visible at a glance without requiring user interaction.
2.  **Progressive Disclosure**: Detailed information should be available on-demand (e.g., clicking an alert or agent node) without cluttering the primary operational views.
3.  **Zero-Latency Control**: High-risk actions, such as policy hot-swapping and agent action overrides, must be implemented with a latency target of **<100ms**.
4.  **Forensic Completeness**: Every manual and automated interaction via any interface tier must be traceable, auditable, and cryptographically anchored in `forensics.db`.
5.  **Multi-Modal Interaction**: Interaction models must prioritize keyboard-first workflows (TUI/CLI) while maintaining secondary accessibility for mouse/web-based stakeholders.

---

## 🔍 3. Interface Component Audit (2026-03-27)

The following files constitute the primary implementation of the HSI:

| Component | Path | Description |
|-----------|------|-------------|
| **CLI Loader** | `tachyon/main.py` | Unified argparse entry point for all agent roles and key operations. |
| **TUI App** | `tachyon/cli/tui/app.py` | Implementation of the `TachyonDash` using the Textual framework. |
| **Bridge Server** | `tachyon/api/server.py` | FastAPI/Uvicorn host for the StateBridge API. |
| **Bridge Routes** | `tachyon/api/routes.py` | Endpoint definitions for forensics and telemetry. |
| **Terminal Config** | `docs/ghostty.conf` | Optimization for the Ghostty terminal (color palettes, font rendering). |

---

## 🛡️ 3. Forensic File Presentation

The substrate presents "Human-Readable Forensic Records" to ensure that the operator (and external auditors) can reconstruct the project's state without specialized tools.

### 🔴 ALERT.md (High-Signal Alerts)
A "Loud" append-only log located in the root directory. It contains critical security events (Intrusion Detection, Integrity Failures, Daemon Crashes) that require immediate human intervention.

### 🔄 SYNC_LOG.md (The Engineering Pulse)
A session-level engineering audit log. Every achievement, architectural decision, and implementation detail is recorded here and anchored to a specific timestamp and git commit.

### 🔲 TASKS_*.md (The Master Records)
Phased master task lists (`BOOTSTRAP`, `CLEANUP`, `ENHANCEMENTS`, `INTERFACES`). These files are the **ground truth** for the project's roadmap and engineering backlog.

### 📊 forensics.db (Structured Audit Ledger)
A high-assurance SQLite database containing the formal record of all `ActionRecord` objects, `DelegationCertificates`, and `TelemetryEvents`.

---

## ✅ 4. Integrity Mandate

Every interface component MUST:
1.  **Display Cryptographic Status**: All presented events must indicate if they were PQC-verified.
2.  **Enforce Default-Deny**: Any command received via the StateBridge without a valid hybrid signature must be rejected.
3.  **Log to the Ledger**: All human-initiated actions via any tier must be recorded in `forensics.db`.

> [!IMPORTANT]
> **AUDIT NOTE**: This document is cryptographically anchored to the substrate's Root of Trust and must be re-signed after any structural modification.
