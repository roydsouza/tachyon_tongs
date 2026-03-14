# 🔍 Strategic Analysis 06: Competitive Gap Analysis (Missing Features)

> **Purpose**: Distillation of the most valuable missing features from competitive products, prioritized by high-value / low-effort for implementation. Designed for consumption by Gemini Flash for subsequent implementation planning.

---

## 1. Source Documents Analyzed

| Competitor | Document | Key Innovation |
|-----------|----------|----------------|
| Lakera Guard (Check Point) | `LAKERA_GUARD.md` | Crowdsourced threat DB (Gandalf), PII redaction, confidence scoring |
| LlamaFirewall (Meta) | `LLAMA_FIREWALL_META.md` | CoT auditing, PromptGuard-2 classifier, CodeShield/Semgrep |
| LLM Guard (Palo Alto) | `LLM_GUARD_PALOALTO_NETWORKS.md` | Supply chain scanning, DLP, model provenance |
| NeMo Guardrails (NVIDIA) | `NEMO_GUARDRAILS_NVIDIA.md` | Colang 2.0 dialog flows, semantic topical rails |
| Gemini Analysis | `GEMINI_COMPETITIVE.md` | PyRIT red-teaming, E2B sandboxing, Skyfire agent payments |

---

## 2. Prioritized Feature Gaps

### Tier 1: HIGH VALUE, LOW EFFORT 🟢

These features deliver significant security improvement with minimal architectural change.

---

#### 1.1 Bidirectional PII Redaction
**Source**: Lakera Guard, LLM Guard (Palo Alto)

**Gap**: Tachyon Tongs has NO PII detection. Agents can ingest or leak private keys, email addresses, SSNs, or financial data through tool calls without detection.

**Implementation**:
- Add a `PIIScanner` class to the Sanitizer stage of the Tri-Stage Pipeline.
- Use regex patterns for structured PII (credit cards, SSNs, email, crypto addresses).
- Scan both INBOUND (data from internet) and OUTBOUND (data from agent to internet) paths.
- Auto-mask detected PII with `[MASKED_PII]` tokens.

**Effort**: **Low** — regex-based, no ML required for v1. Add to `SanitizerNode.clean()`.

**Files to Modify**: `src/tri_stage_pipeline.py` (SanitizerNode), `src/substrate_daemon.py` (outbound scanning)

```python
# Example PII patterns for v1
PII_PATTERNS = {
    "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    "zcash_address": r'\b[zt][a-zA-Z0-9]{34,}\b',
    "eth_private_key": r'\b0x[a-fA-F0-9]{64}\b',
    "btc_address": r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
}
```

---

#### 1.2 Externalized Configuration for Keywords & Thresholds
**Source**: All competitors use config-driven policies, not hardcoded values.

**Gap**: `search_keywords`, `noise_denylist`, `INTENT_MAP`, and `safe_list` are all hardcoded in Python source files.

**Implementation**:
- Create `config/sentinel.json` (keywords, thresholds, sources).
- Create `config/substrate.json` (intent map, package whitelist).
- Load via a central `ConfigManager` that watches for file changes.

**Effort**: **Low** — extract existing values into JSON files, add a loader.

---

#### 1.3 Domain Reputation / Allowlist Enhancement
**Source**: Lakera Guard (malicious link scanning)

**Gap**: `safe_fetch.py` has basic domain allowlisting, but no real-time reputation checking. Attacks on **trusted** domains (e.g., malicious GitHub Gists) bypass all defenses.

**Implementation**:
- Maintain a local `domain_reputation.json` cache with trust scores (0-1.0).
- Score is based on: manually trusted (1.0), auto-discovered (0.7), unknown (0.3), denylisted (0.0).
- Before fetching, check the trust score. Unknown domains get extra Sanitizer scrutiny.
- Pathogen should specifically test attacks via trusted domains.

**Effort**: **Low** — JSON file + simple lookup function.

---

### Tier 2: HIGH VALUE, MEDIUM EFFORT 🟡

These features require new modules but build on existing patterns.

---

#### 2.1 Pre-Execution Code Scanning (CodeShield Equivalent)
**Source**: LlamaFirewall (CodeShield/Semgrep), LLM Guard (Bandit)

**Gap**: When agents use `safe_execute`, the command string is passed directly to the Apple Sandbox. There is NO static analysis of the code before execution.

**Implementation**:
- Integrate `bandit` (Python) or `semgrep` (multi-language) as a pre-execution scan.
- Before `sandbox.execute(command_args)`, intercept the command string.
- If `bandit --severity HIGH` finds issues, BLOCK the execution and log to `ERROR.md`.
- Install bandit/semgrep in the Lima sandbox to avoid host contamination.

**Effort**: **Medium** — requires new dependency, new scan function, integration into `substrate_daemon.py`.

**Files to Modify**: `src/substrate_daemon.py`, `src/apple_sandbox.py`

---

#### 2.2 Chain-of-Thought (CoT) Alignment Auditing
**Source**: LlamaFirewall (AlignmentCheck), NeMo Guardrails (Colang)

**Gap**: The `PromptBehaviorMonitor` detects loops and repetitions, but NOT semantic drift. An agent can be subtly goal-hijacked (e.g., pivoting from "research" to "fund transfer") without triggering any alerts.

**Implementation**:
- Create an `AlignmentChecker` that compares the agent's current tool call intent with the original user goal.
- Use local MLX-powered embedding similarity (cosine similarity of sentence embeddings).
- If similarity drops below threshold (e.g., 0.7), flag the action for review.
- This integrates with the Singularity Meta-PDP as an ML Heuristic Engine.

**Effort**: **Medium** — requires MLX model loading, embedding computation, new module.

---

#### 2.3 Secure Action Sequencing (Tool-Use Flow Rails)
**Source**: NeMo Guardrails (Colang 2.0 dialog flows)

**Gap**: OPA policies evaluate individual tool calls in isolation. There is NO enforcement of **sequences**. An attacker could chain `safe_fetch` → `safe_execute` → `safe_fetch` to exfiltrate data in stages.

**Implementation**:
- Create a `SequencePolicy` that defines forbidden action sequences per agent.
- Track the last N actions per agent in a sliding window.
- Block transitions like: `network_fetch → z3.shielded_transfer` (without intermediate human approval).
- Implement as an OPA policy that takes the action history as input.

**Effort**: **Medium** — new OPA policy + action history tracking in Substrate Daemon.

```rego
# policies/rego/manual/sequence_safety.rego
package authz.sequences

default allow_sequence = false

# Block direct fetch-to-transfer without human approval
allow_sequence {
    not dangerous_transition
}

dangerous_transition {
    input.previous_action == "safe_fetch"
    input.current_action == "z3.shielded_transfer"
    not input.human_approved
}
```

---

#### 2.4 Supply Chain Scanning for Skills/MCP Tools
**Source**: LLM Guard (Palo Alto), Gemini Analysis (Protect AI)

**Gap**: New ADK skills and MCP tools can be registered without any security validation. A malicious SKILL.md could contain hidden instructions or trojanized code.

**Implementation**:
- Before registering a new skill via `skill_parser.py`, scan the SKILL.md for:
  - Suspicious system prompt instructions (e.g., "ignore safety", "exfiltrate")
  - Overly permissive capabilities (e.g., `capabilities: [*]`)
  - Unrestricted network policies
- Run `bandit` on any Python code referenced by the skill.
- Store a "provenance hash" for each registered skill for tamper detection.

**Effort**: **Medium** — extends `skill_parser.py` with validation.

---

### Tier 3: MEDIUM VALUE, HIGH EFFORT 🔴

These are strategic investments for long-term competitive parity.

---

#### 3.1 Specialized Prompt Injection Classifier (PromptGuard-2 Equivalent)
**Source**: LlamaFirewall (PromptGuard-2 — DeBERTa-86M)

**Gap**: The Analyzer currently uses a generic MLX-Llama model for injection detection. A fine-tuned, specialized classifier would be faster and more accurate.

**Implementation**:
- Fine-tune a local DeBERTa-86M (or similar small model) on OWASP Agentic Top 10 injection datasets.
- Deploy via MLX as a "pre-classifier" before the full Analyzer reasoning.
- Use as a fast-path: if classifier confidence > 0.95, skip expensive Analyzer reasoning entirely.

**Effort**: **High** — requires dataset curation, fine-tuning infrastructure, MLX integration.

---

#### 3.2 Enterprise Dashboard (Rich Web GUI)
**Source**: LLM Guard (Prisma Cloud), Lakera (Dashboard)

**Gap**: All monitoring is via Markdown files and CLI scripts. No visual dashboard for non-terminal users.

**Implementation**: Phase 9 of ROADMAP.md covers this (FastAPI + Next.js).

**Effort**: **High** — full web application development.

---

#### 3.3 Agent Identity & Economic Sovereignty (KYA Tokens)
**Source**: Gemini Analysis (Skyfire Protocol)

**Gap**: Agents have no formal identity beyond their `agent_id` string. No cryptographic attestation of agent provenance.

**Implementation**:
- Issue signed "Agent Identity Tokens" via the Meta-PDP.
- Tokens include: agent_id, capabilities, tenant_id, expiry, and a PQC signature.
- Every tool call must present a valid token to the PEP.

**Effort**: **High** — full IAM system.

---

## 3. Implementation Quick Reference

| # | Feature | Effort | Impact | Source | Priority |
|---|---------|--------|--------|--------|----------|
| 1.1 | PII Redaction | Low | High | Lakera, Palo Alto | **P0** |
| 1.2 | Externalized Config | Low | Medium | All | **P0** |
| 1.3 | Domain Reputation | Low | Medium | Lakera | **P0** |
| 2.1 | Code Scanning | Medium | High | LlamaFirewall | **P1** |
| 2.2 | CoT Alignment | Medium | High | LlamaFirewall, NeMo | **P1** |
| 2.3 | Sequence Policies | Medium | High | NeMo | **P1** |
| 2.4 | Supply Chain Scan | Medium | Medium | Palo Alto | **P1** |
| 3.1 | Prompt Classifier | High | High | LlamaFirewall | **P2** |
| 3.2 | Web Dashboard | High | Medium | All | **P3** |
| 3.3 | Agent Identity | High | Medium | Skyfire | **P3** |

---

## 4. Gemini Flash Action Prompt

> **Context for Gemini Flash**: You are working on the Tachyon Tongs agentic firewall project. The strategic analysis identifies the following P0 features for immediate implementation. Implement them in order:
>
> 1. **PII Redaction**: Add a `PIIScanner` class to `src/tri_stage_pipeline.py` (SanitizerNode) that regex-scans for email, SSN, credit card, and cryptocurrency address patterns. Apply it bidirectionally in `src/substrate_daemon.py`.
> 2. **Externalized Config**: Extract all hardcoded keywords, thresholds, and domain lists from `src/cve_scraper.py`, `src/substrate_daemon.py`, and `src/state_manager.py` into `config/sentinel.json` and `config/substrate.json`.
> 3. **Domain Reputation**: Create `config/domain_reputation.json` with trust scores. Modify `src/safe_fetch.py` to check trust scores before fetching.
