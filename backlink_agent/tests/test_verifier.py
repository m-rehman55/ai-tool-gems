"""Unit tests for Backlink HTML Parser and Verifier."""

from __future__ import annotations

import unittest
from backlink_agent.verifier import BacklinkHTMLParser, parse_and_verify_html, classify_rel_tokens


class TestBacklinkVerifier(unittest.TestCase):

    def test_plain_text_mention_without_anchor_is_not_live(self):
        html = """
        <html>
        <body>
            <p>We recommend checking aitoolgems.tech for the latest AI tools in Pakistan.</p>
        </body>
        </html>
        """
        classification, found, anchor_text, rel_tokens, is_noindex, canonical = parse_and_verify_html(
            html_text=html,
            base_url="https://example.com/article",
            target_url="https://aitoolgems.tech/",
        )
        self.assertFalse(found)
        self.assertEqual(classification, "removed")
        self.assertEqual(anchor_text, "")

    def test_real_absolute_anchor_dofollow_is_live_follow(self):
        html = """
        <html>
        <body>
            <p>Visit <a href="https://aitoolgems.tech/">AI Tool Gems</a> for pricing.</p>
        </body>
        </html>
        """
        classification, found, anchor_text, rel_tokens, is_noindex, canonical = parse_and_verify_html(
            html_text=html,
            base_url="https://example.com/post",
            target_url="https://aitoolgems.tech/",
        )
        self.assertTrue(found)
        self.assertEqual(classification, "live_follow")
        self.assertEqual(anchor_text, "AI Tool Gems")
        self.assertEqual(rel_tokens, [])

    def test_relative_anchor_resolved_to_target(self):
        html = """
        <html>
        <body>
            <a href="/prices/">Pakistan Pricing Dataset</a>
        </body>
        </html>
        """
        classification, found, anchor_text, rel_tokens, is_noindex, canonical = parse_and_verify_html(
            html_text=html,
            base_url="https://aitoolgems.tech/blog/intro",
            target_url="https://aitoolgems.tech/prices/",
        )
        self.assertTrue(found)
        self.assertEqual(classification, "live_follow")
        self.assertEqual(anchor_text, "Pakistan Pricing Dataset")

    def test_anchor_to_wrong_target_on_same_domain(self):
        html = """
        <html>
        <body>
            <a href="https://aitoolgems.tech/tools/chatgpt/">ChatGPT Deal</a>
        </body>
        </html>
        """
        classification, found, anchor_text, rel_tokens, is_noindex, canonical = parse_and_verify_html(
            html_text=html,
            base_url="https://example.com/list",
            target_url="https://aitoolgems.tech/prices/",
        )
        self.assertFalse(found)
        self.assertEqual(classification, "wrong_target")
        self.assertEqual(anchor_text, "ChatGPT Deal")

    def test_rel_classifications_exact(self):
        # nofollow
        h1 = '<a href="https://aitoolgems.tech/" rel="nofollow">Link</a>'
        c1, f1, _, rel1, _, _ = parse_and_verify_html(h1, "https://ex.com", "https://aitoolgems.tech/")
        self.assertEqual(c1, "live_nofollow")
        self.assertEqual(rel1, ["nofollow"])

        # sponsored
        h2 = '<a href="https://aitoolgems.tech/" rel="sponsored">Link</a>'
        c2, f2, _, rel2, _, _ = parse_and_verify_html(h2, "https://ex.com", "https://aitoolgems.tech/")
        self.assertEqual(c2, "live_sponsored")
        self.assertEqual(rel2, ["sponsored"])

        # ugc
        h3 = '<a href="https://aitoolgems.tech/" rel="ugc">Link</a>'
        c3, f3, _, rel3, _, _ = parse_and_verify_html(h3, "https://ex.com", "https://aitoolgems.tech/")
        self.assertEqual(c3, "live_ugc")
        self.assertEqual(rel3, ["ugc"])

        # mixed (nofollow ugc)
        h4 = '<a href="https://aitoolgems.tech/" rel="nofollow ugc noopener">Link</a>'
        c4, f4, _, rel4, _, _ = parse_and_verify_html(h4, "https://ex.com", "https://aitoolgems.tech/")
        self.assertEqual(c4, "live_mixed")
        self.assertIn("nofollow", rel4)
        self.assertIn("ugc", rel4)

    def test_source_page_meta_noindex_classifies_source_noindex(self):
        html = """
        <html>
        <head>
            <meta name="robots" content="noindex, follow">
        </head>
        <body>
            <a href="https://aitoolgems.tech/">AI Tool Gems</a>
        </body>
        </html>
        """
        classification, found, _, _, is_noindex, _ = parse_and_verify_html(
            html_text=html,
            base_url="https://example.com/page",
            target_url="https://aitoolgems.tech/",
        )
        self.assertTrue(found)
        self.assertTrue(is_noindex)
        self.assertEqual(classification, "source_noindex")

    def test_source_page_x_robots_tag_header_noindex(self):
        html = '<a href="https://aitoolgems.tech/">AI Tool Gems</a>'
        headers = {"X-Robots-Tag": "noindex, noarchive"}
        classification, found, _, _, is_noindex, _ = parse_and_verify_html(
            html_text=html,
            base_url="https://example.com/page",
            target_url="https://aitoolgems.tech/",
            response_headers=headers,
        )
        self.assertTrue(found)
        self.assertTrue(is_noindex)
        self.assertEqual(classification, "source_noindex")

    def test_trailing_slash_and_fragment_tolerance(self):
        # Target has trailing slash, anchor has no trailing slash
        h1 = '<a href="https://aitoolgems.tech">Home</a>'
        c1, f1, _, _, _, _ = parse_and_verify_html(h1, "https://ex.com", "https://aitoolgems.tech/")
        self.assertTrue(f1)
        self.assertEqual(c1, "live_follow")

        # Anchor has client fragment, target does not
        h2 = '<a href="https://aitoolgems.tech/#pricing">Home Pricing</a>'
        c2, f2, _, _, _, _ = parse_and_verify_html(h2, "https://ex.com", "https://aitoolgems.tech/")
        self.assertTrue(f2)
        self.assertEqual(c2, "live_follow")

    def test_query_parameters_preserved(self):
        h = '<a href="https://aitoolgems.tech/prices/?ref=directory">Pricing</a>'
        # Exact match with query
        c1, f1, _, _, _, _ = parse_and_verify_html(
            h, "https://ex.com", "https://aitoolgems.tech/prices/?ref=directory"
        )
        self.assertTrue(f1)
        self.assertEqual(c1, "live_follow")

        # Mismatch if target query differs
        c2, f2, _, _, _, _ = parse_and_verify_html(
            h, "https://ex.com", "https://aitoolgems.tech/prices/?ref=other"
        )
        self.assertFalse(f2)


if __name__ == "__main__":
    unittest.main()
