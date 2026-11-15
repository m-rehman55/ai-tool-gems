"""Unit tests for Worker Anchor Verifier and URL Validation."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

WORKER_DIR = Path(__file__).resolve().parents[1]
if str(WORKER_DIR) not in sys.path:
    sys.path.insert(0, str(WORKER_DIR))

from src.verifier_worker import (
    classify_rel_tokens,
    is_html_content_type,
    normalize_target_url,
    validate_redirect_chain,
    validate_redirect_hop,
    validate_worker_url,
    verify_html_content,
)


class TestWorkerVerifier(unittest.TestCase):

    def test_plain_text_without_anchor_is_removed(self):
        html = "<p>aitoolgems.tech provides AI tools.</p>"
        res = verify_html_content(html, "https://example.com", "https://aitoolgems.tech/")
        self.assertFalse(res["target_found"])
        self.assertEqual(res["classification"], "removed")

    def test_real_anchor_live_follow(self):
        html = '<p>Check <a href="https://aitoolgems.tech/">AI Tool Gems</a></p>'
        res = verify_html_content(html, "https://example.com", "https://aitoolgems.tech/")
        self.assertTrue(res["target_found"])
        self.assertEqual(res["classification"], "live_follow")
        self.assertEqual(res["actual_anchor_text"], "AI Tool Gems")

    def test_rel_token_classifications(self):
        self.assertEqual(classify_rel_tokens(["nofollow"]), "live_nofollow")
        self.assertEqual(classify_rel_tokens(["sponsored"]), "live_sponsored")
        self.assertEqual(classify_rel_tokens(["ugc"]), "live_ugc")
        self.assertEqual(classify_rel_tokens(["nofollow", "ugc"]), "live_mixed")
        self.assertEqual(classify_rel_tokens([]), "live_follow")

    def test_noindex_meta_sets_source_noindex(self):
        html = '<html><head><meta name="robots" content="noindex"></head><body><a href="https://aitoolgems.tech/">Link</a></body></html>'
        res = verify_html_content(html, "https://example.com", "https://aitoolgems.tech/")
        self.assertTrue(res["target_found"])
        self.assertTrue(res["is_noindex"])
        self.assertEqual(res["classification"], "source_noindex")

    def test_validate_worker_url_blocks_insecure_schemes(self):
        with self.assertRaises(ValueError):
            validate_worker_url("http://example.com")
        with self.assertRaises(ValueError):
            validate_worker_url("ftp://example.com")
        with self.assertRaises(ValueError):
            validate_worker_url("https://localhost/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://metadata.google.internal/")
        # Blocks IP literals in blocked ranges
        with self.assertRaises(ValueError):
            validate_worker_url("https://127.0.0.1/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://169.254.169.254/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://10.0.0.1/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://192.168.1.1/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://0.0.0.1/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://100.64.0.1/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://192.0.0.1/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://198.18.0.1/")
        with self.assertRaises(ValueError):
            validate_worker_url("https://240.0.0.1/")

    def test_validate_worker_url_blocks_ipv6_special_ranges_and_mapped(self):
        # IPv6 loopback
        with self.assertRaises(ValueError):
            validate_worker_url("https://[::1]/")
        # IPv6 link-local
        with self.assertRaises(ValueError):
            validate_worker_url("https://[fe80::1]/")
        # IPv6 ULA
        with self.assertRaises(ValueError):
            validate_worker_url("https://[fc00::1]/")
        # IPv6 multicast
        with self.assertRaises(ValueError):
            validate_worker_url("https://[ff02::1]/")
        # IPv4-mapped IPv6 loopback
        with self.assertRaises(ValueError):
            validate_worker_url("https://[::ffff:127.0.0.1]/")
        # IPv4-mapped IPv6 metadata
        with self.assertRaises(ValueError):
            validate_worker_url("https://[::ffff:169.254.169.254]/")
        # IPv4-mapped IPv6 private
        with self.assertRaises(ValueError):
            validate_worker_url("https://[::ffff:10.0.0.1]/")

    def test_validate_redirect_chain_and_loop_detection(self):
        # Valid 2-hop chain
        final_url = validate_redirect_chain(
            "https://start.com/entry",
            ["/step1", "https://destination.com/final"],
            max_hops=5,
        )
        self.assertEqual(final_url, "https://destination.com/final")

        # Redirect loop detection
        with self.assertRaises(ValueError) as ctx_loop:
            validate_redirect_chain(
                "https://start.com/entry",
                ["/step1", "https://start.com/entry"],
                max_hops=5,
            )
        self.assertIn("Redirect loop detected", str(ctx_loop.exception))

        # Excessive hops detection (> max_hops)
        with self.assertRaises(ValueError) as ctx_hops:
            validate_redirect_chain(
                "https://start.com/entry",
                ["/1", "/2", "/3", "/4", "/5", "/6"],
                max_hops=5,
            )
        self.assertIn("Excessive redirects", str(ctx_hops.exception))

        # Redirect chain terminating in forbidden SSRF IP
        with self.assertRaises(ValueError):
            validate_redirect_chain(
                "https://start.com/entry",
                ["/safe", "https://169.254.169.254/latest/meta-data"],
                max_hops=5,
            )

    def test_validate_redirect_hop(self):
        # Valid relative redirect
        res1 = validate_redirect_hop("https://example.com/start", "/final")
        self.assertEqual(res1, "https://example.com/final")

        # Valid absolute HTTPS redirect
        res2 = validate_redirect_hop("https://example.com/start", "https://trusted-site.com/page")
        self.assertEqual(res2, "https://trusted-site.com/page")

        # Blocked redirect to loopback
        with self.assertRaises(ValueError):
            validate_redirect_hop("https://example.com/start", "https://127.0.0.1/admin")

        # Blocked redirect to private network
        with self.assertRaises(ValueError):
            validate_redirect_hop("https://example.com/start", "https://10.0.0.1/internal")

        # Blocked redirect to HTTP
        with self.assertRaises(ValueError):
            validate_redirect_hop("https://example.com/start", "http://insecure.com/target")

    def test_is_html_content_type(self):
        self.assertTrue(is_html_content_type("text/html; charset=utf-8"))
        self.assertTrue(is_html_content_type("application/xhtml+xml"))
        self.assertFalse(is_html_content_type("application/json"))
        self.assertFalse(is_html_content_type("application/pdf"))
        self.assertFalse(is_html_content_type("image/png"))
        self.assertFalse(is_html_content_type(None))
        self.assertFalse(is_html_content_type(""))


if __name__ == "__main__":
    unittest.main()
