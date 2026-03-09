# 🧠 Sentinel Operational Strategy (The Master Plan)

> *"To defeat the Prompt Injection, you must think like the Prompt Injection. But also wrap yourself in non-printable Unicode characters." - Ancient DevOps Proverb*

This document defines the behavioral logic and execution strategy for the **Sentinel Agent**, built using the **Google Agent Development Kit (ADK)**. 

The strategy is simple: Let the Sentinel autonomously hunt for threats, parse horrifying academic papers about zero-days, and generate actionable mitigations... *without getting hijacked itself.*

## 🛡️ The Prime Directive
**The Sentinel must never execute code found during its search operations.** 
Its sole utility in life is to be a glorified, extremely paranoid librarian. It gathers intelligence, summarizes it, complains about it in `TASKS.md`, and goes to sleep.

## 🔄 The Threat Intelligence Loop

The Sentinel runs on a scheduled cron-loop (e.g., every 12 hours). It follows this hyper-rigid ADK pipeline, and if it deviates, Matchlock puts it in timeout.

### Step 1: Target Selection & Fetching
1. Read `SITES.md` to figure out whose blogs we are allowed to read today.
2. Invoke the **Fetcher** (Stage 1 of the Prophylactic Pipeline). 
   - *Constraint:* The Fetcher runs in `network: egress-only` mode. It downloads raw HTML/PDFs into an isolated `/tmp/fetch_inbox` and then has its hands tied behind its back.

### Step 2: Content Sanitization (The Scrub Down)
1. The ADK invokes the **Sanitizer** (Stage 2).
2. The Sanitizer mercilessly strips `<script>` tags, hidden CSS, and zero-width characters. 
3. The ADK then wraps the cleaned text in machine-verifiable cryptographic boundaries. It looks like this:
   ```text
   \u0001UNTRUSTED_CONTENT_START\u0002
   [The sanitized text goes here. The AI knows this box is dangerous.]
   \u0003UNTRUSTED_CONTENT_END\u0004
   ```

### Step 3: Analysis (The Padded Room)
1. The ADK passes the bounded payload to the **Analyzer Agent** (Stage 3). 
   - *Constraint:* The Analyzer is entirely air-gapped. No network. No terminal. Just a brain in a jar analyzing text.
2. The Analyzer extracts the exploit category (e.g., Sandbox Escape), the attack vector, and frantically proposes defenses.

### Step 4: Verification & Synthesis (The Bouncer)
1. The **Verifier Agent** (Stage 4) cross-references the Analyzer's output to make sure it didn't hallucinate or try to slip a `curl` command into the final report.
2. If validated, the Sentinel patches the local knowledge base:
   - Appends new nightmare fuel to `ATTACKS.md`.
   - Appends proposed solutions to `MITIGATION.md`.
3. **Critical Step:** The Sentinel generates an actionable ticket in `TASKS.md` for AntiGravity (and Roy) to implement the defense so we don't all get hacked tomorrow.

## 🧬 Self-Improvement Protocol

The Sentinel is constantly watching itself. It's a 24/7 Civilization-Scale Vibe Check.
- If the Analyzer frequently flags "Unknown Vulnerability Type," the Sentinel generates a task to update its own prompt taxonomy.
- If a target in `SITES.md` yields zero actionable intel for 30 days, the Sentinel deletes the link. Tokens aren't free, you know. Make them earn their keep.
