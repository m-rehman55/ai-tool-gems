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
    normalize_target_url,
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


if __name__ == "__main__":
    unittest.main()
