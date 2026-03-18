package tachyon.authz.autonomous.CVE_2025_54135

# Metadata: CVE-2025-54135
# Description: Cursor is a code editor built for programming with AI. Cursor allows writing in-workspace files with...

default allow = true

# Threat Mitigation Rule
deny_fetch [msg] {
    input.tool == "tachyon_safe_fetch"
    false
    msg := "Blocked by autonomous policy for CVE-2025-54135"
}
