"""
Tachyon Tongs: High-Assurance AI Agent Substrate
"""

# Re-exporting core components to maintain backward compatibility with the test suite
# while preserving the new modular structure.

from tachyon.core.state_manager import StateManager
from tachyon.core.signing import IntegrityManager
from tachyon.core.skill_parser import load_skill, materialize_network_constraints
from tachyon.agents.engineer import AutoPatcher
from tachyon.enforcement.sandbox import AppleSandbox
from tachyon.pipeline.orchestrator import run_supervisor, create_supervisor_graph

# Exposing as modules for legacy tests that do 'from tachyon import auto_patcher'
# We use 'sys.modules' shimming to handle 'import tachyon.auto_patcher' style calls
import sys
import tachyon.agents.engineer as auto_patcher_mod
import tachyon.core.state_manager as state_manager_mod
import tachyon.core.skill_parser as skill_parser_mod
import tachyon.enforcement.sandbox as apple_sandbox_mod
import tachyon.pipeline.orchestrator as adk_sentinel_mod
import tachyon.core.signing as signing_mod
import tachyon.agents.scout as scout_mod
import tachyon.core.metal_accelerator as metal_mod
import tachyon.pipeline.tri_stage_pipeline as intel_pipeline_mod

sys.modules['tachyon.auto_patcher'] = auto_patcher_mod
sys.modules['tachyon.state_manager'] = state_manager_mod
sys.modules['tachyon.skill_parser'] = skill_parser_mod
sys.modules['tachyon.apple_sandbox'] = apple_sandbox_mod
sys.modules['tachyon.adk_sentinel'] = adk_sentinel_mod
sys.modules['tachyon.signing'] = signing_mod
sys.modules['tachyon.intel_pipeline'] = intel_pipeline_mod
sys.modules['tachyon.horizon_scout'] = scout_mod
sys.modules['tachyon.metal_accelerator'] = metal_mod
