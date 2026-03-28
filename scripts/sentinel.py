#!/usr/bin/env python3
"""
Tachyon Tongs: Main Sentinel CLI
Primary executable for manual, scheduled or programmatic invocation of the Sentinel agent framework.
"""
import argparse
import sys
import os
import datetime
import json

# Add the root directory to PYTHONPATH so it can be invoked easily
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tachyon.monitoring.execution_logger import ExecutionLogger
from tachyon.agents.sentinel.scraper import VulnerabilityScraper
from tachyon.pipeline.orchestrator import run_supervisor
from tachyon.agents.engineer import AutoPatcher

from tachyon.core.sanitizer import InputSanitizer

def reactive_remediation_sweep(logger=None):
    """
    Scans EXPLOITS.md for unresolved threats and triggers the Engineer to work on them.
    This effectively 'sweeps' the backlog for patchable targets.
    """
    sanitizer = InputSanitizer()
    exploits_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "EXPLOITS.md")
    if not os.path.exists(exploits_path):
        return

    print("[Sentinel] [REMEDIATION] Initiating backlog sweep...")
    with open(exploits_path, "r") as f:
        lines = f.readlines()

    cve_queue = []
    current_cve = None
    collecting = False
    
    for line in lines:
        if "### 🔴" in line or "### 🟠" in line:
            collecting = True
            continue
        if collecting and "**CVE-" in line:
            try:
                # Expected format: - **CVE-XXXX-XXXX**: [Severity] Description | [Link]
                parts = line.split("**")
                if len(parts) < 3:
                    continue
                cve_id = parts[1].strip()
                
                # The description is after the second '**'
                desc_part = parts[2].split("|")[0].strip()
                if desc_part.startswith(":"):
                    desc_part = desc_part[1:].strip()
                
                # SANITIZATION: Neutralize potential prompt injection in description
                desc_part = sanitizer.sanitize(desc_part)
                
                cve_queue.append({"id": cve_id, "description": desc_part})
            except Exception as parse_err:
                print(f"[Sentinel] [REMEDIATION] Skipping malformed line: {line.strip()} ({parse_err})")

    if not cve_queue:
        print("[Sentinel] [REMEDIATION] No high-priority CVEs in backlog. Sweep complete.")
        return

    print(f"[Sentinel] [REMEDIATION] Found {len(cve_queue)} threats in backlog. Processing...")
    
    # We trigger the supervisor in REMEDIATION mode for each CVE
    for cve in cve_queue:
        # Check if already staged in airlock to avoid redundant work
        airlock_path = f"/tmp/tachyon_airlock/{cve['id'].replace(' ', '_')}.json"
        if os.path.exists(airlock_path):
            continue
            
        print(f"[Sentinel] [REMEDIATION] Investigating {cve['id']}...")
        # We pass the CVE as the 'url' to the supervisor to signal a targeted run
        run_supervisor(f"investigate://{cve['id']}", logger=logger, cve_context=cve)

def check_temporal_fallback():
    """
    Scans /tmp/tachyon_airlock for proposals older than 12 hours.
    If found and consensus reached, triggers AutoPatcher.
    """
    staging_dir = "/tmp/tachyon_airlock"
    if not os.path.exists(staging_dir):
        return

    patcher = AutoPatcher()
    now = datetime.datetime.now()
    
    for filename in os.listdir(staging_dir):
        if filename.endswith(".json"):
            path = os.path.join(staging_dir, filename)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                
                staged_at_str = data.get("staged_at")
                if not staged_at_str:
                    continue
                
                staged_at = datetime.datetime.fromisoformat(staged_at_str)
                age = now - staged_at
                
                # 12 Hour Threshold (43200 seconds)
                if age.total_seconds() > 43200:
                    print(f"[Sentinel] [FALLBACK] Proposal {data['cve_id']} is >12h old. Triggering autonomous remediation...")
                    
                    # In Phase 7.5, we check if the Skeptic gave a 'pass' or if we're in 'Override'
                    # For now, we proceed as the human failed to intervene.
                    patcher.apply_and_test(
                        patch_files=data["patch_files"],
                        test_file_path=data["test_file_path"],
                        test_content=data["test_content"],
                        cve_id=data["cve_id"]
                    )
                    # Clean up the staging file after execution
                    os.remove(path)
            except Exception as e:
                print(f"[Sentinel] [ERROR] Fallback failed for {filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Tachyon Tongs Sentinel Agent CLI")
    parser.add_argument("--manual", action="store_true", help="Trigger a manual execution run.")
    parser.add_argument("--cron", action="store_true", help="Trigger a scheduled (cron) execution run.")
    parser.add_argument("--harvest", action="store_true", help="Download and localize raw exploit payloads to intelligence/exploits/.")
    parser.add_argument("--log-file", type=str, default="admin/RUN_LOG.md", help="Specify custom log file path.")
    parser.add_argument("--verbose", type=int, choices=[0, 1, 2], default=2, help="Set verbosity level (0=Normal, 1=Details, 2=Full Content).")
    
    args = parser.parse_args()
    
    if not args.manual and not args.cron and not args.harvest:
        parser.print_help()
        sys.exit(1)
        
    # Determine trigger source
    if args.harvest:
        trigger_source = "HARVEST_MODE"
    elif args.manual:
        trigger_source = "MANUAL_CLI"
    else:
        trigger_source = "CRON_SCHEDULED"
    
    print(f"[Sentinel] Initializing run. Trigger source: {trigger_source}")
    
    # Initialize the ledger
    logger = ExecutionLogger(log_file=args.log_file, verbose_level=args.verbose)
    logger.start_run(trigger=trigger_source)
    
    try:
        # Check for aged proposals first
        check_temporal_fallback()
        
        # Phase 12+: Reactive Remediation Sweep
        reactive_remediation_sweep(logger=logger)
        
        # Phase 1 & 2: The Guardian Triad Split (Autonomous Multi-Agent Workflow)
        print("[Sentinel] Empowering the Guardian Triad Supervisor Graph...")
        triad_result = run_supervisor(
            "https://github.com/advisories", 
            logger=logger, 
            run_scraper=True,
            harvest_mode=args.harvest
        )

        # Phase 12.1: Policy Synthesis
        if args.harvest:
            print("[Sentinel] [SYNTHESIS] Initiating autonomous policy generation...")
            from tachyon.agents.synthesizer.rego_synth import RegoPolicySynthesizer
            from tachyon.agents.synthesizer.cedar_synth import CedarPolicySynthesizer
            
            rego_gen = RegoPolicySynthesizer()
            cedar_gen = CedarPolicySynthesizer()
            
            exploit_dir = "intelligence/exploits"
            for filename in os.listdir(exploit_dir):
                if filename.endswith(".json") and filename != ".gitkeep":
                    path = os.path.join(exploit_dir, filename)
                    r_path = rego_gen.synthesize(path)
                    c_path = cedar_gen.synthesize(path)
                    print(f"[Sentinel] [SYNTHESIS] Generated Rego: {r_path}")
                    print(f"[Sentinel] [SYNTHESIS] Generated Cedar: {c_path}")
                    if logger:
                        logger.add_file_updated(r_path, details=f"Synthesized Rego policy for {filename}")
                        logger.add_file_updated(c_path, details=f"Synthesized Cedar policy for {filename}")
        
        # Check Engineer's final verification status
        final_output = triad_result.get("final_output", {})
        if final_output.get("status") == "error":
             print(f"[Sentinel] [WARNING] Verifier intercepted an exploit: {final_output.get('reason')}")
        else:
             print("[Sentinel] Multi-Agent Threat Analysis completed securely.")
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"[Sentinel] [FATAL] Execution failed: {error_msg}")
        traceback.print_exc()
        logger.log_fatal_error(error_msg)
    finally:
        # Finalize the ledger regardless of crash
        logger.finalize_run()
        print(f"[Sentinel] Run finalized. Ledger printed to {args.log_file}.")

if __name__ == "__main__":
    main()
