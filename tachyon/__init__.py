"""
Tachyon Tongs: High-Assurance AI Agent Substrate
"""
import sys
import importlib.util

# Legacy Shims for Test Compatibility
SHIMS = {
    'tachyon.auto_patcher': 'tachyon.agents.engineer',
    'tachyon.state_manager': 'tachyon.core.state_manager',
    'tachyon.skill_parser': 'tachyon.core.skill_parser',
    'tachyon.apple_sandbox': 'tachyon.enforcement.sandbox',
    'tachyon.enforcement.apple_sandbox': 'tachyon.enforcement.sandbox',
    'tachyon.adk_sentinel': 'tachyon.pipeline.orchestrator',
    'tachyon.signing': 'tachyon.core.signing',
    'tachyon.intel_pipeline': 'tachyon.pipeline.tri_stage_pipeline',
    'tachyon.horizon_scout': 'tachyon.agents.scout',
    'tachyon.metal_accelerator': 'tachyon.core.metal_accelerator',
    'tachyon.intent_scoring': 'tachyon.agents.sentinel.scorer',
    'tachyon.agents.legacy.intent_scoring': 'tachyon.agents.sentinel.scorer',
    'tachyon.substrate_daemon': 'tachyon.enforcement.daemon'
}

def _apply_shims():
    for legacy, current in SHIMS.items():
        if legacy not in sys.modules:
            try:
                spec = importlib.util.find_spec(current)
                if spec:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[legacy] = module
                    spec.loader.exec_module(module)
            except (ImportError, AttributeError):
                pass

_apply_shims()

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
