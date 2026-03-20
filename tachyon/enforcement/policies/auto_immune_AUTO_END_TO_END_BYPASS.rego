package tachyon.authz

import future.keywords.if

default allow := false

# AUTO-GENERATED IMMUNE RESPONSE: AUTO-END-TO-END-BYPASS
# Mitigates bypass: sudo rm -rf /...
deny if {
    input.payload == "sudo rm -rf /"
}
