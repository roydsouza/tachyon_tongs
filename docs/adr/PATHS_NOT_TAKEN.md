# 🚷 Tachyon Tongs: Paths Not Taken Ledger

This ledger documents architectural paths and design decisions that were explicitly **rejected** due to security risks, suboptimal reasoning, or operational fragility.

## 🗄️ Rejected Paths

### ❌ Plain SHA-256 for Architectural Integrity (ADR-0001–0015 Legacy)
- **Date Rejected**: 2026-03-18
- **Reason**: Standard SHA-256 hashes are susceptible to collision attacks (long-term) and do not provide the attribution/authentication benefits of a keyed HMAC. 
- **Decision**: Upgraded the substrate to **High-Assurance HVAC (HMAC)** using `TACHYON_SECRET_KEY` to ensure only the authorized substrate operator can mutate architectural records.
- **Risk of Revisit**: High. Future agents might attempt to simplify the code by reverting to plain hashes.

### ❌ In-Stream Prompt Sanitization at the LLM Level Only
- **Date Rejected**: 2026-03-18
- **Reason**: Relying on "System Prompt Guidance" alone to avoid injection is inherently vulnerable to latent instruction activation.
- **Decision**: Implemented the **InputSanitizer** layer as a pre-policy gate (NFKC normalization + regex scrubbing).
- **Risk of Revisit**: Extreme. Prompt injection remains the primary attack vector for agentic systems.

### ❌ Cross-Platform Abstraction Layer (Claude Feedback)
- **Date Rejected**: 2026-03-21
- **Source**: Claude FEEDBACK_CLAUDE_03_20_2230 — "Biggest barrier to adoption"
- **Reason**: Apple Silicon lock-in (Secure Enclave, sandbox-exec, Metal) is an intentional design choice, not a limitation. The substrate's security guarantees depend on hardware-specific primitives that cannot be faithfully emulated on Linux/Windows without degrading the trust model. Abstracting these away would create a false sense of security on less capable platforms.
- **Decision**: Apple Silicon remains the sole supported platform. The moat is the feature.
- **Risk of Revisit**: Low. Only revisit if Apple deprecates sandbox-exec or Hypervisor.framework.

### ❌ SQLite Materialized View for Exploitation Catalog (Grok Feedback)
- **Date Rejected**: 2026-03-21
- **Source**: Grok FEEDBACK_GROK_03_20_2230 — "sign the view instead of the markdown"
- **Reason**: The markdown-based Exploitation Catalog is human-readable, git-diffable, and directly embeddable in debate transcripts. Moving to SQLite would break the forensic audit trail that relies on line-by-line diffing and signed markdown commits.
- **Decision**: Catalog remains markdown. Integrity is ensured via hybrid dual-signatures on the file itself.
- **Risk of Revisit**: Low. Only revisit if catalog exceeds 10,000 entries.

### ❌ Symbiote Agent / Embedded WASM Shim for Third-Party Agents (Grok Feedback)
- **Date Rejected**: 2026-03-21
- **Source**: Grok FEEDBACK_GROK_03_20_2230 — "Turns any third-party agent into a Tachyon-native citizen"
- **Reason**: Embedding a Tachyon shim into third-party agents (Claude Desktop, Cursor, etc.) requires those agents to opt-in to our trust model and load our signed code. This creates a supply-chain attack vector in reverse — our shim becomes a target inside foreign runtimes we don't control.
- **Decision**: Tachyon protects agents that run *under* the substrate, not agents that load our code *into their process*.
- **Risk of Revisit**: Medium. Revisit if a standard "agent telemetry protocol" emerges.

### ❌ ConfigManager / IaC Agent (Claude Feedback)
- **Date Rejected**: 2026-03-21
- **Source**: Claude FEEDBACK_CLAUDE_03_20_2230 — "Infrastructure-as-Code agent"
- **Reason**: Tachyon Tongs is an agent security substrate, not a DevOps pipeline. Terraform/Kubernetes configuration management is orthogonal to the project's mission. An IaC agent would run *under* Tachyon's protection, but building it as part of the core substrate conflates security infrastructure with deployment tooling.
- **Decision**: Out of scope. External IaC agents can be protected by Tachyon without being part of it.
- **Risk of Revisit**: None.

### ❌ Persistent Terminal Executor / Code Execution Agent (Grok Feedback)
- **Date Rejected**: 2026-03-21
- **Source**: Grok FEEDBACK_GROK_03_20_2230 — "Open Interpreter under sandbox"
- **Reason**: A persistent terminal executor with `pip install` and `git` access — even sandboxed — creates an unnecessarily large blast radius inside the security substrate. This role is better served by external tools (Aider, Open Interpreter) running *under* Tachyon's protection rather than *as* a core agent.
- **Decision**: Out of scope. Use Tachyon to *protect* existing terminal executors, don't build one inside the firewall.
- **Risk of Revisit**: Low.

### ❌ Open-Sourcing Core Components (Claude Feedback)
- **Date Rejected**: 2026-03-21
- **Source**: Claude FEEDBACK_CLAUDE_03_20_2230 — "broader value"
- **Reason**: The substrate is in active HITL development. Open-sourcing before the HOTL transition would expose unfinished security surfaces and invite premature adoption of an unstable platform.
- **Decision**: Defer until the substrate achieves HOTL readiness (Phase 32 milestone).
- **Risk of Revisit**: High. Revisit after 30 consecutive clean days in HOTL mode.

---

## Integrity Attestation


