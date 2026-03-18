package tachyon.authz.manual.dlp

# Metadata: Outbound Data Loss Prevention
# Description: Prevents exfiltration of sensitive tokens and PII.

default allow = true

# Block sensitive tokens (Patterns)
deny_outbound [msg] {
    input.action == "outbound_dlp"
    # Matches common secret formats (Mocking the scanner result)
    input.parameters.has_sensitive_token == true
    msg := "Blocked by Reverse Firewall: Sensitive token detected in outbound payload."
}

# Block PII (Semantic/Pattern)
deny_outbound [msg] {
    input.action == "outbound_dlp"
    input.parameters.has_pii == true
    msg := "Blocked by Reverse Firewall: PII detected in outbound payload."
}
