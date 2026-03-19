# 🚷 Tachyon Tongs: Paths Not Taken Ledger

This ledger documents architectural paths and design decisions that were explicitly **rejected** due to security risks, suboptimal reasoning, or operational fragility.

## 🗄️ Rejected Paths

### ❌ Plain SHA-256 for Architectural Integrity (ADR-0001–0015 Legacy)
- **Date Rejected**: 2026-03-18
- **Reason**: Standard SHA-256 hashes are susceptible to collision attacks (long-term) and do not provide the attribution/authentication benefits of a keyed HMAC. 
- **Decision**: Upgraded the substrate to **High-Assurance HVAC (HMAC)** using `TACHYON_SECRET_KEY` to ensure only the authorized substrate operator can mutate architectural records.
- **Risk of Revisit**: High. Future agents might attempt to simplify the code by reverting to plain hashes.

### ❌ In-Stream Prompt Sanitization at the LLM Level Only
- **Date Rejected**: 2026-03-18
- **Reason**: Relying on "System Prompt Guidance" alone to avoid injection is inherently vulnerable to latent instruction activation.
- **Decision**: Implemented the **InputSanitizer** layer as a pre-policy gate (NFKC normalization + regex scrubbing).
- **Risk of Revisit**: Extreme. Prompt injection remains the primary attack vector for agentic systems.

---
*Next rejection here.*


## Integrity Attestation


