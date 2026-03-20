# Tachyon Tongs: Genesis & Recovery Ceremony Guide

This guide walks you through the two most critical cryptographic operations in the Tachyon Tongs substrate: **Genesis** (creation of the Root of Trust) and **Resurrection** (recovery from backup).

---

## 1. Prerequisites

1. **Hardware**: Apple Silicon Mac (M1/M2/M3/M4/M5).
2. **Environment**: Ensure `TACHYON_STRICT_MODE=1` is set.
3. **CLI Access**: `tt` must be installed (`pip install -e .`).
4. **Physical Prep**: Have your 5 cold-storage locations ready:
   - 1Password / Passkey vault
   - YubiKey / HSM
   - Physical Safe / Lockbox
   - Encrypted Cloud Storage
   - Paper/Printer for QR backup

---

## 2. The Genesis Ceremony (Initial Setup)

Run this **exactly once** to establish your hardware-backed root of trust.

### Step 1: Initiate
```bash
tt keys genesis
```

### Step 2: Biometric Anchor
The system will prompt for **Touch ID**. This anchor binds the generated Ed25519 key to your Secure Enclave hardware.

### Step 3: Secret Distribution
The terminal will display 5 masked shares. 
- Use the arrow keys to select a share.
- Press **Enter** to reveal the share (masking it again after 30 seconds).
- **Copy and store each share** in your 5 separate locations immediately.

> [!CAUTION]
> **This is a one-time event.** The substrate does not save these shares. If you close the terminal before saving them, you must wipe the substrate and start over.

---

## 3. The Resurrection Ceremony (Recovery)

Run this if you move to a new laptop or your current Secure Enclave is wiped.

### Step 1: Collection
Retrieve any **3 of your 5 shares** from their storage locations.

### Step 2: Initiate Recovery
```bash
tt keys recovery
```

### Step 3: Input
Paste the 3 shares when prompted. The substrate will reconstruct the seed in ephemeral memory.

### Step 4: Hardware Import
The substrate will re-derive the Ed25519 key and attempt to import it into the local Secure Enclave.
- If a key with the same name exists, macOS will prompt to **Overwrite**.

### Step 5: The Signing Check (Success)
The script will automatically perform a signature test against the public key on GitHub.
```text
[✓] Reconstructing seed...
[✓] Importing to Secure Enclave...
[✓] Cryptographic Challenge: 32 bytes
[✓] Signature Verification: PASS
[✓] Status: SIGN_OK - ROOT OF TRUST RESTORED
```

---

## 4. Operational Troubleshooting

### "Label Collision" Error
If you see `Error: CSSM_ERRCODE_DUPLICATE_ITEM`, it means the Secure Enclave already holds a Tachyon Root Key. Use `tt keys status` to verify the existing key's fingerprint before overwriting.

### "Insufficient Shares"
If only 2 shares are provided, the math of Shamir's Secret Sharing ensures **nothing** can be recovered. You must find a 3rd share.

---
**Secure Software Development Lifecycle**
*Protect the Seed. Trust the Chain.*
