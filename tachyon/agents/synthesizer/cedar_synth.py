import json
import os
import re

class CedarPolicySynthesizer:
    """
    Tachyon Tongs: Cedar Policy Synthesizer
    Converts harvested exploit JSON into AWS Cedar (.cedar) policies.
    """
    def __init__(self, output_dir="policies/cedar/autonomous"):
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
        output_path = os.path.join(self.output_dir, f"{safe_cve_id}.cedar")

        # Simplified Cedar policy generation
        blocked_terms = []
        desc_lower = description.lower()
        if "emailgpt" in desc_lower:
            blocked_terms.append("*emailgpt.com*")

        cedar_content = f"""// Policy for {cve_id}
// Description: {description[:100]}...

forbid (
    principal,
    action == Action::"tachyon_safe_fetch",
    resource
)
when {{
    {f'resource.url like "{blocked_terms[0]}"' if blocked_terms else "false"}
}};
        """
        with open(output_path, 'w') as f:
            f.write(cedar_content)

        return output_path
