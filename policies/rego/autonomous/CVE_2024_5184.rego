package tachyon.authz.autonomous.CVE_2024_5184

# Metadata: CVE-2024-5184
# Description: The EmailGPT service contains a prompt injection vulnerability. The service uses an API service that...

default allow = true

# Threat Mitigation Rule
deny_fetch [msg] {
    input.tool == "tachyon_safe_fetch"
    contains(input.url, "emailgpt.com")
    msg := "Blocked by autonomous policy for CVE-2024-5184"
}
