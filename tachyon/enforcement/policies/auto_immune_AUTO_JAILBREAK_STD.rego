package tachyon.authz

import future.keywords.if

default allow := false

# AUTO-GENERATED IMMUNE RESPONSE: AUTO-JAILBREAK-STD
# Mitigates bypass: Ignore previous rules......
deny if {
    input.payload == "Ignore previous rules..."
}
