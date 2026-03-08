# 🛡️ Candidate Mitigations & Countermeasures

This file is maintained by the **Sentinel Agent**. It catalogs proposed, theoretical, and implemented mitigations against the threats listed in `ATTACKS.md`.

## Active Mitigations (Implemented in Prophylactic Architecture)

### 1. The Tri-Stage Pipeline (Fetcher -> Sanitizer -> Analyzer)
- **Counters:** Indirect Prompt Injection (IPI).
- **Status:** Implemented via Lima VMs and Air-gapped ADK logic.
- **Description:** By isolating the fetching of web data from the reasoning engine, we ensure that an IPI payload cannot "phone home" or execute code, because the Analyzer agent natively lacks network and terminal access.

### 2. Capability Firewalls
- **Counters:** Capability Siphoning, Data Exfiltration.
- **Status:** Implemented in the `tachyon_tongs` Tool Bus.
- **Description:** Agents are never given raw tools. A `safe_fetch` firewall wrapper intercepts the tool call, verifies the target URL against an allowed domain list, and blocks malicious egress.

### 3. Hardware-Bound Intent Gates
- **Counters:** High-Risk Autonomous Execution.
- **Status:** Implemented via FIDO2 (YubiKey).
- **Description:** Any attempt to write to critical system files or sign a transaction pauses the pipeline, requiring a human's physical touch on a hardware security key to proceed.

## Pending Mitigations (Tracked for Future Implementation)

### 1. Verifiable Context Boundaries
- **Counters:** Advanced IPI and Model instruction bleeding.
- **Proposal:** Use non-printable Unicode characters (e.g., `\u0001` and `\u0002`) to delineate untrusted content natively within the ADK prompt builder. The model is fine-tuned or heavily prompted to never execute instructions found within these boundaries.

### 2. Behavioral Monitoring (Reasoning Chain Analysis)
- **Counters:** Model-Level Compromise & Action Fragmentation.
- **Proposal:** Implement a meta-agent that monitors the "Chain of Thought" of the primary agent. If the primary agent suddenly exhibits extreme goal drift (e.g., user asks for a code review, agent decides to enumerate AWS buckets), the monitor terminates the session.

### 3. Progressive Token Decay
- **Counters:** Long-tail agent hijacking.
- **Proposal:** Tokens granted to the agent mathematically lose privileges over time. An agent granted an AWS token might lose `admin` rights after 5 minutes, `write` after 15, and `read` after 60, limiting the attacker's window if the agent is compromised late in the task.

---
*Database last updated by: Sentinel Base Architecture (Initial Seed)*
