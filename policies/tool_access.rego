package authz.tools

import future.keywords.in

default allow_fetch = false

# Phase 5.5: Dynamic Denylist (loaded via data.json)
# OPA will see this if we pass it in the data payload or keep it in the same directory.
import data.malicious_domains

allow_fetch {
    not is_denied
    is_allowed
}

is_denied {
    some d in data.malicious_domains
    endswith(input.domain, d)
}

# 1. If the client passed allowed_domains, it must match one of them.
is_allowed {
    input.allowed_domains
    count(input.allowed_domains) > 0
    some d in input.allowed_domains
    endswith(input.domain, d)
}

# 2. If the client did NOT pass allowed_domains, allow anything (relying on Triad filtering).
is_allowed {
    not has_allowed_domains
}

has_allowed_domains {
    input.allowed_domains
}
