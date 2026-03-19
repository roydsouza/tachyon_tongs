package tachyon.authz
default allow = false
# AUTO-FIX for bypass: malicious-bypass-str...
deny { input.payload == "malicious-bypass-string" }
