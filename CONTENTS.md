# Tachyon Tongs: Directory of Contents

This document provides a bird's-eye view of all critical documentation, intelligence catalogs, configuration structures, and core scripts within the Tachyon Tongs repository to streamline audit and deployment efforts.

## 1. High-Level Documentation

*   [`README.md`](README.md): The primary whitepaper outlining the problem (AI hijacking), the Tachyon Tongs solution (Tiered Sandbox, Triad Pipeline), protection variants, and macOS Apple Silicon quickstart.
*   [`docs/STRATEGY.md`](docs/STRATEGY.md): Operational thesis focusing on amortized defense and continuous improvement protocols.
*   [`docs/ROADMAP.md`](docs/ROADMAP.md): Systematic progression of the framework architecture and project milestones.
*   [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Deep-dive into the internal control flows, detailing the Guardian Triad, the integration of Open Policy Agent (OPA) `.rego` intent-gating, Apple Native Sandboxing, and `mlx_lm` Meta acceleration.
*   [`docs/COMPETITIVE_ANALYSIS.md`](docs/COMPETITIVE_ANALYSIS.md): Market positioning and actionable analysis against 2026 enterprise competitors (NeMo, PyRIT, MCP integration).
*   [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md): The Builder's Guide. Structural methodologies to configure In-Band (Substrate managed) and Out-of-Band (Independent) agents, including generic manifest templates.
*   [`docs/BEHAVIOR.md`](docs/BEHAVIOR.md): Detailed explanation of the Righteous Evolutionary Cycle, detailing how the Substrate autonomously self-modifies and heals.
*   [`docs/CLIENT_INTEGRATION.md`](docs/CLIENT_INTEGRATION.md): Overview on integrating external agents using `tachyon_client.py`.
*   [`docs/SKILLS_ARCHITECTURE.md`](docs/SKILLS_ARCHITECTURE.md): The declarative agent framework powering the Pathogen simulator.
*   [`docs/HYBRID_AUTH.md`](docs/HYBRID_AUTH.md): The Apple Secure Enclave & FIDO2 integration thesis.
*   [`docs/TAILSCALE.md`](docs/TAILSCALE.md): The roadmap for zero-trust mesh expansion [UPCOMING].
*   [`CONTENTS.md`](CONTENTS.md): This file.

## 2. Intelligence & Auditing Catalogs

## 2. Intelligence & Auditing Catalogs

*   [`EVOLUTION.md`](EVOLUTION.md): The Somatic Ledger. Chronological tracking of autonomous codebase mutations and perimeter expansions.
*   [`EXPLOITATION_CATALOG.md`](EXPLOITATION_CATALOG.md): The Master Ledger. Synthesized threat vectors retrieved by the Sentinel Blue Team and exported automatically by the SQLite `StateManager`.
*   [`docs/zero_day_drills.md`](docs/zero_day_drills.md): The fuzzer metric log. Tracks the continuous resiliency score of the Substrate against novel Pathogen attacks.
*   [`RUN_LOG.md`](RUN_LOG.md): The chronologically appended, multi-tenant cryptographically verified summary of execution actions, bounded by N=25 limits.
*   [`SITES.md`](SITES.md): Formal tracking of globally vetted intelligence destinations (e.g., CISA, GitHub Advisories, NVD API 2.0).
*   [`TASKS.md`](TASKS.md): The active engineering backlog, dynamically mutated by the Sentinel when new threats necessitate human intervention or tracking.

## 3. Core Source Directives (`src/`)

*   **Daemon Orchestration Contexts:**
    *   [`substrate_daemon.py`](src/substrate_daemon.py): The autonomous security proxy server enforcing OPA capabilities and dispatching to secure endpoints.
    *   [`tachyon_client.py`](src/tachyon_client.py): Out-of-Band integration API (e.g., `safe_fetch`).
    *   [`state_manager.py`](src/state_manager.py): SQLite-backed transaction coordinator maintaining durable multi-tenant persistence.
*   **The Guardian Triad Pipeline:**
    *   [`adk_sentinel.py`](src/adk_sentinel.py): The Action Broker and entry point to the air-gapped pipeline.
    *   [`tri_stage_pipeline.py`](src/tri_stage_pipeline.py): The isolated bounds routing payload retrieval, sanitation, and MLX reasoning inference.
*   **Hardware Acceleration:**
    *   [`metal_accelerator.py`](src/metal_accelerator.py): Apple Silicon NPU/GPU binding via `mlx_lm` for localized, rapid reasoning inference.
    *   [`apple_sandbox.py`](src/apple_sandbox.py): Tier 0 workload isolation invoking macOS native `sandbox-exec` Profiles.

## 4. Configuration Manifests (`policies/` & `agents/`)

*   **Security Gating:**
    *   [`policies/semantic_access.rego`](policies/semantic_access.rego): The OPA policy validating tool execution and intent boundaries based on tenant ID and dynamic configuration scopes.
*   **In-Band Agent Manifests:**
    *   [`agents/pathogen/SKILL.md`](agents/pathogen/SKILL.md): The declarative `.md` configuration detailing the capabilities, constraints, and instructions for the Red Team Pathogen simulator.
*   **Daemon Services:**
    *   [`scripts/com.antigravity.tachyon.pathogen.plist`](scripts/com.antigravity.tachyon.pathogen.plist): Local macOS daemon configuration for scheduling active-measuring Red Team payloads.

## 5. Administrative Overlays (`scripts/`)

*   [`scripts/doom_ticker.py`](scripts/doom_ticker.py): Shared utility outputting terminal-style apocalyptic reporting sourced from the intelligence catalogs.
*   [`scripts/start_opa.sh`](scripts/start_opa.sh): Local bootstrapper ensuring the Open Policy Agent port is initialized securely bound to localhost.
*   [`scripts/intel_ingest.py`](scripts/intel_ingest.py): The plugin-driven data ingester routing NVD/GitHub threats into the Triad.
*   [`scripts/run_pathogen.py`](scripts/run_pathogen.py): The orchestration daemon loading Pathogen's `SKILL.md` to initiate the red-team cycle.
*   [`scripts/zero_day_drill.py`](scripts/zero_day_drill.py): The continuous adversarial fuzzer generating and measuring zero-day LLM mutations against the Guardian Triad.
*   [`scripts/tailscale-auth.sh`](scripts/tailscale-auth.sh): Secure node authentication wrapper for generating ephemeral Tailscale keys.
