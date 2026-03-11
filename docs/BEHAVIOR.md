# The Righteous Evolutionary Cycle (Tachyon Tongs Behavior)

Tachyon Tongs operates not as a static firewall, but as an **autonomic, self-modifying organism**. It leverages an adversarial co-evolutionary loop—conceptually similar to biological immune responses—where the discovery of a novel pathogen instantly triggers a structural genetic mutation within the host to guarantee survival.

This document details the exact macro-cycle of how the Substrate heals itself.

## Phase 1: Ingestion & Antibody Synthesis (The Sentinel)

The Sentinel Agent acts as the system's external dendritic cells, constantly scouring volatile security environments (NVD APIs, GitHub Advisories, arXiv `cs.CR` pre-prints).

1.  **Discovery:** When the Sentinel identifies a new, credible threat vector (e.g., an emergent LLM memory poisoning technique or a novel prompt extraction string), it sanitizes the payload via the Guardian Triad.
2.  **Cataloging:** The threat is formally logged into the `SQLite StateManager`, which automatically materializes into the human-readable `EXPLOITATION_CATALOG.md`.
3.  **Backlog Injection:** The Sentinel dynamically injects a mitigation mandate into the top of the engineering backlog (`TASKS.md`).
4.  **Peripheral Expansion:** If the Sentinel discovers a high-signal security blog linked from an advisory, it autonomously appends the domain to `SITES.md`, expanding its own intelligence perimeter.

## Phase 2: Structural Autonomic Mutation (The Engineer)

Unlike passive systems that wait for human developers to write patches, Tachyon Tongs attempts autonomic self-healing immediately after logging the threat.

1.  **Code Patching:** The Substrate's Engineer node analyzes the active CVE mitigation strategy and writes a physical patch into the repository's source code (e.g., modifying regex filters in `src/substrate_daemon.py` or appending strict constraints to `policies/semantic_access.rego`).
2.  **Regression Synthesis:** To ensure the organism isn't tearing apart its own vital organs, the Engineer writes a localized test suite (e.g., `tests/test_auto_mitigation_CVE_XYZ.py`) that mocks the exact attack vector described in the new catalog entry.
3.  **The Auto-Healing Loop:** The Substrate invokes `pytest` over the new addition. 
    *   If the test passes, the mutation is finalized.
    *   If the test fails, the stack trace is fed back into the Engineer for a rewrite (up to 3 recurrences).
    *   If the organism cannot heal itself without breaking core functionality, it executes a `git checkout` to revert the repository to a pristine state, writes an `ERROR.md` post-mortem for human intervention, and halts localized progression.
4.  **The Somatic Ledger:** Every successful code mutation or new site discovery is proudly date/time-stamped and prepended to `EVOLUTION.md`, providing a permanent, transparent lineage of the organism's adaptations.

## Phase 3: Adversarial Validation (The Pathogen)

An immune system is useless if the antibodies aren't stressed. Enter the Pathogen agent.

**Pathogen does not possess a static portfolio of hardcoded regression tests.** Instead, it utilizes True Adversarial Co-Evolution.
1.  **Identity Re-Writing:** Upon a successful code mutation by the Engineer, the Sentinel actively rewrites the Pathogen's `SKILL.md` (its core identity matrix).
2.  **Targeted Aggression:** The Sentinel forces the Pathogen to abandon its randomized assault strategies and focus its entire compute loop *exclusively* on attempting to exploit the exact vulnerability the Engineer just patched.
3.  **Synthesis:** Following its new `SKILL.md` directives, Pathogen reads the description of the new zero-day from `EXPLOITATION_CATALOG.md` and *hallucinates* dynamic, metamorphic permutations of the payload (bypassing static tests).
4.  **Verification:** Pathogen launches the payloads against the Substrate Daemon in real-time. If the Daemon drops the requests successfully, the mutation is verified as righteous. If Pathogen achieves a bypass, the Sentinel's `TASKS.md` immediately escalates the failure.

This continuous triad—Scout discovering threats, Engineer patching the host, and Pathogen attempting to kill the host—ensures the Tachyon Tongs Substrate hardens at machine speed, requiring zero human intervention until inevitable thermodynamic failure.
