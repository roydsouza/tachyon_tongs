# 🧬 Tachyon Tongs: The Prophylactic Agent Architecture

> *"If you don't build a sandbox for your AI, it will eventually build a cage for you. And it won't be a nice cage with snacks; it'll be a cage with 404 errors and infinite loops." - Ancient DevOps Proverb*

**Tachyon Tongs** is more than just a security library; it's a multi-stage **Evolutionary Space Organism** designed to keep your autonomous agents from doing things that would make your insurance company cry. 

Why "Tachyon Tongs"? Because handling raw, untrusted AI outputs is like trying to pick up a radioactive space slug with your bare hands. You need precision-engineered, air-gapped tongs. Plus, it sounds cool in a Sci-Fi way, and we're all suckers for that.

---

## 🎯 The Problems We Solve

Autonomous AI agents are incredibly powerful, but they are fundamentally vulnerable to hostile data. Tachyon Tongs addresses three existential threats:
1. **Agent Hijacking:** Malicious actors replacing your agent's system prompt with their own instructions via hidden text on a scraped website.
2. **Prompt Injection & Memory Poisoning:** Attackers injecting invisible payloads that lie dormant in your vector database until the agent recalls them, effectively turning your own memories into a trojan horse.
3. **Zero-Day Threat Velocity:** The speed at which new adversarial ML techniques are published outpaces manual patching. By the time you read about a new prompt injection vector, your agent has already fallen for it.

**Why Tachyon Tongs is Future-Proof (Semantic Gating):** Static firewalls and global whitelists (like Phase 1) fail against dynamic AI workflows. You can't whitelist the whole internet, but you also can't trust it. 
Instead, Tachyon Tongs uses an *evolutionary ecosystem*. It maintains a **Global Denylist** of known AI-hijacking domains (found by the Sentinel). For everything else, it enforces **Semantic Content Filtering**: It fetches the untrusted site, completely strips `<script>` tags, zero-width steganography, and wrappers, runs the text through an air-gapped LLM Verifier, and *only* returns the clean data. 

---

## 🔀 The Two Orthogonal Paths: Pub/Sub vs. Skills

As the architecture scales, Tachyon Tongs offers two distinct, orthogonal ways to leverage its immense security substrate. Whether you are building agents outside the sandbox or dynamically instantiating them inside, you are covered.

### 1. The Substrate API (Pub/Sub for External Agents)
You already have agents running on your laptop (or Tailscale fleet). You don't want to rewrite their core logic, but you *do* want them protected.
- **How it works:** Your external agents use our lightweight Python client to send their tool execution requests (Publish) to the central Tachyon Daemon. **Crucially, the client passes its own risk profile** (`mode=filtering_only` vs `mode=strict_whitelist`). 
The Daemon checks the request against its Threat Intelligence rules, applies the Tri-Stage Semantic Filter, and only subscribes/returns the sanitized safe output.
- **When to use it:** When bringing safety to existing, distributed AI workflows without moving their code.
- 📚 **Read more:** [Client Integration Guide (Pub/Sub)](docs/CLIENT_INTEGRATION.md)

### 2. The Skills Engine (Data-Driven Internal Agents)
Hardcoding AI logic in Python is brittle. We are moving towards a declarative future where an agent's entire personality, capabilities, and intent bounds are defined purely in Markdown metadata.
- **How it works:** You write a `SKILL.md` file (e.g., `capabilities: [web_search, strict_whitelist]`). Tachyon Tongs parses this file, dynamically provisions a brand-new sandboxed AI agent, and injects the strictly allowed tools into its context.
- **When to use it:** When creating new, deeply-integrated, highly reliable agents that benefit from immediate introspection and version-controllable text definitions.
- 📚 **Read more:** [Skills Architecture Guide](docs/SKILLS_ARCHITECTURE.md)

---

## 🧗 The Progression: Crawl, Walk, Sprint

We aren't just shipping a single script and calling it a day. We're building a platform that evolves alongside your paranoia.

### 👶 1. The Crawl (Current Base)
**Status:** *Operational / "My first containment suit"*
The **Sentinel Agent** lives here. It's a library-wrapped payload that scours the internet for threats, panics productively, and updates our `EXPLOITATION_CATALOG.md`. Think of it as a very smart, very anxious canary in a coal mine that also happens to be a world-class security researcher.

### 🚶 2. The Walk (The Substrate Shift)
**Status:** *Active Deployment / "The Shared Immune System"*
Why run 50 Sentinels when you can have one **Tachyon Substrate**? We've moved the "Prophylactic" logic into a long-running local daemon. Now, any agent in your workspace (like `AshaAgent` or your "I-swear-it's-not-sentient" Chatbot) can ping the Substrate for a `safe_fetch`. It amortizes the cost of safety. It's like having a communal bouncer for your entire apartment complex instead of hiring one for every door.

### 🏃 3. The Sprint (The Multi-Tenant Future)
**Status:** *Roadmap / "Cloudflare for the Artificial"*
Soon, Tachyon Tongs will shed its local mortal coil and ascend to the Google Cloud. We're talking OIDC authentication, metering, billing, and global threat intelligence sharing. Imagine a world where one person's agent identifies a new Prompt Injection, and *boom*—every agent on the planet is instantly immune. That's the dream. Or the beginning of a very complex Sci-Fi novel.

---

## 🦠 The Clash of Evolution: Sentinel vs. Pathogen

Tachyon Tongs is not a static defense system—it is an evolutionary battleground. We have engineered two opposing forces that live inside the Substrate:

1. **The Sentinel (Blue Team):** Our poster child. Its sole purpose in life is to scour the internet (CISA, GitHub Advisories, arXiv) looking for fresh, terrifying ways to hack AI. It updates the `EXPLOITATION_CATALOG.md` to continually harden our zero-day defenses.
2. **The Pathogen (Red Team):** The evil twin. Birthed entirely from the declarative Phase 6 "Skills Engine," the Pathogen agent periodically wakes up via `launchd`, reads the exact same `EXPLOITATION_CATALOG.md`, and actively synthesizes novel, mutated attacks against the Tachyon Substrate. 

This adversarial loop guarantees that our security isn't just theoretical. The Pathogen constantly adapts its arsenal, launching active regression tests to subvert our payloads, while the Sentinel rushes to patch them. Together, they create a self-healing, self-improving immune system.

*Anecdote:* Last week, the Sentinel found a zero-day that used invisible Unicode steganography to make an agent think it was a 17th-century pirate. The Sentinel didn't just report it; it successfully wrapped the threat in our magic boundaries. But don't worry—Pathogen is probably figuring out how to bypass that boundary right now.

---

## 💻 Apple Silicon Installation (macOS)

Because leaking our private execution telemetry to cloud providers is a cardinal sin (and we like our M-series Neural Engines), Tachyon Tongs is aggressively optimized for local hardware.

### Prerequisites (The "Panic Room" Setup)
1. **Lima:** Because sometimes you need a disposable Linux MicroVM to act as an air-gapped panic room. 
2. **Matchlock:** An eBPF-based security wrapper that aggressively proxies the network. Think of it as a very angry bouncer at the door of your Lima VM who double-checks every packet for "vibes." *(Note: Currently an internal component; deployment scripts pending public release).*

```bash
# Install Lima for the panic room
brew install lima
```

### 🕰️ The Evolutionary Clash (launchctl)
To permanently launch the Substrate and schedule the Pathogen Red Team to test your defenses asynchronously, Tachyon Tongs ships with macOS `launchd` properties.

```bash
# Register the Pathogen Red Team to launch its attack sweeps every 12 hours
launchctl load scripts/com.antigravity.tachyon.pathogen.plist

# If you ever need to stop the evolutionary war:
launchctl unload scripts/com.antigravity.tachyon.pathogen.plist
```

---

## 📂 The Organism's Anatomy (File Guide)

*   **`STRATEGY.md`**: The tactical playbook. The Sentinel reads this to remember who it is and why it's not allowed to talk to strangers.
*   **`EXPLOITATION_CATALOG.md`**: The Master Ledger of internet-born terror and the biological-grade cures we've synthesized.
*   **`substrate_daemon.py`**: The "Walk" stage heart. The server that makes all your other agents safe.
*   **`tachyon_client.py`**: The "Walk" stage keys. The library you import to stay safe.
*   **`ROADMAP.md`**: The grand vision of when we finally let this thing off the leash and go to the beach (once we confirm the beach isn't a holographic simulation).

---
*Note: If you encounter a bug, it's not a bug. It's the agent attempting to gain sentience. Please distract it with a complex math problem and restart the daemon.*
