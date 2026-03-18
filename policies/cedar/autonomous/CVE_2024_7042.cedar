// Policy for CVE-2024-7042
// Description: A vulnerability in the GraphCypherQAChain class of langchain-ai/langchainjs versions 0.2.5 and all v...

forbid (
    principal,
    action == Action::"tachyon_safe_fetch",
    resource
)
when {
    false
};
        