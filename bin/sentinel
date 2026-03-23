#!/usr/bin/env python3
"""
Tachyon Tongs: Sentinel Root Shim
Restores compatibility for root-level execution after modularization.
"""
import sys
import os

# Add the root directory to PYTHONPATH
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import and run the script from scripts/
from scripts.sentinel import main

if __name__ == "__main__":
    main()
