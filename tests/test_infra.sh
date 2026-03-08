#!/bin/bash

# Tachyon Tongs: Infrastructure Regression Test

echo "Running Phase 0 Regression Tests..."
EXIT_CODE=0

fail() {
    echo "[FAIL] $1"
    EXIT_CODE=1
}

pass() {
    echo "[PASS] $1"
}

# 1. Directory Checks
DIRECTORIES=("src" "policies" "scripts" "docs" ".agent/rules" "tests")

echo "--- Checking Directories ---"
for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        fail "Directory missing: $dir"
    else
        pass "Directory exists: $dir"
    fi
done

# 2. File Checks
FILES=(".agent/rules/MISSION.md" "scripts/matchlock-agent.yaml" ".antigravity.yml")

echo "--- Checking Files ---"
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        fail "File missing: $file"
    else
        pass "File exists: $file"
    fi
done

# 3. YAML Syntax Validation
echo "--- Validating YAML Syntax ---"
if command -v yamllint >/dev/null 2>&1; then
    yamllint scripts/matchlock-agent.yaml || fail "matchlock-agent.yaml contains syntax errors."
    pass "matchlock-agent.yaml syntax is valid."
    
    yamllint .antigravity.yml || fail ".antigravity.yml contains syntax errors."
    pass ".antigravity.yml syntax is valid."
elif python3 -c "import yaml" >/dev/null 2>&1; then
    # Fallback to python yaml parsing if yamllint isn't installed but PyYAML is
    python3 -c "import yaml; yaml.safe_load(open('scripts/matchlock-agent.yaml'))" 2>/dev/null
    if [ $? -ne 0 ]; then
        fail "matchlock-agent.yaml contains syntax errors (Python fallback)."
    else
        pass "matchlock-agent.yaml syntax is valid."
    fi

    python3 -c "import yaml; yaml.safe_load(open('.antigravity.yml'))" 2>/dev/null
    if [ $? -ne 0 ]; then
        fail ".antigravity.yml contains syntax errors (Python fallback)."
    else
        pass ".antigravity.yml syntax is valid."
    fi
else
    echo "[WARN] yamllint and PyYAML not found. Skipping strict YAML validation."
    # Basic grep sanity checks
    grep -q "performance_profile:" .antigravity.yml || fail ".antigravity.yml missing primary key."
    grep -q "images:" scripts/matchlock-agent.yaml || fail "matchlock-agent.yaml missing primary key."
fi

# 4. Content Verification
echo "--- Verifying Core Content ---"
grep -q "hardware_neural_engine" .antigravity.yml || fail ".antigravity.yml is missing hardware acceleration spec."
grep -q "matchlock_inbox" scripts/matchlock-agent.yaml || fail "matchlock-agent.yaml is missing inbox mount."
grep -q "L1 Intent Gate" .agent/rules/MISSION.md || fail "MISSION.md is missing specific L1 rules."

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed. Infrastructure is solid."
else
    echo "❌ Some tests failed. Please review."
fi

exit $EXIT_CODE
