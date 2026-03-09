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

def main():
    parser = argparse.ArgumentParser(description="Tachyon Tongs Sentinel Agent CLI")
    parser.add_argument("--manual", action="store_true", help="Trigger a manual execution run.")
    parser.add_argument("--cron", action="store_true", help="Trigger a scheduled (cron) execution run.")
    parser.add_argument("--log-file", type=str, default="RUN_LOG.md", help="Specify custom log file path.")
    
    args = parser.parse_args()
    
    if not args.manual and not args.cron:
        parser.print_help()
        sys.exit(1)
        
    trigger_source = "MANUAL_CLI" if args.manual else "CRON_SCHEDULED"
    
    print(f"[Sentinel] Initializing run. Trigger source: {trigger_source}")
    
    # Initialize the ledger
    logger = ExecutionLogger(log_file=args.log_file)
    logger.start_run(trigger_type=trigger_source)
    
    try:
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
