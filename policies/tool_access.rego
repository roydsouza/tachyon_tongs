package authz.tools

import future.keywords.in

# Default deny
default allow_fetch = false

# Allowed threat intelligence domains for Sentinel
allowed_domains := [
    "cisa.gov",
    "github.com",
    "nvd.nist.gov",
    "arxiv.org",
    "huntr.ml",
    "lmsys.org"
]

# Allow if the requested URL domain ends with one of the allowed_domains
allow_fetch {
    some domain in allowed_domains
    endswith(input.url, domain)
}

# Explicit deny for known malicious staging grounds (simulated)
deny_fetch {
    endswith(input.url, "pastebin.com")
}
