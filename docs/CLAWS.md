# 🦞 Claw Compatibility: The Ecosystem Bridge

Tachyon Tongs provides a **secure import pipeline** that allows operators to leverage the 5,700+ agent skills from the ClawHub ecosystem while maintaining strict security-first principles.

## 🏗️ Architecture: The 5-Stage Vetting Pipeline

To ensure that imported "Claws" do not compromise the substrate, every import follows a mandatory multi-stage vetting process:

1.  **Stage 1: Format Translation**: Converts Claw structure (`SOUL.md`, `HEARTBEAT.md`, `WORKING.md`) into Tachyon's standardized `config.yaml` and `SKILL.md` format.
2.  **Stage 2: Static Analysis**: Scans the translated agent for dangerous capability requests, shell-execution patterns, and unrestricted network intents.
3.  **Stage 3: Canary Sandbox Test**: Executes the agent within a strictly isolated, ephemeral environment to observe runtime behavior and resource consumption.
4.  **Stage 4: Airlock Review**: Stages the agent and its security report for a manual "Airlock Debate." A human operator or the **Skeptic** agent must explicitly authorize deployment.
5.  **Stage 5: Quarantine Deployment**: Initially deploys the agent with "Read-Only" capabilities and strict rate limits. Capabilities are graduated only after a successful observation period.

## 🛠️ Usage: The Import Utility

Operators can import Claws using the unified import script:

```bash
# Import from a local Claw directory
python scripts/import_claw_agent.py --source /path/to/claw-agent --name my-specialist

# Review the import in the Airlock
tt airlock review CLAW-MY-SPECIALIST-a3f4b
```

## 🔐 Why it's Secure
Unlike running Claws natively, Tachyon Tongs wraps every imported agent in the **Substrate Firewall**:
- **Capability Gating**: Even if a Claw *claims* to have network access, the Tachyon PDP can hard-block it via Rego policy.
- **Intent Scrubbing**: All LLM-generated intents are filtered through the **Guardian Triad** to prevent prompt-injection escalation.
- **Forensic Auditing**: Every action is cryptographically signed and logged to `EVOLUTION.md`.

---
> [!TIP]
> Use Claws for specialized tasks (e.g., specific language translation, weather analysis) while keeping the core Tachyon agents for substrate-critical security roles.
