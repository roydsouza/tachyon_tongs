// Policy for CVE-2023-29374
// Description: In LangChain through 0.0.131, the LLMMathChain chain allows prompt injection attacks that can execut...

forbid (
    principal,
    action == Action::"tachyon_safe_fetch",
    resource
)
when {
    false
};
        