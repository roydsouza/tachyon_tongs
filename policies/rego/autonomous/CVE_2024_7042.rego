package tachyon.authz.autonomous.CVE_2024_7042

# Metadata: CVE-2024-7042
# Description: A vulnerability in the GraphCypherQAChain class of langchain-ai/langchainjs versions 0.2.5 and all v...

default allow = true

# Threat Mitigation Rule
deny_fetch [msg] {
    input.tool == "tachyon_safe_fetch"
    false
    msg := "Blocked by autonomous policy for CVE-2024-7042"
}
