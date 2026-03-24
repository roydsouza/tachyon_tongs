# ADR-0043: Fail-Closed PQC Mandate & Model Integrity

## Status
Proposed

## Context
As Tachyon Tongs moves toward autonomous agentic operation, the integrity of both the code and the model weights becomes paramount. 
1. **Strip Attacks**: An adversary might remove the PQC layer from a hybrid signature, forcing a fallback to classical Ed25519. We must ensure that if PQC is configured, its absence is a terminal failure.
2. **Model Poisoning**: Unauthorized modification of local model weights (e.g., MLX LoRA adapters) can subtly shift agent alignment.

## Decision
1. **PQC Mandate**: Implement a `TACHYON_PQC_STRICT` environment variable. When set, `HybridSigner` will raise a `RuntimeError` if a signature lacks the `mldsa65:` prefix, even if `liboqs` is unavailable.
2. **Model Warden**: Create a `ModelIntegrityWarden` that performs cryptographic hashing of specific model directories. These hashes will be signed by the Root PQC identity and checked on every substrate boot.

## Consequences
- **Security**: Eliminates the "classical fallback" bypass vector.
- **Reliability**: Prevents execution with compromised model weights.
- **Operational**: Setting `STRICT` mode in an environment without `liboqs` but with existing PQC keys will result in immediate halts (desired fail-closed behavior).
