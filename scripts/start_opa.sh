#!/usr/bin/env bash

# Tachyon Tongs: Local OPA Server Runner
# Downloads the Open Policy Agent binary if not present and starts the AuthZ server.

set -e

OPA_VERSION="v0.61.0"
OS=$(uname | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    ARCH="amd64"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    ARCH="arm64_static"
fi

if ! command -v opa &> /dev/null; then
    echo "[start_opa] 'opa' binary not found. Downloading v$OPA_VERSION for $OS-$ARCH..."
    curl -L -o opa https://openpolicyagent.org/downloads/${OPA_VERSION}/opa_${OS}_${ARCH}
    chmod 755 ./opa
    sudo mv opa /usr/local/bin/opa
    echo "[start_opa] OPA installed to /usr/local/bin/opa"
fi

# Locate the policies directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POLICIES_DIR="$ROOT_DIR/policies"

echo "[start_opa] Starting OPA server on port 9181 with policies from $POLICIES_DIR..."
# Run in foreground. To run in background, user can append &
opa run --server --addr :9181 "$POLICIES_DIR"
