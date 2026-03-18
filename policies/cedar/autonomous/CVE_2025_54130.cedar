// Policy for CVE-2025-54130
// Description: Cursor is a code editor built for programming with AI. Cursor allows writing in-workspace files with...

forbid (
    principal,
    action == Action::"tachyon_safe_fetch",
    resource
)
when {
    false
};
        