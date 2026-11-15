"""Unit tests for WP15 Advanced Backlink Verification Engine."""

import unittest

from backlink_agent.advanced_verifier import AdvancedBacklinkVerifier, LinkQualification


class TestAdvancedVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = AdvancedBacklinkVerifier()
        self.target = "https://aitoolgems.tech/prices/"

    def test_editorial_dofollow_anchor_detection(self):
        html = """
        <html>
        <head><title>Tech Blog</title><link rel="canonical" href="https://dev.to/post1"></head>
        <body>
            <p>Check out the comprehensive dataset on <a href="https://aitoolgems.tech/prices/">AI Tool Gems Pricing</a>.</p>
        </body>
        </html>
        """
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://dev.to/post1",
            target_url=self.target,
            http_status=200,
        )
        self.assertTrue(res.anchor_found)
        self.assertTrue(res.is_live_backlink)
        self.assertEqual(res.qualification, LinkQualification.EDITORIAL_DOFOLLOW)
        self.assertEqual(res.actual_anchor_text, "AI Tool Gems Pricing")
        self.assertEqual(res.canonical_url, "https://dev.to/post1")
        self.assertTrue(res.is_indexable)
        self.assertEqual(len(res.content_hash), 16)

    def test_editorial_nofollow_anchor_classification(self):
        html = """
        <p>Reference: <a href="https://aitoolgems.tech/prices/" rel="nofollow">AI Tool Gems</a></p>
        """
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://medium.com/post",
            target_url=self.target,
        )
        self.assertTrue(res.anchor_found)
        self.assertTrue(res.is_live_backlink)  # Legitimate earned citation
        self.assertEqual(res.qualification, LinkQualification.EDITORIAL_NOFOLLOW)
        self.assertIn("nofollow", res.rel_tokens)

    def test_sponsored_anchor_classification(self):
        html = """
        <p>Partner: <a href="https://aitoolgems.tech/prices/" rel="sponsored">Sponsor Tool</a></p>
        """
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://directory.com/sponsored",
            target_url=self.target,
        )
        self.assertTrue(res.anchor_found)
        self.assertTrue(res.is_live_backlink)
        self.assertEqual(res.qualification, LinkQualification.SPONSORED)

    def test_user_generated_ugc_anchor_classification(self):
        html = """
        <p>Comment: <a href="https://aitoolgems.tech/prices/" rel="ugc">Great comparison site</a></p>
        """
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://forum.com/thread",
            target_url=self.target,
        )
        self.assertTrue(res.anchor_found)
        self.assertTrue(res.is_live_backlink)
        self.assertEqual(res.qualification, LinkQualification.USER_GENERATED_UGC)

    def test_source_noindex_meta_tag(self):
        html = """
        <html>
        <head><meta name="robots" content="noindex, follow"></head>
        <body><a href="https://aitoolgems.tech/prices/">Pricing</a></body>
        </html>
        """
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://example.com/draft",
            target_url=self.target,
        )
        self.assertTrue(res.anchor_found)
        self.assertFalse(res.is_live_backlink)  # Ineligible for live equity
        self.assertEqual(res.qualification, LinkQualification.SOURCE_NOINDEX)
        self.assertEqual(res.noindex_source, "meta_robots")

    def test_x_robots_tag_header_noindex(self):
        html = '<a href="https://aitoolgems.tech/prices/">Pricing</a>'
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://example.com/page",
            target_url=self.target,
            response_headers={"X-Robots-Tag": "noindex, nofollow"},
        )
        self.assertFalse(res.is_live_backlink)
        self.assertEqual(res.qualification, LinkQualification.SOURCE_NOINDEX)
        self.assertEqual(res.noindex_source, "x_robots_tag")

    def test_wrong_target_url_on_same_domain(self):
        html = '<a href="https://aitoolgems.tech/tools/chatgpt/">ChatGPT</a>'
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://example.com/tools",
            target_url="https://aitoolgems.tech/prices/",
        )
        self.assertTrue(res.anchor_found)
        self.assertFalse(res.target_matches_approved)
        self.assertFalse(res.is_live_backlink)
        self.assertEqual(res.qualification, LinkQualification.WRONG_TARGET)

    def test_missing_anchor_detection(self):
        html = "<p>AI Tool Gems is mentioned here in plain text without an anchor tag.</p>"
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://example.com/article",
            target_url=self.target,
        )
        self.assertFalse(res.anchor_found)
        self.assertFalse(res.is_live_backlink)
        self.assertEqual(res.qualification, LinkQualification.ANCHOR_MISSING)

    def test_ssrf_security_blocks_private_ips(self):
        """Verifier must refuse to fetch loopback or metadata endpoints."""
        res_meta = self.verifier.verify_url("http://169.254.169.254/latest/meta-data/", self.target)
        self.assertEqual(res_meta.qualification, LinkQualification.SSRF_BLOCKED)
        self.assertFalse(res_meta.is_live_backlink)

        res_local = self.verifier.verify_url("http://127.0.0.1:8080/admin", self.target)
        self.assertEqual(res_local.qualification, LinkQualification.SSRF_BLOCKED)
        self.assertFalse(res_local.is_live_backlink)


if __name__ == "__main__":
    unittest.main()
