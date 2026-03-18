// Policy for CVE-2024-8309
// Description: A vulnerability in the GraphCypherQAChain class of langchain-ai/langchain version 0.2.5 allows for S...

forbid (
    principal,
    action == Action::"tachyon_safe_fetch",
    resource
)
when {
    false
};
        