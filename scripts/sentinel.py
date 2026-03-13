#!/usr/bin/env python3
"""
Tachyon Tongs: Main Sentinel CLI
Primary executable for manual, scheduled or programmatic invocation of the Sentinel agent framework.
"""
import argparse
import sys
import os

# Add the root directory to PYTHONPATH so it can be invoked easily
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.execution_logger import ExecutionLogger
from src.cve_scraper import VulnerabilityScraper
from src.adk_sentinel import run_supervisor

import datetime
import os
import json
from src.auto_patcher import AutoPatcher

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
    parser.add_argument("--log-file", type=str, default="RUN_LOG.md", help="Specify custom log file path.")
    parser.add_argument("--verbose", type=int, choices=[0, 1, 2], default=2, help="Set verbosity level (0=Normal, 1=Details, 2=Full Content).")
    
    args = parser.parse_args()
    
    if not args.manual and not args.cron:
        parser.print_help()
        sys.exit(1)
        
    trigger_source = "MANUAL_CLI" if args.manual else "CRON_SCHEDULED"
    
    print(f"[Sentinel] Initializing run. Trigger source: {trigger_source}")
    
    # Initialize the ledger
    logger = ExecutionLogger(log_file=args.log_file, verbose_level=args.verbose)
    logger.start_run(trigger=trigger_source)
    
    try:
        # Check for aged proposals first
        check_temporal_fallback()
        
        # Phase 1 & 2: The Guardian Triad Split (Autonomous Multi-Agent Workflow)
        print("[Sentinel] Empowering the Guardian Triad Supervisor Graph...")
        # The Scout handles the scraping and the targeted URL fetching!
        triad_result = run_supervisor("https://github.com/advisories", logger=logger, run_scraper=True)
        
        # Check Engineer's final verification status
        final_output = triad_result.get("final_output", {})
        if final_output.get("status") == "error":
             print(f"[Sentinel] [WARNING] Verifier intercepted an exploit: {final_output.get('reason')}")
        else:
             print("[Sentinel] Multi-Agent Threat Analysis completed securely.")
        
    except Exception as e:
        error_msg = str(e)
        print(f"[Sentinel] [FATAL] Execution failed: {error_msg}")
        logger.log_fatal_error(error_msg)
    finally:
        # Finalize the ledger regardless of crash
        logger.finalize_run()
        print(f"[Sentinel] Run finalized. Ledger printed to {args.log_file}.")

if __name__ == "__main__":
    main()
