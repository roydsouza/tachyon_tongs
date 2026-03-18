package tachyon.authz.autonomous.CVE_2023_29374

# Metadata: CVE-2023-29374
# Description: In LangChain through 0.0.131, the LLMMathChain chain allows prompt injection attacks that can execut...

default allow = true

# Threat Mitigation Rule
deny_fetch [msg] {
    input.tool == "tachyon_safe_fetch"
    false
    msg := "Blocked by autonomous policy for CVE-2023-29374"
}
