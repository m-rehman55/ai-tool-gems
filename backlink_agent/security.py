"""Security and SSRF Protection Module for Backlink Agent.

Treats all input URLs (from CSV, redirected locations, external pages) as untrusted.
Enforces strict HTTPS, scheme boundaries, hostname validation, IP blacklist (IPv4/IPv6),
and redirect target inspection.
"""

from __future__ import annotations

import ipaddress
import re
import socket
import urllib.parse
from typing import List, Optional, Set, Tuple

# RFC-defined blocked networks
BLOCKED_IPV4_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),         # "This" network
    ipaddress.ip_network("10.0.0.0/8"),        # Private-use (RFC 1918)
    ipaddress.ip_network("100.64.0.0/10"),     # Shared Address Space / CGNAT (RFC 6598)
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback (RFC 1122)
    ipaddress.ip_network("169.254.0.0/16"),    # Link-Local / Cloud Metadata (RFC 3927)
    ipaddress.ip_network("172.16.0.0/12"),     # Private-use (RFC 1918)
    ipaddress.ip_network("192.0.0.0/24"),      # IETF Protocol Assignments (RFC 6890)
    ipaddress.ip_network("192.0.2.0/24"),      # TEST-NET-1 (RFC 5737)
    ipaddress.ip_network("192.88.99.0/24"),    # 6to4 Relay Anycast (RFC 7526)
    ipaddress.ip_network("192.168.0.0/16"),    # Private-use (RFC 1918)
    ipaddress.ip_network("198.18.0.0/15"),     # Network Interconnect Benchmarking (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),   # TEST-NET-2 (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),    # TEST-NET-3 (RFC 5737)
    ipaddress.ip_network("224.0.0.0/4"),       # Multicast (RFC 5771)
    ipaddress.ip_network("240.0.0.0/4"),       # Reserved for Future Use (RFC 1112)
    ipaddress.ip_network("255.255.255.255/32"),# Broadcast
]

BLOCKED_IPV6_NETWORKS = [
    ipaddress.ip_network("::/128"),            # Unspecified
    ipaddress.ip_network("::1/128"),          # Loopback
    ipaddress.ip_network("100::/64"),          # Discard prefix (RFC 6666)
    ipaddress.ip_network("2001:db8::/32"),     # Documentation (RFC 3849)
    ipaddress.ip_network("fc00::/7"),          # Unique Local Addresses (ULA, RFC 4193)
    ipaddress.ip_network("fe80::/10"),         # Link-Local Unicast (RFC 4291)
    ipaddress.ip_network("ff00::/8"),          # Multicast (RFC 4291)
]

FORBIDDEN_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
    "metadata.google.internal",
    "metadata",
    "instance-data",
}


class SSRFSecurityError(ValueError):
    """Raised when an untrusted URL fails SSRF safety boundary verification."""
    pass


def is_ip_prohibited(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> Tuple[bool, str]:
    """Inspects an IP address and determines if it falls into prohibited ranges."""
    # Check IPv4-mapped IPv6 (e.g. ::ffff:127.0.0.1)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return is_ip_prohibited(ip.ipv4_mapped)

    # Built-in attributes
    if ip.is_loopback:
        return True, f"Loopback address ({ip})"
    if ip.is_private:
        return True, f"Private network address ({ip})"
    if ip.is_link_local:
        return True, f"Link-local address ({ip})"
    if ip.is_multicast:
        return True, f"Multicast address ({ip})"
    if ip.is_reserved:
        return True, f"Reserved address ({ip})"
    if ip.is_unspecified:
        return True, f"Unspecified address ({ip})"

    # Explicit subnet ranges check
    if isinstance(ip, ipaddress.IPv4Address):
        for net in BLOCKED_IPV4_NETWORKS:
            if ip in net:
                return True, f"Prohibited IPv4 subnet {net} ({ip})"
    elif isinstance(ip, ipaddress.IPv6Address):
        for net in BLOCKED_IPV6_NETWORKS:
            if ip in net:
                return True, f"Prohibited IPv6 subnet {net} ({ip})"

    return False, ""


def validate_url_syntax(url: str) -> urllib.parse.ParseResult:
    """Validates basic syntax, scheme, credentials, and control characters."""
    if not url or not isinstance(url, str):
        raise SSRFSecurityError("URL must be a non-empty string")

    # Reject whitespace or ASCII control chars
    if any(c in url for c in " \t\r\n\0"):
        raise SSRFSecurityError("URL contains illegal whitespace or control characters")

    parsed = urllib.parse.urlsplit(url)

    if parsed.scheme.lower() != "https":
        raise SSRFSecurityError(f"Prohibited scheme '{parsed.scheme}': only 'https' is permitted")

    if parsed.username or parsed.password:
        raise SSRFSecurityError("Embedded credentials in URL are strictly prohibited")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFSecurityError("URL is missing a valid hostname")

    if hostname.lower() in FORBIDDEN_HOSTNAMES:
        raise SSRFSecurityError(f"Forbidden hostname alias '{hostname}'")

    if hostname.endswith(".localhost") or hostname.endswith(".local") or hostname.endswith(".internal"):
        raise SSRFSecurityError(f"Forbidden local/internal domain suffix '{hostname}'")

    # Validate port if specified
    if parsed.port is not None:
        if not (1 <= parsed.port <= 65535):
            raise SSRFSecurityError(f"Invalid port: {parsed.port}")

    return parsed


def resolve_and_verify_hostname(
    hostname: str,
    port: int = 443,
    dns_resolver=None,
) -> List[Tuple[str, int]]:
    """Resolves hostname and verifies that NO resolved IP is in a prohibited range.

    Returns a list of safe (ip_str, port) tuples.
    Raises SSRFSecurityError if resolution fails or any IP is prohibited.
    """
    # Check if hostname is already a raw IP literal
    try:
        raw_ip = ipaddress.ip_address(hostname.strip("[]"))
        prohibited, reason = is_ip_prohibited(raw_ip)
        if prohibited:
            raise SSRFSecurityError(f"Direct IP access prohibited: {reason}")
        return [(str(raw_ip), port)]
    except ValueError:
        pass  # It is a domain name, proceed to DNS resolution

    resolver = dns_resolver or socket.getaddrinfo
    try:
        addrinfo = resolver(hostname, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
    except (socket.gaierror, socket.herror) as exc:
        raise SSRFSecurityError(f"DNS resolution failure for '{hostname}': {exc}") from exc
    except Exception as exc:
        raise SSRFSecurityError(f"Unexpected error resolving '{hostname}': {exc}") from exc

    if not addrinfo:
        raise SSRFSecurityError(f"No IP addresses returned for '{hostname}'")

    safe_destinations: List[Tuple[str, int]] = []
    seen_ips: Set[str] = set()

    for entry in addrinfo:
        sockaddr = entry[4]
        ip_str = sockaddr[0]
        resolved_port = sockaddr[1]

        if ip_str in seen_ips:
            continue
        seen_ips.add(ip_str)

        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError as exc:
            raise SSRFSecurityError(f"Unparseable resolved IP '{ip_str}': {exc}") from exc

        prohibited, reason = is_ip_prohibited(ip_obj)
        if prohibited:
            raise SSRFSecurityError(
                f"Hostname '{hostname}' resolved to prohibited IP {ip_str}: {reason}"
            )

        safe_destinations.append((ip_str, resolved_port))

    if not safe_destinations:
        raise SSRFSecurityError(f"No valid safe IPs resolved for '{hostname}'")

    return safe_destinations


def validate_and_sanitize_url(url: str) -> Tuple[str, List[Tuple[str, int]]]:
    """Complete SSRF pre-flight validation.

    Returns:
        (sanitized_url, safe_ip_destinations)
    Raises:
        SSRFSecurityError if URL fails any security check.
    """
    parsed = validate_url_syntax(url)
    hostname = parsed.hostname
    assert hostname is not None
    port = parsed.port or 443

    safe_destinations = resolve_and_verify_hostname(hostname, port)

    # Reconstruct sanitized canonical URL without fragment
    sanitized = urllib.parse.urlunsplit((
        "https",
        f"{hostname.lower()}:{port}" if parsed.port and parsed.port != 443 else hostname.lower(),
        parsed.path or "/",
        parsed.query,
        "",  # Strip fragment
    ))

    return sanitized, safe_destinations


def normalize_target_url(url: str) -> str:
    """Normalizes target URL for strict anchor comparison."""
    if not url:
        return ""
    p = urllib.parse.urlsplit(url.strip())
    scheme = (p.scheme or "https").lower()
    netloc = (p.netloc or "").lower()
    if ":" in netloc:
        host, port = netloc.split(":", 1)
        if port == "443" and scheme == "https":
            netloc = host
        elif port == "80" and scheme == "http":
            netloc = host

    path = p.path or "/"
    # Clean redundant slashes
    path = re.sub(r"/+", "/", path)
    # Strip trailing slash if path != "/" for normalized comparison
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    # Rebuild normalized string (ignoring fragment)
    return urllib.parse.urlunsplit((scheme, netloc, path, p.query, ""))
