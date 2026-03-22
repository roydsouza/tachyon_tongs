# 📣 The Herald Agent

The **Herald Agent** operates as the communication aggregator and deterministic command router for Tachyon Tongs. It is defined as a `CustomAgent` (or Specialist) that handles all bidirectional interactions between the human operator and the agentic collective.

## 🎯 Role Designation: The Mouth & Ear

While the Firewall Administrator acts as the "Thinker", the Herald focuses purely on high-fidelity I/O. It is not an LLM agent; rather, its value lies in complex, deterministic state management for various user interfaces.

### Core Responsibilities
1. **Bidirectional Communication Bridge:** Forwards alerts, debates, and summaries from local agents to the operator's remote device.
2. **Command Parsing & Routing:** Parses natural language or slash commends (`/status`, `/airlock list`) and routes them to the appropriate subsystem.
3. **Notification Aggregation:** Formats complex system state information into semantic, human-readable UI views.
4. **Transport Agnosticism:** Provides interfaces independent of the transport layer, effectively wrapping CLI, NeoVIM floating windows, Textual TUIs, and external services like Slack/Signal.

## ⚙️ Deterministic Execution (CustomAgent)

Because the Herald must manage strict protocols and UI state machines without hallucination, it inherits from `BaseAgent` and completely overrides the `_run_async_impl` method.

- **Non-Cognitive Loop:** Replaces LLM-based reasoning with direct Python control flow and socket management.
- **AgentTool Availability:** The Herald exposes itself as an `AgentTool` to the Firewall Administrator, allowing the Administrator to "think" its way to a decision and then explicitly call the Herald to "dispatch a Signal alert" or "update the TUI."

## 🔌 Integration Points

The Herald serves as the backbone for the **Event-Horizon Command Bridge**:
- **NeoVIM Integration (`tachyon.nvim`)**: Streams structured state back to the semantic UI buffers.
- **Textual Dashboard (`tt dash`)**: Feeds the real-time manifolds over Unix domain sockets or async queues.
- **Slack / Signal / External Transports**: Routes critical threshold alerts to remote operator mobile devices.

*For details on the Event-Horizon Command Bridge, see [ARCHITECTURE.md](ARCHITECTURE.md).*
