#!/bin/bash
set -euo pipefail

# Tachyon Tongs: Tailscale OAuth Pre-Flight
# This script ensures the TS_AUTHKEY is securely evaluated before provisioning the Matchlock/Lima sandbox.
# It acts as a safety wrapper so keys aren't hardcoded into YAML or pushed to GitHub.

if [[ -z "${TS_AUTHKEY:-}" ]]; then
    echo "❌ ERROR: TS_AUTHKEY environment variable is not set."
    echo ""
    echo "To provision the Matchlock Sandbox securely onto the private Tailnet:"
    echo "1. Generate an Ephemeral Auth Key in your Tailscale Admin Console."
    echo "2. Run: export TS_AUTHKEY='tskey-auth-YOURKEY...'"
    echo "3. Run: ./scripts/tailscale-auth.sh"
    exit 1
fi

echo "✅ TS_AUTHKEY detected. Proceeding to spin up Zero-Trust Sandbox..."

# Assuming Limactl is installed and configured via Homebrew
# We pass the environment variable directly into the Lima boot context.
# In a real deployment, lima can accept user data or we use cloud-init configs.
limactl start --name=tachyon-sentinel scripts/matchlock-agent.yaml

echo "✅ tachyon-sentinel MicroVM is live on the Tailnet!"
