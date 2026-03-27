# ADR-0027: Hardware-Level Isolation Protocol

## Status
Proposed

## Context
As the Tachyon Tongs substrate evolves toward autonomic self-healing (Phase 22), the risk of "Substrate Escape"—where synthesized code or agent tool-calls interact with the host OS in unintended ways—increases. Software-defined policies (Rego/Cedar) are necessary but insufficient for a high-assurance Trusted Computing Base (TCB). We require physical boundaries provided by hardware virtualization to isolate untrusted execution.

## Decision
We will implement a **Tiered Hardware Isolation Protocol** optimized for the Apple Silicon M5.

### Tier 1: Deterministic Sandboxing (WASM)
- **Target**: Pure data transformations, log parsers, and side-effect-free tools.
- **Technology**: `wasmtime` (via `wasmtime-py`).
- **Isolation**: Memory-safe, capability-based security. No filesystem or network access unless explicitly granted via WASI.

### Tier 0: Agent-Level Isolation (MicroVM)
- **Target**: High-privilege agents (Sentinel, Engineer) and tools requiring filesystem/network access.
- **Technology**: Apple `Virtualization.framework` (via `lima` or `tart`).
- **Isolation**: Full hardware virtualization with a minimal Linux kernel. I/O is restricted to encrypted virtio-serial channels.

### Root of Trust (SEP)
- **Anchor**: Investigation into anchoring the substrate's Merkle root in the Apple Silicon **Secure Enclave (SEP)** to prevent offline tampering with the integrity manifest.

## Consequences
- **Security**: Significantly reduced attack surface; defense-in-depth against RCE.
- **Performance**: Near-native speed on M5 due to hardware virtualization extensions (VHE).
- **Complexity**: Increased deployment requirements (requires `wasmtime` and `lima` on the host).

---
*Signed by: Sentinel Agent*
*Date: 2026-03-20*


## Integrity Attestation

```json
{
  "adr_id": "ADR-0027",
  "hash": "sha256:d1d1a2006c1be220232cd94591458d52dc0a9bb2c4f9cb486ee54ded37c6099a",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
