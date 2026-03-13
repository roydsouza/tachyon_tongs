#!/bin/bash
# Tachyon Tongs: MCP Registration Script
# This script automates the registration of the Tachyon Substrate as an MCP server.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
GATEWAY_SCRIPT="$PROJECT_DIR/src/mcp_gateway.py"
CONFIG_FILE="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/mcp_settings.json"

# Create backup of existing config
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "${CONFIG_FILE}.bak_$(date +%Y%m%d_%H%M%S)"
fi

# Use python to perform a safe JSON update
"$PYTHON_BIN" - <<EOF
import json
import os

config_path = "$CONFIG_FILE"
os.makedirs(os.path.dirname(config_path), exist_ok=True)

if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            config = {"mcpServers": {}}
else:
    config = {"mcpServers": {}}

if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["tachyon-substrate"] = {
    "command": "$PYTHON_BIN",
    "args": ["$GATEWAY_SCRIPT"],
    "env": {
        "PYTHONPATH": "$PROJECT_DIR"
    }
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"Successfully registered Tachyon Substrate in {config_path}")
EOF
