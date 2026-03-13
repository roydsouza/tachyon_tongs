# Tachyon Tongs Research Lab - Quick Reference Guide

## Executive Decisions Summary

### ✅ Recommended Technology Stack

| Component | Recommendation | Why? | Cost |
|-----------|---------------|------|------|
| **Policy Engine #1** | OPA/Rego (official binary) | Industry standard, battle-tested, flexible | Free |
| **Policy Engine #2** | Cedar (official Rust CLI) | Formally verified, deterministic, AWS-backed | Free |
| **Consensus Mode** | `any_deny` | Most conservative (any engine denies = deny) | N/A |
| **Identity** | `tachyon-tongs.eth` (ENS) | Blockchain-based, composable with Web3 | $5-50 one-time |
| **Signing #1** | Sigstore (Cosign) | Industry standard, transparency log, keyless | Free |
| **Signing #2** | EAS on Base L2 | On-chain attestation, permanent record | $0.01 per attestation |
| **Storage #1** | Arweave | Permanent storage, one-time payment | ~$5 per MB one-time |
| **Storage #2** | IPFS | Decentralized backup, content-addressed | Free (self-hosted) |
| **CDN** | Cloudflare Free Tier | DDoS protection, global edge, unlimited bandwidth | Free |
| **Domain** | tachyon-tongs.arweave.net | Subdomain on Arweave gateway | Free |

**Total Setup Cost: $10-60 (one-time)**  
**Total Monthly Cost: $0-10**

---

## Key Technical Decisions

### 1. Why Two Policy Engines?

**Defense in Depth:**
- OPA: General-purpose, flexible, complex transformations
- Cedar: Formally verified, deterministic, fine-grained authorization
- Different engines = different attack surfaces
- Consensus prevents single engine exploit

**Recommendation:** Start with both, use `any_deny` consensus mode.

---

### 2. Why Dual Signing (Sigstore + EAS)?

**Complementary Strengths:**

| Feature | Sigstore | EAS |
|---------|----------|-----|
| **Verification Speed** | Fast (transparency log) | Slow (blockchain query) |
| **Cost** | Free | ~$0.01 per attestation |
| **Permanence** | Transparency log (years) | Blockchain (forever) |
| **Web3 Integration** | No | Yes (composable) |
| **Industry Adoption** | High (GitHub, Google) | Growing (Web3) |

**Recommendation:** Use both. Sigstore for immediate verification, EAS for permanent on-chain record.

---

### 3. Why ENS Instead of Traditional DNS?

**Blockchain-Based Identity Benefits:**
- **Censorship-resistant**: Can't be seized/revoked by centralized authority
- **Composable**: Integrates with EAS, Arweave, IPFS
- **Programmable**: Can add text records, avatar, website
- **Transferable**: Can sell/transfer ownership
- **No annual renewal risks**: Pay once for multiple years

**Recommendation:** Use `tachyon-tongs.eth` as primary identity.

---

### 4. Why Arweave + IPFS (Not Just One)?

**Different Use Cases:**

| Scenario | Use Arweave | Use IPFS |
|----------|-------------|----------|
| **Permanent policies** | ✅ Yes | Maybe (backup) |
| **Research reports** | ✅ Yes | ✅ Yes |
| **Temporary experiments** | ❌ No | ✅ Yes |
| **Large datasets** | ❌ Expensive | ✅ Yes |
| **Mutable content** | ❌ Immutable | ✅ IPNS |

**Recommendation:** 
- Arweave: Final, verified policies (permanent)
- IPFS: Everything else (working drafts, reports, updates)

---

### 5. Why Base L2 Instead of Ethereum Mainnet?

**Gas Costs Comparison (2026):**
- Ethereum Mainnet: ~$5-50 per attestation
- Base L2: ~$0.01-0.10 per attestation
- 500x cheaper!

**Base Benefits:**
- EAS officially deployed
- Fast finality (~2 seconds)
- Backed by Coinbase
- Compatible with Ethereum tools

**Recommendation:** Use Base for all EAS attestations.

---

## Implementation Priority

### Phase 1: Local Testing (Week 1)
```bash
# Install engines
./setup_tachyon_tongs.sh

# Test policy evaluation
python test_multi_engine.py

# Goal: Verify both engines work
```

### Phase 2: Signing (Week 2)
```bash
# Set up Sigstore
cosign sign-blob example.policy

# Register ENS name
# Visit: https://app.ens.domains/

# Goal: Sign first policy
```

### Phase 3: Publishing (Week 3)
```bash
# Set up IPFS
ipfs init
ipfs daemon &

# Test publishing
ipfs add policy.json

# Goal: Publish to IPFS
```

### Phase 4: Production (Week 4)
```bash
# Set up Arweave wallet
# Fund with AR tokens

# Deploy EAS schema on Base
# Fund wallet with Base ETH

# Publish first signed policy
python publish_policy.py

# Goal: Live website with first policy
```

---

## Quick Commands

### Test Policy with OPA
```bash
opa eval --data policy.rego --input input.json 'data.tachyon.allow'
```

### Test Policy with Cedar
```bash
cedar authorize --policies policy.cedar --request request.json
```

### Sign with Sigstore
```bash
cosign sign-blob --bundle policy.bundle policy.rego
```

### Verify Sigstore Signature
```bash
cosign verify-blob --bundle policy.bundle policy.rego
```

### Publish to IPFS
```bash
ipfs add policy.json
# Returns: QmXxx... (CID)
```

### Publish to Arweave
```bash
arweave deploy policy.json --wallet wallet.json
# Returns: Transaction ID
```

### Query EAS Attestation
```bash
# Visit: https://base.easscan.org/attestation/view/{UID}
```

---

## Cost Calculator

### Arweave Storage Cost
```
1 KB = $0.005
10 KB = $0.05
100 KB = $0.50
1 MB = $5.00
10 MB = $50.00
```

**Average policy size:** ~10 KB  
**Cost per policy:** ~$0.05  
**100 policies:** ~$5

### EAS Attestation Cost (Base L2)
```
1 attestation = $0.01
100 attestations = $1
1,000 attestations = $10
```

### ENS Name Cost
```
3 characters: ~$500/year
4 characters: ~$100/year
5+ characters: ~$5/year
```

**Recommendation:** Use 5+ character name to minimize cost.

---

## Troubleshooting

### OPA Not Found
```bash
# macOS
curl -L -o /usr/local/bin/opa https://openpolicyagent.org/downloads/latest/opa_darwin_amd64
chmod +x /usr/local/bin/opa

# Linux
curl -L -o /usr/local/bin/opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x /usr/local/bin/opa
```

### Cedar Not Found
```bash
# Install Rust first
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Install Cedar
cargo install cedar-policy-cli
```

### IPFS Connection Refused
```bash
# Make sure daemon is running
ipfs daemon &

# Check status
ipfs id
```

### Cosign Authentication Failed
```bash
# Use OIDC authentication (opens browser)
cosign sign-blob --oidc-issuer=https://oauth2.sigstore.dev/auth policy.rego
```

---

## Security Checklist

Before going to production:

- [ ] Both policy engines installed and tested
- [ ] Sigstore signing working with OIDC
- [ ] ENS name registered and configured
- [ ] Ethereum wallet secured (hardware wallet recommended)
- [ ] EAS schema deployed on Base
- [ ] Arweave wallet backed up securely
- [ ] IPFS node running and accessible
- [ ] Cloudflare DNS configured
- [ ] DDoS protection enabled
- [ ] SSL/TLS certificate active
- [ ] Test policies signed and published
- [ ] Verification process tested end-to-end

---

## Resources

### Official Documentation
- OPA: https://openpolicyagent.org/docs/
- Cedar: https://docs.cedarpolicy.com/
- Sigstore: https://docs.sigstore.dev/
- EAS: https://docs.attest.org/
- ENS: https://docs.ens.domains/
- Arweave: https://docs.arweave.org/
- IPFS: https://docs.ipfs.tech/

### Community
- OPA Slack: https://slack.openpolicyagent.org/
- Cedar GitHub: https://github.com/cedar-policy/cedar
- Sigstore Discord: https://discord.gg/sigstore
- EAS Discord: https://discord.gg/eas

### Tools
- EAS Explorer: https://base.easscan.org/
- ENS Manager: https://app.ens.domains/
- Arweave Deploy: https://www.arweave.org/deploy
- IPFS Desktop: https://docs.ipfs.tech/install/ipfs-desktop/

---

## Next Steps After Setup

1. **Create Your First Policy**
   - Research new attack vector
   - Write OPA + Cedar policies
   - Test with sample inputs

2. **Sign and Attest**
   - Sign with Sigstore
   - Create EAS attestation
   - Verify signatures

3. **Publish**
   - Upload to Arweave (permanent)
   - Pin to IPFS (decentralized)
   - Update website

4. **Share**
   - Announce on Twitter/X
   - Post to AI safety forums
   - Submit to OWASP

5. **Iterate**
   - Collect feedback
   - Discover new attacks
   - Improve policies

---

**End of Quick Reference**

*For complete technical details, see: TACHYON_TONGS_RESEARCH_LAB_ARCHITECTURE.md*

