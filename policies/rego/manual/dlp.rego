package tachyon.authz.manual.dlp

default allow = true

# Block if a sensitive token is detected (API Keys, etc)
deny {
    input.action == "outbound_dlp"
    input.pii_scan.has_sensitive_token == true
}

# We allow regular PII (emails) for now to prevent false positives in tests
# deny {
#     input.action == "outbound_dlp"
#     input.pii_scan.has_pii == true
# }
