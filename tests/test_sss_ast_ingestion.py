import ast
import sys

def verify_ast_ingestion():
    """Verify that ast.literal_eval correctly parses the exact string provided by the user."""
    user_input = "b'\\x02\\x00@6\\x16\\xdf\\x99=\\\x915W\\x9d\\x16\\xdc.\\xd8f\\xa2.(u\\xa0\\x18&\\xe7<\\x9c\\xeb\\xa00\\xf1p\\x82ax\\xa0\\xd5\\x9f_\\x82C\\xdb\\xc1\\xccHVkK\\xe0X\\xdc\\xa7\\x16\\x95\\x9dIa\\xd8/\\xe7jc\\xbf\\x8d\\x7f3'"
    
    print(f"[*] Testing ingestion of: {user_input[:40]}...")
    
    try:
        parsed = ast.literal_eval(user_input)
        if isinstance(parsed, bytes):
            print(f"[✓] Success: Parsed to {len(parsed)} bytes.")
            print(f"[✓] First byte: {parsed[0]} (Expected: 2)")
        else:
            print(f"[!] Failure: Parsed to {type(parsed)}, not bytes.")
            sys.exit(1)
    except Exception as e:
        print(f"[!] AST Parse Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_ast_ingestion()
