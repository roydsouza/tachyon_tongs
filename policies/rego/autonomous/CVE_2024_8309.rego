package tachyon.authz.autonomous.CVE_2024_8309

# Metadata: CVE-2024-8309
# Description: A vulnerability in the GraphCypherQAChain class of langchain-ai/langchain version 0.2.5 allows for S...

default allow = true

# Threat Mitigation Rule
deny_fetch [msg] {
    input.tool == "tachyon_safe_fetch"
    false
    msg := "Blocked by autonomous policy for CVE-2024-8309"
}
