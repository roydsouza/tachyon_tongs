# ⚔️ Tachyon Tongs: Competitive Analysis & Market Positioning

> This is a **living registry** of competitive intelligence, architectural moats, and strategic positioning. It is designed to be updated continuously as new competitors and attack vectors emerge.

---

## 🏗️ The Architectural Moat

Tachyon Tongs maintains a five-layer defense-in-depth strategy that provides unique security guarantees compared to SaaS-first or cloud-dependent competitors.

| Layer | Moat Name | Security Guarantee |
|-------|-----------|--------------------|
| **1** | **Data Sovereignty** | 100% local execution on Apple Silicon. Zero cloud telemetry. |
| **2** | **Evolutionary Defense** | Sentinel/Pathogen co-evolution. The system self-heals by red-teaming itself. |
| **3** | **Hardware Isolation** | Tier-0 sandboxing via macOS Seatbelt and Lima/Matchlock. |
| **4** | **Air-Gapped Pipeline** | Physical isolation between network egress (Scout) and reasoning (Analyst). |
| **5** | **Deterministic Policy** | Logic-based enforcement (OPA/Rego + Cedar) instead of fragile LLM prompts. |

---

## 🏆 Superiority Matrix

### Strategic Advantages

| Vector | Tachyon Tongs | SaaS Competitors (Lakera, LLM Guard) | Verdict |
|--------|---------------|-------------------------------------|---------|
| **Privacy** | Air-gapped local inference | Prompts sent to 3rd party cloud | ✅ **Sovereign** |
| **Red-Teaming** | Integrated runtime adversary | Static benchmarks / External tools | ✅ **Autonomous** |
| **Hardening** | Hardware-level Seatbelt sandbox | API-level middleware | ✅ **Hardened** |
| **Protocol** | Native MCP Gateway | Proprietary REST APIs | ✅ **Open** |

---

## 🔍 Competitor Registry

### 🛡️ Active Tracking

| Competitor | Document | Focus Area | Latest Eval |
|------------|----------|------------|-------------|
| **Lakera Guard** | [LAKERA_GUARD.md](file:///Users/rds/antigravity/tachyon_tongs/docs/competition/LAKERA_GUARD.md) | Gandalf, PII, SaaS WAF | 2026-03-14 |
| **LlamaFirewall** | [LLAMA_FIREWALL_META.md](file:///Users/rds/antigravity/tachyon_tongs/docs/competition/LLAMA_FIREWALL_META.md) | CodeShield, PromptGuard-2 | 2026-03-14 |
| **LLM Guard** | [LLM_GUARD_PALOALTO_NETWORKS.md](file:///Users/rds/antigravity/tachyon_tongs/docs/competition/LLM_GUARD_PALOALTO_NETWORKS.md) | Enterprise DLP, Scanners | 2026-03-14 |
| **NeMo Guardrails** | [NEMO_GUARDRAILS_NVIDIA.md](file:///Users/rds/antigravity/tachyon_tongs/docs/competition/NEMO_GUARDRAILS_NVIDIA.md) | Colang 2.0, Dialog Rails | 2026-03-14 |
| **E2B** | [GEMINI_COMPETITIVE.md](file:///Users/rds/antigravity/tachyon_tongs/docs/competition/GEMINI_COMPETITIVE.md) | Code Execution Sandboxing | 2026-03-14 |
| **Skyfire** | [GEMINI_COMPETITIVE.md](file:///Users/rds/antigravity/tachyon_tongs/docs/competition/GEMINI_COMPETITIVE.md) | Agent Economic Identity | 2026-03-14 |

---

## 📈 Strategic Directions

### ✅ Double Down (Strengths)
- **Pathogen Intelligence**: Maintain the most aggressive local red-teaming agent.
- **Apple Silicon Optimization**: Maximize M5 Neural Engine utilization for local sanitization.
- **Deterministic Logic**: Expand OPA/Cedar coverage to reduce reliance on "vibe-based" filtering.

### ⚠️ Close the Gap (Priorities)
- **PII Redaction**: Implement local regex-based PII masking (Tier 1).
- **Static Analysis**: Integrate `bandit`/`semgrep` for code execution scanning (Tier 2).
- **Sequence Policies**: Implement dialog-flow tracking via OPA sequences (Tier 2).

### ❌ Avoid (Anti-Patterns)
- **Cloud Dependency**: Do not build SaaS components that require telemetry.
- **General WAF Features**: Avoid bloating the substrate with traditional web security features.

---

## 📝 Continuous Evaluation Protocol
1. **Identify**: Discovery of new competitor via Sentinel or human review.
2. **Review**: Analyze architecture for moats (e.g., local vs cloud).
3. **Compare**: Create parity/superiority entry in this document.
4. **Action**: Create `TASKS.md` entries if high-value/low-effort gaps are found.