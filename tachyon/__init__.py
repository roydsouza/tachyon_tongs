"""
Tachyon Tongs: The High-Assurance Agentic Substrate
Modularized Package Root
"""

import sys
import importlib

# 1. Essential Exports (Direct Imports to avoid KeyError circularity)
from tachyon.core.state_manager import StateManager
from tachyon.core.signing import IntegrityManager
from tachyon.core.skill_parser import load_skill, materialize_network_constraints
from tachyon.core import wasm_benchmark, capability_token
from tachyon.monitoring.execution_logger import ExecutionLogger
from tachyon.monitoring.cot_monitor import PromptBehaviorMonitor
from tachyon.monitoring.syscall_monitor import syscall_monitor, SyscallBehaviorMonitor
from tachyon.monitoring.auditor_report import AuditorReport
from tachyon.agents.engineer import AutoPatcher, engineer_action_node
from tachyon.agents.scout import HorizonScout, scout_discovery_node
from tachyon.agents.legacy import analyst_agent
from tachyon.enforcement.apple_sandbox import AppleSandbox
from tachyon.enforcement.router import ToolRouter
from tachyon.enforcement.safe_fetch import SafeFetch, SecurityViolationError
from tachyon.pipeline.orchestrator import run_supervisor, create_supervisor_graph
from tachyon.pipeline.tri_stage_pipeline import UNTRUSTED_CONTENT_START, run_pipeline
from tachyon.pipeline.verifier import VerifierAgent, VerificationFailedError
from tachyon.protocol.mcp_gateway import MCPGateway, MCPHandler, handle_mcp_request
from tachyon.protocol.mcp_resources import MCPResourceManager

# 2. Module Attributes for legacy access
analyst_reasoning_node = analyst_agent.analyst_reasoning_node

# 3. Global Shims for legacy scripts (src.* and top-level tachyon.*)
if 'src' not in sys.modules:
    sys.modules['src'] = sys.modules['tachyon']

# Shimming submodules to satisfy legacy imports
# We use importlib to ensure the module is fully loaded before shimming
sys.modules['tachyon.execution_logger'] = sys.modules['tachyon.monitoring.execution_logger']
sys.modules['tachyon.cve_scraper'] = sys.modules['tachyon.agents.sentinel.scraper']
sys.modules['tachyon.verifier_agent'] = sys.modules['tachyon.pipeline.verifier']
sys.modules['tachyon.tri_stage_pipeline'] = sys.modules['tachyon.pipeline.tri_stage_pipeline']
sys.modules['tachyon.safe_fetch'] = sys.modules['tachyon.enforcement.safe_fetch']
sys.modules['tachyon.wasm_benchmark'] = sys.modules['tachyon.core.wasm_benchmark']
sys.modules['tachyon.capability_token'] = sys.modules['tachyon.core.capability_token']
sys.modules['tachyon.mcp_gateway'] = sys.modules['tachyon.protocol.mcp_gateway']
sys.modules['tachyon.mcp_resources'] = sys.modules['tachyon.protocol.mcp_resources']
sys.modules['tachyon.behavior_monitor'] = sys.modules['tachyon.monitoring']
sys.modules['tachyon.intel_pipeline'] = sys.modules['tachyon.pipeline.orchestrator']

# Shimming nested agent paths
sys.modules['tachyon.agents.analyst_agent'] = analyst_agent
sys.modules['tachyon.agents.scout_agent'] = sys.modules['tachyon.agents.scout']
sys.modules['tachyon.agents.engineer_agent'] = sys.modules['tachyon.agents.engineer']

# Nested src.* shims for legacy scripts
sys.modules['src.execution_logger'] = sys.modules['tachyon.execution_logger']
sys.modules['src.cve_scraper'] = sys.modules['tachyon.cve_scraper']
sys.modules['src.core'] = sys.modules['tachyon.core']
sys.modules['src.agents'] = sys.modules['tachyon.agents']
sys.modules['src.enforcement'] = sys.modules['tachyon.enforcement']
sys.modules['src.pipeline'] = sys.modules['tachyon.pipeline']
sys.modules['src.monitoring'] = sys.modules['tachyon.monitoring']
sys.modules['src.protocol'] = sys.modules['tachyon.protocol']

try:
    from tachyon.enforcement.daemon import app
except ImportError:
    app = None
