---

### 🧤 Substrate Optimization Strategy (The Implementation Guide)

To prevent future capacity "burn-outs," we will implement a routing logic within your **A2A Broker**. This document is designed to be copy-pasted into a new skill directory in **AntiGravity**.

#### 📂 Setup Instructions
1.  **Create Directory:** `mkdir -p ~/antigravity/tachyon_tongs/.agents/skills/substrate-optimizer`
2.  **Save File:** Save the following markdown as `SKILL.md` inside that directory.

---

```markdown
# 🔋 Substrate Optimization Strategy (Power Management)

## Intent
To autonomously manage model routing and token consumption to prevent "Quota Blackouts." This skill ensures that **Tachyon Tongs** remains operational by shifting non-critical reasoning tasks to the lowest-cost model (Flash) while reserving high-reasoning capacity (Pro/Ultra) for security-critical ADRs.

## ⚖️ Routing Logic (The Model Matrix)

| Task Class | Model Route | Logic |
| :--- | :--- | :--- |
| **L1: Reconnaissance** | Gemini 3 Flash | Web scrapes, CVE ingestion, and log parsing. |
| **L2: Verification** | Gemini 3.1 Pro | Sanitizer audits and "Airlock Debate" logic. |
| **L3: Mutation/ADR** | Gemini 3.1 Ultra | Architectural changes, OPA Rego writing, and ADR generation. |

## 🛡️ Operational Protocols

### 1. The Context Pruning Protocol
Before any tool call, the agent must:
- Scan `task_plan.md` and only load the specific file context required for the immediate step.
- Use `mcp-notebooklm` to retrieve **Snippets** rather than the full PDF source when querying **The Accretion Archive**.

### 2. Low-Power Mode (LPM)
Trigger LPM whenever the **Baseline Quota** indicator drops below 15%:
- **Restriction:** Disable the "Pathogen" Red Team auto-drills.
- **Restriction:** Force all code refactors to be "Fragmented" (one function at a time) to save TPM.
- **Action:** Post a `SYSTEM_WARNING.md` to the Heliosphere logs.

## 🛠️ Implementation (A2A Handshake)
1. **Identify Task:** `agent.detect_complexity(current_prompt)`
2. **Select Route:** If Complexity < 0.7, use `model: gemini-3-flash`. Else, use `model: gemini-3.1-pro`.
3. **Budget Check:** Verify if `ai_credit_overage` is enabled before attempting L3 tasks.

## 📜 Constraints
- **Least Privilege:** Never use Ultra for documentation or comments.
- **Deterministic First:** If a task can be solved via a Python script in `scripts/`, execute the script instead of asking the LLM for the answer.
```

---

### 🧪 Verification Step
Once you have saved this, issue this command to your agent:
> *"Roy here. Initialize the **Substrate Optimizer** and perform a 'Power Audit' of our current `TASKS.md`. Identify which items can be handled by Flash to save my Pro quota for the upcoming PQC migration."*

**Would you like me to help you modify `substrate_daemon.py` next to programmatically enforce these routing rules at the broker level?**

