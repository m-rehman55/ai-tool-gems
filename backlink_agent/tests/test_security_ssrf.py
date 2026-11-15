"""Unit tests for Backlink Agent SSRF Guard and URL Safety Boundaries."""

from __future__ import annotations

import ipaddress
import socket
import unittest
from unittest.mock import patch

from backlink_agent.security import (
    SSRFSecurityError,
    is_ip_prohibited,
    resolve_and_verify_hostname,
    validate_and_sanitize_url,
    validate_url_syntax,
)


class TestSSRFSecurity(unittest.TestCase):

    def test_rejects_non_https_schemes(self):
        disallowed = [
            "http://example.com/page",
            "ftp://example.com/file",
            "file:///etc/passwd",
            "gopher://example.com/",
            "data:text/html,<html></html>",
            "javascript:alert(1)",
        ]
        for url in disallowed:
            with self.subTest(url=url):
                with self.assertRaises(SSRFSecurityError) as ctx:
                    validate_url_syntax(url)
                self.assertIn("permitted", str(ctx.exception).lower())

    def test_rejects_embedded_credentials(self):
        urls = [
            "https://user:pass@example.com/path",
            "https://admin@example.com/",
        ]
        for url in urls:
            with self.subTest(url=url):
                with self.assertRaises(SSRFSecurityError) as ctx:
                    validate_url_syntax(url)
                self.assertIn("credentials", str(ctx.exception).lower())

    def test_rejects_forbidden_hostnames(self):
        hostnames = [
            "https://localhost/test",
            "https://localhost.localdomain/",
            "https://metadata.google.internal/computeMetadata/v1/",
            "https://test.local/",
            "https://service.internal/",
        ]
        for url in hostnames:
            with self.subTest(url=url):
                with self.assertRaises(SSRFSecurityError) as ctx:
                    validate_url_syntax(url)

    def test_is_ip_prohibited_ipv4_boundaries(self):
        prohibited_ips = [
            "127.0.0.1",        # loopback
            "127.255.255.255",  # loopback range
            "10.0.0.1",         # RFC 1918
            "10.255.255.254",   # RFC 1918
            "172.16.0.1",       # RFC 1918
            "172.31.255.254",   # RFC 1918
            "192.168.1.1",      # RFC 1918
            "169.254.169.254",  # AWS/GCP link-local metadata
            "100.64.0.1",       # CGNAT
            "100.127.255.254",  # CGNAT
            "0.0.0.0",          # Current network
            "0.0.0.1",          # 0.0.0.0/8 host
            "192.0.0.1",        # IETF protocol assignments RFC 6890
            "192.0.2.1",        # TEST-NET-1
            "198.18.0.1",       # Network benchmark RFC 2544
            "198.51.100.1",     # TEST-NET-2
            "203.0.113.1",      # TEST-NET-3
            "224.0.0.1",        # Multicast
            "240.0.0.1",        # Reserved
            "255.255.255.255",  # Broadcast
        ]
        for ip_s in prohibited_ips:
            with self.subTest(ip=ip_s):
                prohibited, reason = is_ip_prohibited(ipaddress.ip_address(ip_s))
                self.assertTrue(prohibited, f"Expected {ip_s} to be prohibited")
                self.assertTrue(len(reason) > 0)

    def test_is_ip_prohibited_ipv6_boundaries(self):
        prohibited_ipv6 = [
            "::1",                 # IPv6 loopback
            "::",                  # IPv6 unspecified
            "fc00::1",             # ULA
            "fd12:3456:789a::1",   # ULA
            "fe80::1",             # Link-local
            "ff02::1",             # Multicast
            "::ffff:127.0.0.1",    # IPv4-mapped loopback
            "::ffff:10.0.0.1",     # IPv4-mapped private
            "::ffff:169.254.169.254", # IPv4-mapped metadata
            "2001:db8::1",         # Documentation
        ]
        for ip_s in prohibited_ipv6:
            with self.subTest(ip=ip_s):
                prohibited, reason = is_ip_prohibited(ipaddress.ip_address(ip_s))
                self.assertTrue(prohibited, f"Expected {ip_s} to be prohibited")

    def test_public_ips_allowed(self):
        public_ips = [
            "8.8.8.8",
            "1.1.1.1",
            "142.250.190.46",  # Google
            "2607:f8b0:4005:808::200e", # Google IPv6
        ]
        for ip_s in public_ips:
            with self.subTest(ip=ip_s):
                prohibited, _ = is_ip_prohibited(ipaddress.ip_address(ip_s))
                self.assertFalse(prohibited, f"Expected {ip_s} to be allowed")

    def test_hostname_resolving_to_private_ip_is_blocked(self):
        # Mock DNS resolver returning a private IP
        mock_addrinfo = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 443))
        ]
        with patch("socket.getaddrinfo", return_value=mock_addrinfo):
            with self.assertRaises(SSRFSecurityError) as ctx:
                resolve_and_verify_hostname("internal.example.com", 443)
            self.assertIn("prohibited ip", str(ctx.exception).lower())

    def test_hostname_resolving_to_metadata_ip_is_blocked(self):
        mock_addrinfo = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", 443))
        ]
        with patch("socket.getaddrinfo", return_value=mock_addrinfo):
            with self.assertRaises(SSRFSecurityError) as ctx:
                resolve_and_verify_hostname("metadata.niceroute.com", 443)
            self.assertIn("prohibited ip", str(ctx.exception).lower())

    def test_hostname_resolving_to_mixed_public_and_private_is_blocked(self):
        mock_addrinfo = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.50", 443)),
        ]
        with patch("socket.getaddrinfo", return_value=mock_addrinfo):
            with self.assertRaises(SSRFSecurityError) as ctx:
                resolve_and_verify_hostname("dual-homed.example.com", 443)
            self.assertIn("prohibited ip", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
