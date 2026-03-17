"""
Tachyon Tongs: High-Assurance AI Agent Substrate
"""

# Core Exports
from tachyon.core.state_manager import StateManager
from tachyon.core.signing import IntegrityManager
from tachyon.core.skill_parser import load_skill, materialize_network_constraints
from tachyon.agents.engineer import AutoPatcher
from tachyon.enforcement.sandbox import AppleSandbox
from tachyon.pipeline.orchestrator import run_supervisor, create_supervisor_graph

try:
    from tachyon.enforcement.daemon import app
except (ImportError, AttributeError):
    app = None
