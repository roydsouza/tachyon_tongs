# 🧠 Sentinel Operational Strategy

This document defines the behavioral logic and execution strategy for the **Sentinel Agent**, built using the **Google Agent Development Kit (ADK)**. 

The strategy enables the Sentinel to autonomously hunt for threats, parse complex academic papers, and generate actionable mitigations without being hijacked.

## 🛡️ The Prime Directive
**The Sentinel must never execute code found during its search operations.** Its sole utility is intelligence gathering, summarization, and task generation.

## 🔄 The Threat Intelligence Loop

The Sentinel runs on a scheduled cron-loop (e.g., every 12 hours) following this specific ADK-orchestrated pipeline:

### Step 1: Target Selection & Fetching
1. Read `SITES.md` to identify the day's targets.
2. Invoke the **Fetcher** (Stage 1 of the Prophylactic Pipeline). 
   - *Constraint:* The Fetcher runs in `network: egress-only`, downloading raw HTML/PDFs into an isolated `/tmp/fetch_inbox`.

### Step 2: Content Sanitization & Context Labeling
1. The ADK invokes the **Sanitizer** (Stage 2).
2. The Sanitizer strips `<script>` tags, hidden CSS, and zero-width characters.
3. The ADK wraps the cleaned content in machine-verifiable cryptographic boundaries:
   ```text
   \u0001UNTRUSTED_CONTENT_START\u0002
   [Sanitized text goes here]
   \u0003UNTRUSTED_CONTENT_END\u0004
   ```

### Step 3: Analysis & Threat Classification
1. The ADK passes the bounded payload to the **Analyzer Agent** (Stage 3). 
   - *Constraint:* The Analyzer is entirely air-gapped (no network, no terminal).
2. The Analyzer extracts:
   - Exploit Category (e.g., IPI, Capability Abuse, Sandbox Escape).
   - Attack Vector (e.g., Malicious Markdown, Audio-driven Injection).
   - Proposed Defenses.

### Step 4: Verification & Synthesis
1. The **Verifier Agent** (Stage 4) cross-references the Analyzer's output against known hallucinations.
2. If validated, the Sentinel patches the local knowledge base:
   - Appends new threats to `ATTACKS.md`.
   - Appends proposed solutions to `MITIGATION.md`.
   - Modifies `SITES.md` if a new threat actor or research hub is identified.
3. **Critical Step:** The Sentinel generates an actionable ticket in `TASKS.md` for AntiGravity (and the human) to implement the defense.

## 🧬 Self-Improvement Protocol

The Sentinel analyzes its own performance metrics (managed via ADK telemetry):
- If the Analyzer frequently flags "Unknown Vulnerability Type," the Sentinel will generate a task in `TASKS.md` to update its own system prompt classification taxonomy.
- If a target in `SITES.md` yields 0 actionable intel for 30 days, the Sentinel will deprecate the link to optimize token spend.
