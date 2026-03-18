// Policy for CVE-2024-5184
// Description: The EmailGPT service contains a prompt injection vulnerability. The service uses an API service that...

forbid (
    principal,
    action == Action::"tachyon_safe_fetch",
    resource
)
when {
    resource.url like "*emailgpt.com*"
};
        