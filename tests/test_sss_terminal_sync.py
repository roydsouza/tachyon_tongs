import sys

def verify_terminal_escapes():
    """Verify parsing against the exact literal string provided in the user's terminal log."""
    # Note the double backslashes which represent how Python sees a literal \x in a string
    user_input = "b'\\x02\\x00@6\\x16\\xdf\\x99=\\\x915W\\x9d\\x16\\xdc.\\xd8f\\xa2.(u\\xa0\\x18&\\xe7<\\x9c\\xeb\\xa00\\xf1p\\x82ax\\xa0\\xd5\\x9f_\\x82C\\xdb\\xc1\\xccHVkK\\xe0X\\xdc\\xa7\\x16\\x95\\x9dIa\\xd8/\\xe7jc\\xbf\\x8d\\x7f3'"
    
    print(f"[*] Testing Terminal Escapes for: {user_input[:40]}...")
    
    try:
        clean_str = user_input
        if clean_str.startswith("b'") and clean_str.endswith("'"):
            clean_str = clean_str[2:-1]
            
        # The key is that 'utf-8'.decode('unicode_escape') handles the literal \x sequences correctly
        parsed = clean_str.encode('utf-8').decode('unicode_escape').encode('latin-1')
        
        print(f"[✓] Success: Parsed to {len(parsed)} bytes.")
        print(f"[✓] First byte: {parsed[0]} (Expected: 2)")
        
        if len(parsed) >= 64:
             print("[✓] Correct length for Phase 25.3 PQC share.")
        else:
             print(f"[!] Unexpected length: {len(parsed)}")

    except Exception as e:
        print(f"[!] Parse Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_terminal_escapes()
