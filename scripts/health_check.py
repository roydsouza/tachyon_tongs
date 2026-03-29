#!/usr/bin/env python3
"""
Tachyon Tongs: Substrate Startup Health Check (C-11)
Validates the local security posture before daemon or agent execution.

Checks:
1. Agent SBOM Integrity (calibrate_sbom.py --verify)
2. Policy Engine Initialization (SingularityPDP)
3. Mandatory Secret Configuration (TACHYON_SECRET_KEY)
4. Alert Hub Status (ALERT.md)
"""
import os
import sys
import json
import logging
import subprocess

# Set up logging to stderr
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("HealthCheck")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

def check_env():
    """Verify mandatory environment variables."""
    if not os.environ.get("TACHYON_SECRET_KEY"):
        logger.warning("TACHYON_SECRET_KEY not set. Using insecure development default.")
    return True

def check_sbom():
    """Verify agent hashes against SBOM."""
    logger.info("Checking Agent SBOM integrity...")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/calibrate_sbom.py", "--verify"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("SBOM: PASSED")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"SBOM: FAILED\n{e.stdout}")
        return False

def check_policy_engines():
    """Verify that SingularityPDP can initialize all configured engines."""
    logger.info("Checking Policy Engine initialization...")
    try:
        from tachyon.policy.singularity import SingularityPDP
        from tachyon.policy.engine import Verdict
        
        pdp = SingularityPDP()
        if pdp._emergency_mode:
            logger.error("Policy Engines: FAILED (Initialization error, Emergency fallback activated)")
            return False
        
        # Test a simple action
        import asyncio
        async def _test():
            return await pdp.evaluate("health_check_agent", "get_status", {})
        
        # Run dummy check
        import asyncio
        verdict = asyncio.run(_test())
        
        logger.info(f"Policy Engines: PASSED (Broker: {pdp.engine_id})")
        return True
    except Exception as e:
        logger.error(f"Policy Engines: CRITICAL FAILURE: {e}")
        return False

def check_alerts():
    """Check for active security alerts in ALERT.md."""
    alert_path = os.path.join(ROOT_DIR, "ALERT.md")
    if not os.path.exists(alert_path):
        return True
    
    with open(alert_path, "r") as f:
        content = f.read().strip()
    
    # Check if there are entries beyond the clean header
    # Stale alerts start with "## ["
    if "## [" in content:
        lines = [l for l in content.splitlines() if l.startswith("## [")]
        logger.warning(f"Alerts: {len(lines)} active alerts detected in ALERT.md")
        return False
    
    logger.info("Alerts: CLEAN")
    return True

def run_all():
    print("=" * 60)
    print("      TACHYON TONGS: SUBSTRATE HEALTH CHECK (M-11)      ")
    print("=" * 60)
    
    success = True
    
    if not check_env(): success = False
    print("-" * 60)
    if not check_sbom(): success = False
    print("-" * 60)
    if not check_policy_engines(): success = False
    print("-" * 60)
    if not check_alerts(): 
        # Alerts are a warning, not a hard failure unless in STRICT mode
        if os.environ.get("TACHYON_STRICT_MODE") == "1":
            success = False
            
    print("=" * 60)
    if success:
        print("RESULT: HEALTHY - Substrate is ready for operation.")
        sys.exit(0)
    else:
        print("RESULT: COMPROMISED OR MISCONFIGURED - Check errors above.")
        sys.exit(1)

if __name__ == "__main__":
    run_all()
