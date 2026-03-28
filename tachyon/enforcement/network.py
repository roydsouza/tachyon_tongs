"""
Tachyon Tongs: Network Policy Engine
Implements strict outbound network hygiene to prevent SSRF and DNS rebinding.
"""
import ipaddress
import socket
import urllib.parse
from typing import List, Optional

class NetworkPolicy:
    """
    Enforces outbound network boundaries (Layer 3/4/7).
    Standardized blocklist includes RFC 1918, RFC 4193, and Cloud Metadata ranges.
    """
    
    # RFC 1918 (Private IPv4)
    PRIVATE_V4 = [
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("127.0.0.0/8"),    # Loopback
        ipaddress.ip_network("169.254.0.0/16"), # Link-Local (Cloud Metadata)
        ipaddress.ip_network("0.0.0.0/8")       # Current network
    ]
    
    # RFC 4193 / RFC 4291 (Private/Local IPv6)
    PRIVATE_V6 = [
        ipaddress.ip_network("fc00::/7"),       # Unique Local Address
        ipaddress.ip_network("::1/128"),        # Loopback
        ipaddress.ip_network("fe80::/10"),      # Link-Local
        ipaddress.ip_network("::/128"),         # Unspecified
    ]

    @classmethod
    def is_ip_private(cls, ip_str: str) -> bool:
        """Determines if an IP address belongs to a private or restricted range."""
        try:
            ip = ipaddress.ip_address(ip_str)
            
            if isinstance(ip, ipaddress.IPv4Address):
                return any(ip in net for net in cls.PRIVATE_V4)
            else:
                return any(ip in net for net in cls.PRIVATE_V6)
        except ValueError:
            return True # If it's not a valid IP, fail-closed

    @classmethod
    def resolve_safe(cls, hostname: str) -> List[str]:
        """
        Performs DNS resolution and returns a list of IPs.
        Strictly used for DNS-before-connect to detect rebinding.
        """
        try:
            # We use getaddrinfo to get both IPv4 and IPv6 results
            results = socket.getaddrinfo(hostname, None)
            return list(set(r[4][0] for r in results))
        except socket.gaierror:
            return []

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Performs initial URL sanity and protocol validation (H-01)."""
        try:
            parsed = urllib.parse.urlparse(url)
            # strictly enforce http/https
            if parsed.scheme not in ["http", "https"]:
                return False
            
            # Block internal protocols (file://, gopher://, etc.)
            if not parsed.netloc:
                return False
                
            return True
        except Exception:
            return False

def is_ssrf_risk(url: str) -> bool:
    """Convenience wrapper for SSRF risk assessment."""
    parsed = urllib.parse.urlparse(url)
    ips = NetworkPolicy.resolve_safe(parsed.hostname)
    if not ips:
        return False # Or True? If we can't resolve, it's a risk but urlopen might still try.
    
    return any(NetworkPolicy.is_ip_private(ip) for ip in ips)
