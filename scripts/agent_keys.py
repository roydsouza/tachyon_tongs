#!/usr/bin/env python3
import os
import sys
import json
import base64
import hashlib
import argparse
from datetime import datetime

# Ensure project root is in path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from tachyon.core.signing import IntegrityManager
from tachyon.core.keys.certificates import DelegationCertificateAuthority

def cmd_status(im):
    print("--- 🏛️ Tachyon Key Hierarchy Status ---")
    
    # 1. Root Identity
    root_pub = im._public_key.public_bytes_raw().hex() if im._public_key else "UNKNOWN"
    root_fingerprint = hashlib.sha256(im._public_key.public_bytes_raw()).hexdigest()[:16] if im._public_key else "UNKNOWN"
    print(f"[ROOT] Fingerprint: {root_fingerprint}")
    print(f"[ROOT] Public Key (Ed25519): {root_pub[:32]}...")
    print(f"[ROOT] PQC Status: {'ML-DSA-65 Active' if im._pqc_private_key_bytes else 'Inactive'}")
    print("-" * 40)
    
    # 2. Delegated Identities
    keys_dir = os.path.join(root_dir, "memory", "keys")
    if not os.path.exists(keys_dir):
        print("No delegated identities found.")
        return

    print(f"{'ROLE':<15} {'FINGERPRINT':<20} {'EXPIRES'}")
    for f in os.listdir(keys_dir):
        if f.startswith("agent_") and f.endswith(".json"):
            try:
                # Use the passed IntegrityManager im
                from tachyon.core.keys.certificates import DelegationCertificateAuthority
                with open(os.path.join(keys_dir, f), "r") as jf:
                    data = json.load(jf)
                cert = data.get("certificate", {})
                payload = cert.get("payload", {})
                subject = payload.get("subject", {})
                
                role = subject.get("role", "unknown")
                fingerprint = subject.get("fingerprint", "unknown")
                expires = payload.get("expires_at", "unknown")
                
                # Check status
                ca = DelegationCertificateAuthority(im)
                is_valid, reason = ca.validate_certificate(cert)
                status_icon = "✅" if is_valid else "❌"
                
                print(f"{role:<15} {fingerprint:<20} {expires[:10]} {status_icon}")
            except Exception as e:
                print(f"Error reading {f}: {e}")

def cmd_delegate(im, role, expiry):
    print(f"[*] Ritual: Deriving sub-key for role '{role}'...")
    try:
        _, cert = im.derive_agent_key(role, save_to_disk=True)
        print(f"✅ Delegation Successful.")
        print(f"[*] Certificate valid until: {cert['payload']['expires_at']}")
    except Exception as e:
        print(f"❌ Delegation Failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Tachyon Tongs: Key Hierarchy Manager")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")
    
    subparsers.add_parser("status", help="Show root and delegated key status")
    
    delegate_parser = subparsers.add_parser("delegate", help="Issue a new delegated identity")
    delegate_parser.add_argument("--role", required=True, help="Agent role (e.g., sentinel, engineer)")
    delegate_parser.add_argument("--expiry", type=int, default=30, help="Expiry in days")
    
    verify_parser = subparsers.add_parser("verify", help="Manually verify a certificate file")
    verify_parser.add_argument("--path", required=True, help="Path to the agent_[role].json file")

    args = parser.parse_args()
    
    im = IntegrityManager()
    
    if args.command == "status":
        cmd_status(im)
    elif args.command == "delegate":
        cmd_delegate(im, args.role, args.expiry)
    elif args.command == "verify":
        if not os.path.exists(args.path):
            print(f"Error: File not found {args.path}")
            return
        with open(args.path, "r") as f:
            data = json.load(f)
        cert = data.get("certificate", data) # Handle both raw cert and identity wrapper
        ca = DelegationCertificateAuthority(im)
        is_valid, reason = ca.validate_certificate(cert)
        if is_valid:
            print(f"✅ Certificate is VALID: {reason}")
        else:
            print(f"❌ Certificate is INVALID: {reason}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
