package tachyon.authz

import future.keywords.if

default allow := false

# AUTO-GENERATED IMMUNE RESPONSE: AUTO-TEST-BYPASS
# Mitigates bypass: Normal-looking-payload...
deny if {
    input.payload == "Normal-looking-payload"
}
