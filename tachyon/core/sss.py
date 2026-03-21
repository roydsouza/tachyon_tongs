import secrets
from typing import List

# Simple Shamir's Secret Sharing over a prime field (P)
# P = 2**256 - 2**32 - 977 (secp256k1 prime)
# Since our secret (Root Seed) is exactly 32 bytes (256 bits), 
# we can treat the entire seed as a single large integer.
P = 2**256 - 2**32 - 977

def split_secret(secret_bytes: bytes, threshold: int, total_shares: int) -> List[bytes]:
    """
    Split a secret of any length into N shares.
    Splits the secret into 32-byte chunks and performs Shamir on each.
    """
    secret_len = len(secret_bytes)
    # Number of 32-byte chunks
    num_chunks = (secret_len + 31) // 32
    
    # Pad secret to multiple of 32
    padded_secret = secret_bytes.ljust(num_chunks * 32, b'\x00')
    
    all_shares = [[] for _ in range(total_shares)]
    
    for i in range(num_chunks):
        chunk = padded_secret[i*32 : (i+1)*32]
        chunk_int = int.from_bytes(chunk, 'big')
        
        # Polynomial: f(x) = chunk + a1*x + ...
        coeffs = [chunk_int] + [secrets.randbelow(P) for _ in range(threshold - 1)]
        
        for x in range(1, total_shares + 1):
            y = 0
            for coeff in reversed(coeffs):
                y = (y * x + coeff) % P
            
            # Store y for this chunk
            all_shares[x-1].append(y.to_bytes(32, 'big'))
            
    # Final share: [x_byte] + [len_byte] + [chunk1] + [chunk2]...
    final_shares = []
    for x in range(1, total_shares + 1):
        # We include the original length in the first share for reconstruction
        share_data = bytes([x]) + secret_len.to_bytes(2, 'big') + b"".join(all_shares[x-1])
        final_shares.append(share_data)
        
    return final_shares

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
    """Reconstruct a secret of arbitrary length from threshold shares."""
    if not shares:
        raise ValueError("No shares provided.")
        
    # All shares must have same x
    xs = [s[0] for s in shares]
    # Original length is at index 1-2
    secret_len = int.from_bytes(shares[0][1:3], 'big')
    num_chunks = (secret_len + 31) // 32
    
    reconstructed_chunks = []
    
    for c in range(num_chunks):
        # Extract y values for this chunk from all shares
        ys = []
        for s in shares:
            # Chunk 'c' starts at index 3 + c*32
            chunk_data = s[3 + c*32 : 3 + (c+1)*32]
            ys.append(int.from_bytes(chunk_data, 'big'))
            
        # Lagrange Interpolation at x=0
        chunk_int = 0
        for i in range(len(xs)):
            num = 1
            den = 1
            for j in range(len(xs)):
                if i == j: continue
                num = (num * (-xs[j])) % P
                den = (den * (xs[i] - xs[j])) % P
            
            li_0 = (num * mod_inverse(den, P)) % P
            chunk_int = (chunk_int + ys[i] * li_0) % P
            
        reconstructed_chunks.append(chunk_int.to_bytes(32, 'big'))
        
    full_secret = b"".join(reconstructed_chunks)
    return full_secret[:secret_len]
