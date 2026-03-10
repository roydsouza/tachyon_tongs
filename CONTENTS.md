# Tachyon Tongs: Directory of Contents

This document provides a bird's-eye view of all critical documentation, intelligence catalogs, configuration structures, and core scripts within the Tachyon Tongs repository to streamline audit and deployment efforts.

## 1. High-Level Documentation

*   [`README.md`](README.md): The primary whitepaper outlining the problem (AI hijacking), the Tachyon Tongs solution (Tiered Sandbox, Triad Pipeline), protection variants, and macOS Apple Silicon quickstart.
*   [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Deep-dive into the internal control flows, detailing the Guardian Triad, the integration of Open Policy Agent (OPA) `.rego` intent-gating, Apple Native Sandboxing, and `mlx_lm` Meta acceleration.
*   [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md): The Builder's Guide. Structural methodologies to configure In-Band (Substrate managed) and Out-of-Band (Independent) agents, including generic manifest templates.
*   [`CONTENTS.md`](CONTENTS.md): This file.

## 2. Intelligence & Auditing Catalogs

*   [`EXPLOITATION_CATALOG.md`](EXPLOITATION_CATALOG.md): The Master Ledger. Synthesized threat vectors retrieved by the Sentinel Blue Team and exported automatically by the SQLite `StateManager`.
*   [`RUN_LOG.md`](RUN_LOG.md): The chronologically appended, multi-tenant cryptographically verified summary of execution actions, bounded by N=25 limits.
*   [`SITES.md`](SITES.md): Formal tracking of globally vetted intelligence destinations (e.g., CISA, GitHub Advisories, NVD API 2.0).

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

*   [`doom_ticker.py`](scripts/doom_ticker.py): Shared utility outputting terminal-style apocalyptic reporting sourced from the intelligence catalogs.
*   [`start_opa.sh`](scripts/start_opa.sh): Local bootstrapper ensuring the Open Policy Agent port is initialized securely bound to localhost.
