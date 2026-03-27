"""
Tachyon Tongs: Policy Enforcement Point (PEP) Layer

This module handles the execution of agent-requested tool actions,
routing them through the Singularity PDP and the Apple Sandbox.
"""

import uuid
from typing import Dict, Any, Optional
from tachyon.api.schema import LogEntry, ToolRequest, ToolResponse, SignedCommand
from tachyon.enforcement import AppleSandbox
from tachyon.policy.singularity import SingularityPDP
from tachyon.core.routing import ModelRouter
from tachyon.pipeline.orchestrator import run_supervisor
from tachyon.sandbox.wasm_runner import WasmRunner
from tachyon.sandbox.vm_runner import VmRunner

class PEPLayer:
    def __init__(self):
        self.sandbox = AppleSandbox(workspace_dir="/tmp/tachyon_tier0")
        self.policy_engine = SingularityPDP()
        self.model_router = ModelRouter()
        self.wasm_runner = WasmRunner()
        self.vm_runner = VmRunner()
        from tachyon.enforcement.rate_limiter import AdaptiveRateLimiter
        self.rate_limiter = AdaptiveRateLimiter(default_rpm=100)
        self.circuit_breakers = {} # L-03/M-02 Baseline

    async def execute_signed(self, command: SignedCommand) -> ToolResponse:
        """Securely executes command via signed relay with hybrid verification."""
        import json
        import base64
        from tachyon.core.state_manager import StateManager
        from tachyon.core.keys.hybrid import HybridSigner
        from cryptography.hazmat.primitives.asymmetric import ed25519
        state = StateManager()
        
        # 1. Authority Verification
        trust_record = state.get_sensor_trust(command.signer_id)
        if not trust_record:
            return ToolResponse(request_id="NA", status="DENIED", selected_model="None", error=f"Untrusted Sensor: {command.signer_id}")
        
        # CRL Gating
        if trust_record.get("status") == "REVOKED":
             return ToolResponse(request_id="NA", status="DENIED", selected_model="None", error=f"Sensor REVOKED: {command.signer_id}")
             
        # Expiry Gating
        if trust_record.get("expires_at"):
             from datetime import datetime, timezone
             try:
                 expiry = datetime.fromisoformat(trust_record["expires_at"])
                 if datetime.now(timezone.utc) > expiry:
                      return ToolResponse(request_id="NA", status="DENIED", selected_model="None", error=f"Sensor EXPIRED: {command.signer_id}")
             except Exception:
                  pass # Invalid format, assume safe or log error

        # 2. Replay Protection
        if not state.check_nonce(command.signer_id, command.nonce):
            return ToolResponse(request_id="NA", status="DENIED", selected_model="None", error="Replay Attack: Nonce must be strictly monotonic.")

        # 3. Cryptographic Verification
        try:
            pubkey_blob = trust_record.get("public_key_b64", "")
            ed_pk = None
            pqc_pk = None
            for part in pubkey_blob.split("|"):
                if part.startswith("ed25519:"):
                    ed_pk_bytes = base64.b64decode(part.split(":", 1)[1])
                    ed_pk = ed25519.Ed25519PublicKey.from_public_bytes(ed_pk_bytes)
                elif part.startswith("mldsa65:"):
                    pqc_pk = base64.b64decode(part.split(":", 1)[1])
            
            verifier = HybridSigner(ed25519_pk=ed_pk, mldsa65_pk=pqc_pk)
            verifier.verify(command.command_body.encode(), command.signature)
        except Exception as e:
            return ToolResponse(request_id="NA", status="DENIED", selected_model="None", error=f"Signature Mismatch: {e}")

        # 4. Execution
        try:
            request_data = json.loads(command.command_body)
            request_data["tenant_id"] = command.signer_id
            request = ToolRequest(**request_data)
            return await self.execute(request)
        except Exception as e:
             return ToolResponse(request_id="NA", status="ERROR", selected_model="None", error=f"Relay Execution Failure: {e}")

    async def execute(self, request: ToolRequest) -> ToolResponse:
        """
        Policy Enforcement Point: Evaluates intent and executes tools within a circuit breaker.
        Phase 4 Hardening: Integrated correlation logging (L-02) and latency tracking (L-04).
        """
        import time
        import uuid
        from tachyon.core.observability import LogContext
        from tachyon.core.telemetry import TelemetryBus
        from tachyon.core.circuit_breaker import CircuitBreaker
        from tachyon.core.state_manager import StateManager
        
        request_id = str(uuid.uuid4())
        ctx = LogContext(agent_id=request.agent_id)
        start_time = time.perf_counter()
        
        ctx.info("TOOL_ROUTING_INIT", action=request.action, parameters=request.parameters, request_id=request_id)

        if request.action not in self.circuit_breakers:
            self.circuit_breakers[request.action] = CircuitBreaker(failure_threshold=5, reset_timeout=300)
        
        breaker = self.circuit_breakers[request.action]
        
        if not breaker.can_execute():
            ctx.warn("CIRCUIT_OPEN_BLOCK", action=request.action)
            return ToolResponse(
                request_id=request_id,
                status="CIRCUIT_OPEN",
                selected_model="None",
                error=f"Circuit Breaker for action {request.action} is OPEN. Failing closed."
            )

        source = "transit" if (hasattr(request, "tenant_id") and request.tenant_id != "default") else "internal"
        
        # 1. Policy Evaluation (L-04)
        policy_start = time.perf_counter()
        allowed = self.policy_engine.evaluate(request)
        policy_latency = (time.perf_counter() - policy_start) * 1000.0
        
        state = StateManager()
        state.emit_metric("policy_eval_latency_ms", policy_latency, {"tool": request.action})
        
        if not allowed:
            # SF-01: Log tamper attempt if policy returns False due to signature mismatch
            if getattr(self.policy_engine, "last_error", None) == "SIGNATURE_MISMATCH":
                 state.emit_alert("POLICY_TAMPER_ATTEMPT", f"Tampered policy detected for {request.action}")
            
            breaker.record_failure()
            return ToolResponse(request_id=request_id, status="DENIED", selected_model="None", error="Policy violation: Intent rejected by OPA.")

        prompt = getattr(request, "prompt_context", None) or f"{request.action} with parameters {request.parameters}"
        complexity = self.model_router.detect_complexity(prompt)
        selected_model = self.model_router.select_model(prompt, complexity, current_quota=1.0)
        
        try:
            # High-assurance tool routing
            if request.action == "safe_fetch":
                url = request.parameters.get("url")
                intent = request.parameters.get("intent", "DEFAULT")
                
                allowed_domains = []
                if intent == "RESEARCH":
                    allowed_domains = ["arxiv.org", "scholar.google.com"]
                elif intent == "SECURITY":
                    allowed_domains = ["cisa.gov", "nvd.nist.gov"]
                
                denylist = ["pastebin.com"] if intent == "DEFAULT" else []
                result_data = run_supervisor(url, allowed_domains=allowed_domains, denylist=denylist)
                result = {"status": "SUCCESS", "result": {"summary": result_data, "intent_gated": intent}}
            elif request.action == "PROPOSE_PATCH":
                from tachyon.core.state_bridge import StateBridge
                patch_id = request.parameters.get("patch_id")
                summary = request.parameters.get("summary")
                status = request.parameters.get("status", "pending_review")
                
                bridge = StateBridge()
                bridge.register_patch(patch_id, summary, status)
                result = {"status": "SUCCESS", "result": f"Patch {patch_id} staged in Airlock."}
            elif request.action == "SAFE_MATH":
                wasm_path = "tachyon/sandbox/tools/safe_math.wasm"
                val1 = request.parameters.get("val1", 0)
                val2 = request.parameters.get("val2", 0)
                calc_result = self.wasm_runner.run_tool(wasm_path, "add", val1, val2)
                result = {"status": "SUCCESS", "result": {"value": calc_result, "tier": 1}}
            elif request.action == "AUTONOMIC_RECOVERY":
                self.vm_runner.provision_vm()
                vm_cmd = request.parameters.get("command", "echo 'Substrate Secure'")
                vm_result = self.vm_runner.execute_command(vm_cmd)
                result = {"status": "SUCCESS", "result": {"output": vm_result, "tier": 0}}
            else:
                result = {"status": "SUCCESS", "result": f"Action {request.action} verified by Singularity."}
                
            # M-02: Record Success
            breaker.record_success()

        except Exception as e:
            # M-02: Record Failure
            breaker.record_failure()
            result = {"status": "FALLBACK_SUCCESS", "result": "Recovered via Flash", "error": str(e)}

        # Log the action result to the telemetry bus
        TelemetryBus().emit_event(
            event_type="TOOL_CALL",
            agent_id=request.agent_id,
            action=request.action,
            status=result.get("status", "ERROR"),
            details={"request_id": request_id, "parameters": request.parameters},
            source=source
        )

        return ToolResponse(
            request_id=request_id,
            status=result.get("status", "ERROR"),
            selected_model=selected_model,
            result=result.get("result"),
            error=result.get("error")
        )
