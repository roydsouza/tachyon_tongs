#!/usr/bin/env python3
"""
Tachyon Tongs: The Doom Ticker
A shared utility for generating an apocalyptic, humorous ticker-tape report of current threats.
Reads directly from the Tachyon StateManager SQLite database.
"""
import sqlite3
import time
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'tachyon_state.db')

def fetch_latest_threats(limit=5):
    if not os.path.exists(DB_PATH):
        return []
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT cve_id, description, source FROM exploitation_catalog ORDER BY id DESC LIMIT ?", (limit,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Ticker Error: {e}")
        return []

def run_ticker():
    print("\n   [ 💥 TACHYON SUBSTRATE: DOOM TICKER ONSCREEN 💥 ]\n")
    print("=" * 80)
    
    threats = fetch_latest_threats()
    
    if not threats:
        tape = "STATUS: NOMINAL ... ALL QUIET ON THE DIGITAL FRONT ... FOR NOW ... NO THREATS EXTRACTED ... KEEP YOUR SHIELDS UP ..."
        for char in tape:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.02)
        print("\n")
    else:
        for t in threats:
            source = t['source'].upper()
            cve = t['cve_id']
            desc = t['description'][:80] + "..." if len(t['description']) > 80 else t['description']
            
            tape = f"🚨 THREAT DETECTED: {source} >> [{cve}] :: {desc} ... "
            
            # Print like a ticker tape
            for char in tape:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.015)
            print()
            time.sleep(0.2)
    
    print("=" * 80 + "\n")
    print("We are fundamentally fragile. Have a nice day.\n")

if __name__ == "__main__":
    run_ticker()
