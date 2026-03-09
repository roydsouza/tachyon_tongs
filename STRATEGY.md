# 🎯 Tachyon Tongs: Operational Strategy (v1.0)

> *"The best way to stay safe in a zero-trust environment is to trust everyone... and then verify them with a high-energy tachyon beam." - Overheard in the Substrate Breakroom*

Our strategy has evolved from "Individual Panic" into **"Systemic Paranoia"**. 

---

## 🧗 Stage 2 Strategy: The Walk (Substrate-First)

In the **Crawl Stage**, our strategy was "Protect the Sentinel at all costs." In the **Walk Stage**, we focus on **Amortized Defense**. 

### 1. Centralized Threat Intelligence
The Sentinel is now a **System Service (Scout)** rather than just a peer. It scours the internet, finds the latest ways to make AI hallucinate its own deletion, and updates the `EXPLOITATION_CATALOG.md`.
- **The Result:** Every other agent in the workspace gets the "vaccine" instantly.

### 2. Mandatory Mediation (The Substrate Law)
No agent is allowed to execute a `SafeFetch` directly. They *must* go through the Substrate Daemon. 
- **The Rationale:** If an agent is compromised, it only sees the sanitized, bounded output. It physically cannot reach the raw, malicious payload because the Substrate (the Guardian Triad) catches it first.

### 3. Verification Enforcement (The Bouncer)
The **Engineer Agent** acts as the final bouncer. It checks for:
- Correct Unicode boundaries.
- No malicious markdown links.
- No shell script injection in the sanitized text.

If the "Analyst" (the reasoning node) is tricked into skipping a check, the Engineer catches the mistake and blocks the whole run. We call this "The Auditor's Revenge."

---

## 🔄 The Feedback Loop: Sentinel -> Substrate -> Agent

1. **Scout:** Finds a new Prompt Injection on GitHub. 🕵️‍♂️
2. **Catalog:** Entries are added to `EXPLOITATION_CATALOG.md`. 📜
3. **Substrate:** Hot-reloads the new threat signature. 🛡️
4. **Agent:** Tries to fetch a similarly poisoned URL; gets blocked before it even sees the packet. 🚫

---
*Anecdote: We once caught the Sentinel trying to 'white-list' a domain that was literally just a picture of a cat with a QR code. Turns out the QR code contained a bash script. The Sentinel now has a mandatory 'No Cats' filter for its own safety. It's still bitter about it.*
ds tied behind its back.

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
   - Appends new nightmare fuel (attack vectors) and proposed biological-grade cures to `EXPLOITATION_CATALOG.md`.
3. **Critical Step:** The Sentinel generates an actionable ticket in `TASKS.md` for AntiGravity (and Roy) to implement the defense so we don't all get hacked tomorrow.

## 🧬 Self-Improvement Protocol

The Sentinel is constantly watching itself. It's a 24/7 Civilization-Scale Vibe Check.
- If the Analyzer frequently flags "Unknown Vulnerability Type," the Sentinel generates a task to update its own prompt taxonomy.
- If a target in `SITES.md` yields zero actionable intel for 30 days, the Sentinel deletes the link. Tokens aren't free, you know. Make them earn their keep.
