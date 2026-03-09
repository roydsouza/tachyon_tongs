# 🖧 Tachyon Tongs: The Zero-Trust VPN Rant (Tailscale)

> *"IP-based firewalls are like putting a 'Keep Out' sign on a screen door in a hurricane. Math is better." - Ancient DevOps Proverb*

Let's talk about networking. If our Analyzer LLM gets hijacked by a malicious payload and decides it wants to pivot into our local network to mine crypto or play Doom on the smart fridge, we have a problem. 

To prevent this, Tachyon Tongs uses **Tailscale** as an eBPF/Wireguard sidecar inside the Matchlock/Lima sandbox. 

## The Intent (Why We Do This)

The goal here is simple: **Replace IP addresses with cryptographic identity.** 

If the agent escapes the Phase 1 and 2 Intent Gates (meaning it outsmarted our Regex and our capability tokens), it breaks out into... an encrypted, permission-less void. Every single outward packet it tries to send is silently dropped into a black hole unless it is mathematically authenticated. 

## The Architecture (How It Works)

We shoved Tailscale deep into the Prophylactic layer. Here is the anatomy of the trap:

### 1. The Lima Panic Room (`matchlock-agent.yaml`)
When the MicroVM boots up, it installs the Tailscale daemon right next to the `matchlock` proxy. 
It authenticates completely headless using an **Ephemeral Auth Key**. Why ephemeral? Because when the VM gets scorched (destroyed after executing a toxic payload), the node is automatically purged from the Tailnet. 
*No zombie access allowed. The bouncer throws you out and burns your VIP card.*

### 2. Machine-to-Machine Identity (Tailnet ACLs)
The Agent's instance gets slapped with a nametag (e.g., `tag:tachyon-sentinel`). 
In the Amin Console, we write ACLs that treat the agent like a toddler:
```jsonc
// The Agent can ONLY talk to the Knowledge Base and the Code Repo. 
// It cannot talk to the internet, your printer, or God.
{
  "action": "accept", 
  "src": ["tag:tachyon-sentinel"], 
  "dst": ["tag:internal-kb:443", "tag:internal-gitlab:22"]
}
```

### 3. The Rego Override (`tool_access.rego`)
Our Open Policy Agent (OPA) firewall is configured to block *all* `0.0.0.0/0` outbound traffic by default because the public internet is a scary place. 
Instead, it relies on **MagicDNS**. The `safe_fetch` node connects natively to things like `https://internal-wiki.tailnet-name.ts.net`. 

## 🚨 SOS: Don't Panic (Troubleshooting)

| Symptom | Probable (Silly) Reality | The Fix |
| :--- | :--- | :--- |
| **"MicroVM won't boot / exits immediately!"** | You forgot to export your `TS_AUTHKEY` and the script panicked. | Run `export TS_AUTHKEY='tskey-auth-XYZ'` before running the Lima start block. |
| **"The Agent can't reach the internal wiki!"** | MagicDNS isn't enabled on your Tailnet or the ACL dropped the packet. | Check your Tailscale Admin console. Did you tag the VM correctly? Does it have rights? |
| **"I can ping google.com from inside the VM!"** | You didn't load the Matchlock profile or the Rego policy is misconfigured. | Panic slightly. Then fix the `tool_access.rego` wildcard block. |

## Implemented Reality

Because we actually listen to our own architectural riders, here is exactly what is running in the codebase right now:

1.  **Auth Wrapper (`scripts/tailscale-auth.sh`)**: A bash script that yells at you if you haven't set the `TS_AUTHKEY` environment variable. We do this so the key isn't hardcoded into YAML for the entire internet to steal.
2.  **Daemon Injection (`scripts/matchlock-agent.yaml`)**: The provision block curls the installer and runs literally this: 
    `tailscale up --authkey=${TS_AUTHKEY} --hostname=tachyon-sentinel --accept-routes`
3.  **Rego MagicDNS (`policies/tool_access.rego`)**: Permits the `.ts.net` MagicDNS wildcard.

> [!NOTE]
> **Rider Fulfilled:** This document was updated by AntiGravity to map perfectly to the live infrastructure configuration. We didn't just write a design doc and forget about it. Who do you think we are?
