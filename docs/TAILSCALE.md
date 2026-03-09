# 🖧 Tachyon Tongs: Tailscale Zero-Trust Overlay (Proposed)

To ensure the Tachyon Tongs architecture can securely access isolated internal network nodes, internal vector databases, or private code repositories without exposing the Agent to the public internet, we propose integrating **Tailscale** as an eBPF/Wireguard sidecar within the hardware-virtualized Matchlock/Lima sandbox.

## Intent

The core objective is to replace traditional IP-based ingress/egress firewall rules with **cryptographic identity**. If a threat successfully compromises the Analyzer LLM and executes a sandbox escape (bypassing Phase 1 and 2 Intent Gates), it should find itself trapped in an encrypted, permission-less subnet where every outward packet is dropped unless mathematically authenticated.

## The Architecture

Tachyon Tongs will implement Tailscale deep in the Prophylactic layer:

1.  **The Lima Initialization (`matchlock-agent.yaml`)**:
    *   The MicroVM provisioning script will install the Tailscale daemon alongside the `matchlock` proxy.
    *   The VM will authenticate headless using a short-lived, **Ephemeral Auth Key**. 
    *   When the virtual machine is destroyed or recreated after a toxic payload execution, the ephemeral node is automatically purged from the Tailnet to prevent zombie access.

2.  **Machine-to-Machine Identity (Tailnet ACLs)**:
    *   The Agent's instance will be automatically tagged (e.g., `tag:tachyon-sentinel`).
    *   The Admin Console ACLs will strictly define behavior: 
        ```jsonc
        // The Agent can ONLY talk to the Internal Knowledge Base and the Code Repository, and NOTHING else.
        {
          "action": "accept", 
          "src": ["tag:tachyon-sentinel"], 
          "dst": ["tag:internal-kb:443", "tag:internal-gitlab:22"]
        }
        ```

3.  **The Rego Override (`tool_access.rego`)**:
    *   The Open Policy Agent (OPA) egress firewall will be reconfigured. Instead of broadly allowing URLs, it will rely on **MagicDNS**.
    *   The firewall will drop all `0.0.0.0/0` outbound traffic by default.
    *   The `safe_fetch` node will connect natively to `https://internal-wiki.tailnet-name.ts.net`.

## Implemented Architecture

The Zero-Trust network has been formally integrated into the repository:

1.  **Auth Wrapper (`scripts/tailscale-auth.sh`)**: We created a bash wrapper to ensure the `TS_AUTHKEY` environment variable is present on the host machine before booting the VM. This prevents secret leakage in YAML.
2.  **Daemon Injection (`scripts/matchlock-agent.yaml`)**: The Lima provision block invokes the Tailscale install script and executes:
    `tailscale up --authkey=${TS_AUTHKEY} --hostname=tachyon-sentinel --accept-routes`
3.  **Rego MagicDNS (`policies/tool_access.rego`)**: The firewall now explictly permits the `.ts.net` MagicDNS wildcard, allowing the Fetcher node to resolve internal Tailscale nodes without hardcoded IPs.

> [!NOTE]
> **Rider Fulfilled:** This document was updated during the Phase 4 execution sequence to map perfectly to the live infrastructure configuration.
