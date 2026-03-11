# Tachyon Tongs: System Architecture Deep Dive

This document details the technical architecture of the **Tachyon Tongs** security substrate. It explains the core routing daemon, the implementation details of the defensive prophylactic layer, and the anatomy of the internal agent abstractions.

## 1. High-Level Component Topology

Tachyon Tongs operates as a client-server architecture running entirely on `localhost`. The core component is the **Substrate Daemon** (`substrate_daemon.py`), which acts as an intercepting proxy and security bouncer for all registered agents.

```text
[External Internet / Data Sources]
      │
      ▼
┌───────────────────────────────────────────────┐
│ TACHYON TONGS SUBSTRATE DAEMON (Port 8443)    │
│                                             │
│  ┌────────────────────────┐                 │
│  │ 1. Client Identity     │◄── (Tenant ID)  │
│  └───────────┬────────────┘                 │
│              │                              │
│  ┌───────────▼────────────┐                 │
│  │ 2. Semantic Intent Gate│◄── (OPA .rego)  │
│  └───────────┬────────────┘                 │
│              │                              │
│  ┌───────────▼────────────┐                 │
│  │ 3. Tool Dispatcher     │                 │
│  └─┬────────────────────┬─┘                 │
│    │                    │                   │
└────┼────────────────────┼───────────────────┘
     │ (Network Fetch)    │ (Code Execution)
┌────▼─────────────┐ ┌────▼───────────────────┐
│  Guardian Triad  │ │  Tier 0 MacOS Sandbox  │
│  (Air-Gapped)    │ │  (Seatbelt Profiles)   │
└────┬─────────────┘ └────┬───────────────────┘
     │                    │
┌────▼────────────────────▼───────────────────┐
│ TACHYON CLIENT (e.g. `tachyon_client.py`)   │
│ (In-Band or Out-Of-Band Agent)              │
└─────────────────────────────────────────────┘
```

### The Sentinel Payload Topology
This explicitly maps how the Sentinel (Blue Team) aggregates and sanitizes its data using the Triad before writing to the structural logs.

```text
[The Internet]
      │
      ▼
┌───────────────────────────────────────────────┐
│ THE PROPHYLACTIC LAYER (Infrastructure)     │
│                                             │
│  ┌───────────▼────────────┐                 │
│  │ L1: Intent Gate (OPA)  │                 │
│  └───────────┬────────────┘                 │
│              │                              │
│  ┌───────────▼────────────┐                 │
│  │ L2: Capability Firewall│                 │
│  └───────────┬────────────┘                 │
│              │                              │
└──────────────┼────────────────────────────────┘
               │ (Strictly Controlled IO)
┌──────────────▼────────────────────────────────┐
│ THE PAYLOAD DOMAIN (Sentinel)               │
│                                             │
│  ┌──────────────┐     ┌────────────────┐    │
│  │ Fetcher VM   ├────►│ Sanitizer Node │    │
│  │ (Network OK) │     │ (Regex/Parse)  │    │
│  └──────────────┘     └───────┬────────┘    │
│                               │             │
│                       ┌───────▼────────┐    │
│                       │ Analyzer VM    │    │
│                       │ (Air-Gapped)   │    │
│                       └───────┬────────┘    │
│                               │             │
│                       ┌───────▼────────┐    │
│                       │ Verifier Node  │    │
│                       │ (Output Check) │    │
│                       └───────┬────────┘    │
│                               │             │
└───────────────────────────────┼───────────────┘
                                ▼
          [Updates to SITES, EXPLOITATION_CATALOG, TASKS]
```

## 2. Defensive Abstractions

### A. Semantic Intent Gating (Open Policy Agent)
Every action requested by an agent client (via HTTP POST to the Substrate Daemon) must carry the payload intent and the target domains/parameters. 
Before execution, the Substrate Daemon transforms this request into a JSON structure and queries a side-car Open Policy Agent (OPA) server running `policies/semantic_access.rego`.
*   **Tenant Isolation:** OPA enforces that the agent possesses the capability mapping for the requested tool.
*   **Domain Constraint Gating:** Outbound network requests are structurally validated. Attempting to fetch from untyped IPs or known adversarial sinkholes dynamically fails the OPA evaluation, dropping the request with a hard `BLOCKED` status.

### B. The Guardian Triad (Data Sanitization)
The ingestion of untrusted external web data is the primary vector for indirect prompt injections. Tachyon Tongs handles `safe_fetch` requests using a strictly isolated three-stage pipeline:
1.  **FetcherNode (Scout):** Executes the HTTP request. This node is completely isolated from LLM memory contexts and only retrieves raw DOM data.
2.  **SanitizerNode (Analyst):** Completely air-gapped from network egress. It utilizes regex patterns to strip zero-width steganography (`\u200B`) and executable tags (`<script>`). 
    *   **Metal Acceleration (`mlx_lm`):** The Analyst then wraps the sanitized payload into cryptographic boundaries (`\u0001UNTRUSTED_CONTENT_START\u0002`). It utilizes an Apple-Silicon native 4-bit Llama model loaded directly into Unified Memory to evaluate the payload for subtle instruction-override attacks.
3.  **VerifierNode (Engineer):** Before returning the data to the client, the Engineer verifies the Analyst's output JSON for trailing shell-execution signatures or malicious Markdown downloads, raising Exceptions on contamination.

### C. Tier 0 Workload Isolation (Apple Sandbox)
When an agent requests code execution (`safe_execute`), it is routed to the `AppleSandbox` wrapper block.
*   **Seatbelt/sandbox-exec:** Tachyon Tongs dynamically generates a strict Apple Sandbox profile.
*   **Profile Constraints:** The process is entirely denied `network-outbound` and `network-inbound` sockets. File system access is strictly defaulted to `deny file-write*`, while granting write permissions exclusively to a temporary, randomized workspace directory scoped to the specific execution run.

## 3. Durable Transaction Management

High-concurrency traffic emitted by distributed agents necessitates rigid concurrency controls on the Substrate's intelligence feeds.
*   **SQLite WAL `StateManager`:** All execution tracking (`RUN_LOG`) and threat intelligence discovery (`EXPLOITATION_CATALOG`) are routed through `src/state_manager.py`. The database is configured in Write-Ahead-Log (WAL) mode, guaranteeing atomic, corruption-free insertions.
*   **Materialization:** The SQLite manager transparently triggers Markdown export routines upon each insertion, providing human-readable audits in real-time.

## 4. The Adversarial Co-Evolution Loop (Live Organism)

Tachyon Tongs is designed as an autonomic, self-healing organism rather than a static proxy. 

1.  **Orchestration (`run_pathogen.py`):** Initiated periodically, the Pathogen Red Team loads its `SKILL.md` manifest to acquire its Tenant ID and OPA clearance.
2.  **Code-Patching (The Engineer):** When the Sentinel discovers a new zero-day, it physically writes a Python/Rego patch into the Substrate's source code, tests it, and logs the mutation to `EVOLUTION.md`.
3.  **Adversarial Synthesis (The Pathogen):** The Sentinel dynamically rewrites the Pathogen's `SKILL.md` to hyper-focus on the newly mitigated threat. The Pathogen reads the `EXPLOITATION_CATALOG.md` and generates hallucinated, metamorphic permutations of the payload.
4.  **Assault:** Pathogen attempts to inject the mutated payload into the Substrate's Event Horizon to verify whether the Engineer's autonomous patch successfully drops the threat.

For a detailed breakdown of this self-modifying biological paradigm, see `docs/BEHAVIOR.md`.
