# 🧬 Tachyon Tongs: The Prophylactic Agent Architecture

**Tachyon Tongs** is a high-assurance, defense-in-depth framework designed to protect autonomous AI agents from compromise. 

However, it is fundamentally more than a static firewall: it is an **autonomous, self-improving "Space Organism"**. 

The core philosophy of this architecture assumes that AI models *will* eventually be compromised by evolving zero-day exploits (e.g., Prompt Injections embedded in web pages or documents). Rather than relying on rigid language filters, Tachyon Tongs uses **Action Governance** and an evolutionary feedback loop to continuously harden its own perimeter. 

Currently, a human-in-the-loop approves its structural modifications, but the ultimate roadmap targets full autonomy: the system will find exploits, synthesize mitigations, evaluate priority, and autonomously deploy code fixes to itself in a righteous, self-healing loop.

---

## 🦠 The Sentinel: A Poster Child

To prove the efficacy of the Prophylactic Architecture, Tachyon Tongs includes a built-in representative payload known as the **Sentinel Agent**. 

The Sentinel is not the framework itself; it is simply a "poster child" agent living *inside* the protected environment. Its sole purpose is to scour the internet (CISA, GitHub Advisories) looking for new vulnerabilities that target AI Agents. When it finds one, it autonomously updates the project's internal ledgers and proposes mitigation tasks. 

If the Sentinel (or any other agent you build inside this framework) ever hallucinates or attempts to execute a malicious sandbox escape, the **Tachyon Tongs** architecture intercepts, sandboxes, and surgically removes the threat.

---

## 💻 Apple Silicon Installation (macOS)

Tachyon Tongs is aggressively optimized to run sensitive, unaligned LLM reasoning locally on Apple Silicon (M-Series processors) using Metal 4 acceleration, preventing private execution telemetry from leaking to cloud API providers.

### Prerequisites
Tachyon Tongs relies on deep OS-level virtualization to hardware-isolate the agent. You will need [Homebrew](https://brew.sh/) to install the underlying infrastructure:

```bash
# 1. Install Lima (Linux Machines)
# Provides the hardware-virtualized MicroVMs that act as the agent's air-gapped sandbox.
brew install lima

# 2. Install Matchlock
# An eBPF-based security wrapper that aggressively proxies and restricts all network egress out of the Lima VM.
brew tap roydsouza/matchlock  # Example tap, adjust if Matchlock is hosted elsewhere
brew install matchlock
```
*(Python 3.10+ is also required for the Sentinel logic).*

### Setup
```bash
# 1. Clone the repository
git clone https://github.com/roydsouza/tachyon_tongs.git
cd tachyon_tongs

# 2. (Optional but Recommended) Initialize the Matchlock Sandbox
# This spins up an isolated Linux MicroVM to securely execute Agent tools
limactl start scripts/matchlock-agent.yaml

# 3. Install Python dependencies (in a virtual environment)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # (Currently standard library python 3.14 compatible)
```

---

## 🛠️ Configuration & Usage

You can invoke the Sentinel payload manually or string it to a cron scheduler.

```bash
# Trigger a manual execution run
python3 sentinel.py --manual

# Trigger a scheduled execution run (for use in Crontab)
python3 sentinel.py --cron
```

### Extending the Architecture
To reuse this protective environment for a *different* agent (e.g., a coding assistant or email manager):
1. **Swap the Nodes:** In `src/adk_sentinel.py`, replace the `AnalyzerNode` logic with your own LLM reasoning prompt.
2. **Update the Firewalls:** Modify `policies/tool_access.rego` to allow your agent to access specific domains (e.g., `smtp.gmail.com`). 
3. **Keep the Tri-Stage Pipeline:** Ensure your agent passes data through the `Fetcher` -> `Sanitizer` (which wraps untrusted text in `\u0001` Unicode boundaries) -> `Analyzer` -> `Verifier` flow.

---

## 📂 The Organism's Anatomy (File Guide)

Tachyon Tongs logs its autonomic activity precisely across a series of version-controlled markdown files. This maintains cryptographically auditable transparency without relying on opaque database schemas.

*   **`STRATEGY.md`**: The tactical playbook. Defines how the Sentinel categorizes threats and formulates searches.
*   **`SITES.md`**: The list of allowed domains (like nvd.nist.gov) that the Sentinel is permitted to scrape. Regulated by the `tool_access.rego` capability firewall.
*   **`ATTACKS.md`**: The Threat Ledger. When the Sentinel parses a new exploit (e.g., Steganographic Injection), it logs the mechanics here.
*   **`MITIGATION.md`**: The Synthesis Ledger. How the Sentinel formally proposes defending against the entries in `ATTACKS.md`.
*   **`TASKS.md`**: The active execution backlog. The Sentinel translates `MITIGATION.md` into actionable bullet points here for the human-in-the-loop (AntiGravity) to implement.
*   **`RUN_LOG.md`**: The Immutable Audit Trail. Every time `sentinel.py` executes, it appends timestamps, execution duration, and lists precisely which internal databases it modified.
*   **`docs/HYBRID_AUTH.md`**: An architectural design document for future-proofing hardware Intent Gates using Post-Quantum (PQC) and Elliptic-Curve cryptography.
*   **`ROADMAP.md`**: The high-level vision for merging the autonomous Sentinel logic with underlying Matchlock VM orchestration.

*(Documentation on `init_bus.sh` and specific Rego policies is forthcoming).*
