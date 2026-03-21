import sys

def verify_manual_parse():
    """Verify the encoding/decoding trick for the user's specific input string."""
    # This is the exact raw string the user provided
    user_input = "b'\\x02\\x00@6\\x16\\xdf\\x99=\\\x915W\\x9d\\x16\\xdc.\\xd8f\\xa2.(u\\xa0\\x18&\\xe7<\\x9c\\xeb\\xa00\\xf1p\\x82ax\\xa0\\xd5\\x9f_\\x82C\\xdb\\xc1\\xccHVkK\\xe0X\\xdc\\xa7\\x16\\x95\\x9dIa\\xd8/\\xe7jc\\xbf\\x8d\\x7f3'"
    
    print(f"[*] Testing manual parse of: {user_input[:40]}...")
    
    try:
        if (user_input.startswith("b'") and user_input.endswith("'")) or \
           (user_input.startswith('b"') and user_input.endswith('"')):
            content = user_input[2:-1]
        else:
            content = user_input
            
        # The 'unicode_escape' trick handles the \xHH sequences
        parsed = content.encode('utf-8').decode('unicode_escape').encode('latin-1')
        
        print(f"[✓] Success: Parsed to {len(parsed)} bytes.")
        print(f"[✓] First byte: {parsed[0]} (Expected: 2)")
        
        # Check target length (x_byte + len_bytes + 2*32B_chunks = 1 + 2 + 64 = 67 bytes)
        # Actually our PQC share for 64B seed with 32B chunks is: 1 (x) + 2 (len) + 64 (data) = 67 bytes.
        if len(parsed) == 67:
             print("[✓] Correct length for Phase 25.3 PQC share.")
        else:
             print(f"[!] Unexpected length: {len(parsed)}")

    except Exception as e:
        print(f"[!] Parse Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_manual_parse()
