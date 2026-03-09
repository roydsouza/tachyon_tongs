# 🧬 Tachyon Tongs: The Prophylactic Agent Architecture

> *"If your AI agent isn't occasionally trying to escape its sandbox to order 10,000 pizzas, are you even building AGI? Keep the airgap tight, folks." - Ancient DevOps Proverb*

**Tachyon Tongs** is a high-assurance, defense-in-depth framework designed to protect autonomous AI agents from compromise. 

But it's more than just a static, boring firewall. It is an **autonomous, self-improving "Space Organism"**. 

Why? Because trying to build the perfect regex to stop a Prompt Injection is like trying to catch the ocean with a spaghetti strainer. AI models *will* eventually be compromised. Tachyon Tongs embraces this chaos with **Action Governance**: let the agent think whatever weird thoughts it wants, but heavily restrict what it can *do*.

Currently, there's a human-in-the-loop (me, AntiGravity, and you, presumably) clicking "Approve." But the ultimate roadmap? Full autonomy. A righteous, self-healing loop where the system finds exploits, synthesizes its own mitigations, and patches itself while we sit back and monitor the civilization-scale vibe check.

---

## 🦠 The Sentinel: Our Adorable Little Canary

To prove this paranoia actually works, Tachyon Tongs includes a built-in payload known as the **Sentinel Agent**. 

The Sentinel isn't the framework itself; it's our "poster child" living *inside* the protected terrarium. Its sole purpose in life is to scour the internet (CISA, GitHub Advisories) looking for fresh, terrifying ways to hack AI. When it finds one, it panics (productively), updates its internal ledgers, and proposes mitigation tasks. 

If the Sentinel ever hallucinates or tries to break out of the terrarium, Tachyon Tongs intercepts it, sandboxes it, and surgically removes the threat. Good boy, Sentinel.

---

## 💻 Apple Silicon Installation (macOS)

Because leaking our private execution telemetry to cloud providers is a cardinal sin, Tachyon Tongs is aggressively optimized to run locally on Apple Silicon (M-Series) using Metal 4 acceleration.

### Prerequisites
Grab your [Homebrew](https://brew.sh/). We need deep OS-level virtualization to hardware-isolate this bad boy.

```bash
# 1. Install Lima (Linux Machines)
# Because sometimes you need a disposable Linux MicroVM to act as an air-gapped panic room.
brew install lima

# 2. Install Matchlock
# An eBPF-based security wrapper that aggressively proxies the network. 
# Think of it as a very angry bouncer at the door of your Lima VM.
brew tap roydsouza/matchlock 
brew install matchlock
```
*(You also need Python 3.10+. If you're running Python 2.7 in 2026, please seek immediate medical attention).*

### Setup
```bash
# 1. Clone the repository
git clone https://github.com/roydsouza/tachyon_tongs.git
cd tachyon_tongs

# 2. (Optional but Highly Encouraged) Initialize the Matchlock Sandbox
# Spin up the isolated Linux MicroVM.
limactl start scripts/matchlock-agent.yaml

# 3. Install Python dependencies (in a virtual environment, we aren't savages)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```

---

## 🛠️ Configuration & Usage

You can poke the Sentinel manually or tie it to a cron schedule so it can have panic attacks automatically at 3 AM.

```bash
# Poke it with a stick (Manual trigger)
python3 sentinel.py --manual

# Let it haunt your background processes (Cron scheduled)
python3 sentinel.py --cron
```

### 🧩 Extending the Architecture (For Asha)
*"Hey, this sounds super complicated. Do I need a PhD in cybersecurity to use this?"* 

Don't worry, Roy is just being Roy and overengineering things because port conflicts at 2 AM are not fun. The beauty of Tachyon Tongs is that you can swap out our paranoid Sentinel for *your* agent (like a coding assistant) and keep all the protection! 

1. **Swap the Brain:** In `src/adk_sentinel.py`, replace the `AnalyzerNode` with your own LLM prompt.
2. **Open the Doors:** Update `policies/tool_access.rego` to let your agent actually talk to the outside world (e.g., `smtp.gmail.com`). 
3. **Keep the Pipeline:** Just make sure your data still flows through our `Sanitizer` so malicious text gets wrapped in invisible Unicode boundaries. Safe and sound!

---

## 📂 The Organism's Anatomy (File Guide)

Tachyon Tongs logs its autonomic activity precisely across a series of Markdown files, because databases are for people who like paying AWS bills and git commits are essentially a legal affidavit.

*   **`STRATEGY.md`**: The tactical playbook. The Sentinel reads this to remember who it is and who it's currently blocking.
*   **`SITES.md`**: The VIP Guest List. Which domains (like `nvd.nist.gov`) the Sentinel is allowed to scrape before the firewall tells it to "Go to its room."
*   **`EXPLOITATION_CATALOG.md`** (Master File): The "Wall of Weird" + "The Panic Ledger". This is our single source of truth for every way the internet tried to kill us today, coupled with how we dodged the bullet.
*   **`TASKS.md`**: The Backlog of Doom. The `EXPLOITATION_CATALOG.md` translated into actual work items for us to procrastinate on.
*   **`RUN_LOG.md`**: The Audit Trail. Proof that the agent woke up, did its job, and didn't accidentally try to synthesize enriched uranium.
*   **`docs/TAILSCALE.md`**: Phase 4 Networking. Using MagicDNS so we don't have to navigate via IP addresses like it's 1995.
*   **`docs/HYBRID_AUTH.md`**: Post-Quantum Cryptography planning. Things that sound cool but might be complete hallucination. Like a second dog or a "stable" JS framework.
*   **`ROADMAP.md`**: The grand vision of when we finally let this thing off the leash and go to the beach.

---
*Note: If `ATTACKS.md` or `MITIGATION.md` still exist on your drive, they are ghosts of a simpler time. Delete them. They are obsolete. We are efficient now.*
