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

## Planned Implementation

The implementation strategy dictates that `TAILSCALE.md` must remain the single source of truth for the network topology.

- **Phase 1:** Generate Ephemeral Auth tokens via an OAuth client specifically for the Limactl instance.
- **Phase 2:** Inject the daemon daemon installation steps into `scripts/matchlock-agent.yaml`.
- **Phase 3:** Rewrite `tool_access.rego` to block public web traversing and test internal routing.

> [!IMPORTANT]
> **Implementation Rider:** Upon completion of this integration, the executor *must* update this `TAILSCALE.md` file to reflect any deviations from the original plan, the actual ACL schemas used, and the precise MagicDNS configurations generated. Always maintain parity between this document and the live deployment.
