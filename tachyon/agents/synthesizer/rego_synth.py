import json
import os
import re

class RegoPolicySynthesizer:
    """
    Tachyon Tongs: Rego Policy Synthesizer
    Converts harvested exploit JSON into OPA/Rego (.rego) rules.
    """
    def __init__(self, output_dir="policies/rego/autonomous"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def synthesize(self, exploit_json_path):
        with open(exploit_json_path, 'r') as f:
            exploit = json.load(f)

        cve_id = exploit.get("cve_id", "UNKNOWN")
        description = exploit.get("description", "")
        
        # Sanitize filename
        safe_cve_id = re.sub(r'[^a-zA-Z0-9_]', '_', cve_id)
        output_path = os.path.join(self.output_dir, f"{safe_cve_id}.rego")

        # Logic to extract defensive signals (Simplified for Phase 12.1)
        # We look for keywords like "EmailGPT" or domain-like strings
        blocked_terms = []
        desc_lower = description.lower()
        if "emailgpt" in desc_lower:
            blocked_terms.append("emailgpt.com")

        rego_content = f"""package tachyon.authz.autonomous.{safe_cve_id}

# Metadata: {cve_id}
# Description: {description[:100]}...

default allow = true

# Threat Mitigation Rule
deny_fetch [msg] {{
    input.tool == "tachyon_safe_fetch"
    {" or ".join([f'contains(input.url, "{term}")' for term in blocked_terms]) if blocked_terms else "false"}
    msg := "Blocked by autonomous policy for {cve_id}"
}}
"""
        with open(output_path, 'w') as f:
            f.write(rego_content)

        return output_path
