import secrets
from typing import List

# Simple Shamir's Secret Sharing over a prime field (P)
# P = 2**256 - 2**32 - 977 (secp256k1 prime)
# Since our secret (Root Seed) is exactly 32 bytes (256 bits), 
# we can treat the entire seed as a single large integer.
P = 2**256 - 2**32 - 977

def split_secret(secret_bytes: bytes, threshold: int, total_shares: int) -> List[bytes]:
    """Split a 32-byte secret into N shares using a prime field."""
    if len(secret_bytes) != 32:
        raise ValueError("Secret must be exactly 32 bytes.")
    
    secret_int = int.from_bytes(secret_bytes, 'big')
    if secret_int >= P:
        raise ValueError("Secret integer exceeds prime field size.")

    # Generate random coefficients for the polynomial: f(x) = s + a1*x + a2*x^2 + ...
    coeffs = [secret_int] + [secrets.randbelow(P) for _ in range(threshold - 1)]

    shares = []
    for i in range(1, total_shares + 1):
        x = i
        # Evaluate polynomial using Horner's method
        y = 0
        for coeff in reversed(coeffs):
            y = (y * x + coeff) % P
        
        # Share is (x, y) encoded as bytes: 1 byte for x, 32 bytes for y
        share = bytes([x]) + y.to_bytes(32, 'big')
        shares.append(share)
    
    return shares

def extended_gcd(a, b):
    """Extended Euclidean Algorithm for modular inverse."""
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = extended_gcd(b % a, a)
        return g, x - (b // a) * y, y

def mod_inverse(a, m):
    """Modular multiplicative inverse."""
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % m

def reconstruct_secret(shares: List[bytes]) -> bytes:
    """Reconstruct the secret from threshold shares using Lagrange Interpolation at x=0."""
    if not shares:
        raise ValueError("No shares provided.")
    
    # Deduplicate shares based on x value (index 0)
    unique_shares = {}
    for s in shares:
        if s[0] not in unique_shares:
            unique_shares[s[0]] = s
    
    shares = list(unique_shares.values())
    
    xs = [s[0] for s in shares]
    ys = [int.from_bytes(s[1:], 'big') for s in shares]
    
    secret_int = 0
    for i in range(len(shares)):
        # Calculate basis polynomial L_i(0)
        num = 1
        den = 1
        for j in range(len(shares)):
            if i == j:
                continue
            num = (num * (-xs[j])) % P
            den = (den * (xs[i] - xs[j])) % P
        
        li_0 = (num * mod_inverse(den, P)) % P
        secret_int = (secret_int + ys[i] * li_0) % P
        
    return secret_int.to_bytes(32, 'big')
