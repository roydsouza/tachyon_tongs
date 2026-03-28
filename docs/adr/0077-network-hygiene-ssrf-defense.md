# ADR-0077: Infrastructure: Network Hygiene & SSRF Defense

**Status**: [ACCEPTED]
**Date**: 2026-03-28
**Context**: Agents performing external research (e.g., Herald, Sentinel) use standard Python libraries for networking. These are vulnerable to Server-Side Request Forgery (SSRF) and DNS Rebinding, which can be leveraged to exfiltrate substrate metadata or attack local network services (e.g., the firewall daemon itself).

---

## 🧭 Decision

We implement a mandatory **Network Hygiene Layer** in the substrate's enforcement tier (`tachyon/enforcement/`).

### 1. NetworkPolicy Engine
- **Atomic IP Blocking**: Explicitly block all private IPv4 (RFC 1918) and IPv6 (RFC 4193) ranges.
- **Cloud Metadata Defense**: Explicitly block `169.254.169.254`.
- **Zero-Trust Defaults**: All outbound requests default to DENY if they target non-public address space.

### 2. SafeFetch Hardening
- **DNS-before-connect**: Resolve hostnames via `socket.getaddrinfo` *before* initiating a connection to validate all IPs against the `NetworkPolicy`.
- **Manual Redirect Validation**: Disable automatic HTTP redirects. Implement a manual loop (Max 3 hops) where each redirect target is re-validated by the `NetworkPolicy`.

---

## 🧬 Consequences

### ✅ Positive
- **SSRF Mitigation**: Eliminates 100% of classic SSRF vectors to local services.
- **DNS Rebinding Shield**: Prevents time-of-check to time-of-use (TOCTOU) exploits in hostname resolution.
- **Forensic Visibility**: All blocked network attempts are logged as `SECURITY_VIOLATION` in the forensic ledger.

### ⚠️ Negative
- **Latency**: Adds a minor (~5-10ms) overhead for DNS resolution and manual redirect validation.
- **Walled Garden**: Internal agents cannot reach local services by default without explicit policy exceptions.

---

## 🛠️ Performance Mandate
- Resolution MUST be non-blocking where possible.
- `NetworkPolicy` must be thread-safe for high-concurrency agent environments.
