import yaml
import re
from typing import Dict, Any, Tuple
import os

class SkillParserError(Exception):
    pass

def load_skill(filepath: str) -> Tuple[Dict[str, Any], str]:
    """
    Parses a specialized declarative SKILL.md file.
    Returns:
        metadata (Dict): The parsed YAML frontmatter.
        system_prompt (str): The Markdown body acting as the LLM's core directive.
    """
    if not os.path.exists(filepath):
        raise SkillParserError(f"Skill definition not found at: {filepath}")

    with open(filepath, 'r') as f:
        content = f.read()

    # Regex to cleanly split the YAML frontmatter from the Markdown body
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, flags=re.DOTALL)
    
    if not match:
        raise SkillParserError(f"Malformed SKILL.md. Requires strict YAML frontmatter delimited by '---'. File: {filepath}")

    yaml_block = match.group(1)
    markdown_body = match.group(2).strip()

    try:
        metadata = yaml.safe_load(yaml_block)
    except yaml.YAMLError as e:
        raise SkillParserError(f"Invalid YAML frontmatter in SKILL.md: {str(e)}")

    # Set up some functional defaults to prevent downstream null crashes
    if not isinstance(metadata.get("capabilities"), list):
        metadata["capabilities"] = []
    
    network_policy = metadata.get("network_policy", {})
    if not isinstance(network_policy, dict):
        metadata["network_policy"] = {"mode": "filtering_only"}

    return metadata, markdown_body

def materialize_network_constraints(skill_metadata: Dict[str, Any]) -> list:
    """
    Translates a Skill's configuration into a strict Substrate payload.
    Returns None if the agent relies purely on the Triad semantic filter.
    Returns a List of domains for the strict_allowlist mode.
    """
    policy = skill_metadata.get("network_policy", {})
    mode = policy.get("mode", "filtering_only")
    
    if mode == "strict_allowlist":
        return policy.get("allowed_domains", [])
    
    # filtering_only mode means we defer to the Sentinel's global denylist + Tri-Stage filter
    return None
