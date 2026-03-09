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
from src.adk_sentinel import run_sentinel

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
        # 1. Autonomous Scraping Phase
        print("[Sentinel] Phase 1: Initiating Threat Intelligence Scraper...")
        scraper = VulnerabilityScraper(mode="mock")
        new_threats = scraper.scrape_new_threats(logger=logger)
        print(f"[Sentinel] Identified {len(new_threats)} new critical threat(s).")
        
        # 2. ADK Deep Analysis Phase
        print("[Sentinel] Phase 2: Analyzing Target Endpoints via ADK StateGraph...")
        adk_result = run_sentinel("https://github.com/advisories", logger=logger)
        
        if adk_result.get("final_output", {}).get("status") == "error":
             print(f"[Sentinel] [WARNING] Verifier intercepted an exploit: {adk_result['final_output'].get('reason')}")
        else:
             print("[Sentinel] Endpoint analysis completed securely.")
        
    except Exception as e:
        print(f"[Sentinel] [FATAL] Execution failed: {str(e)}")
    finally:
        # Finalize the ledger regardless of crash
        logger.finalize_run()
        print(f"[Sentinel] Run finalized. Ledger printed to {args.log_file}.")

if __name__ == "__main__":
    main()
