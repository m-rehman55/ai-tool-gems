#!/usr/bin/env python3
"""
Unit and regression tests for AIToolGems Autonomous Daily Blog Publisher & Sitemap Engine.
Verifies queue validation, candidate selection, duplicate prevention, fail-safe cleanup,
sitemap ElementTree XML generation, and truth policy enforcement.
"""

import unittest
import tempfile
import shutil
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from scripts.auto_blog_publisher import (
    validate_queue_candidate,
    load_queue_candidate,
    run_publisher
)
from scripts.generate_sitemap import (
    build_sitemap,
    validate_sitemap_file,
    collect_indexable_pages
)


class TestAutoBlogPublisherSafeguards(unittest.TestCase):
    """Test suite covering safe candidate selection, validation, and publisher lifecycle."""

    def setUp(self):
        self.valid_sample_candidate = {
            "slug": "deepseek-ai-pakistan",
            "title": "DeepSeek AI in Pakistan: Pricing, Local Access & Guide (2026)",
            "meta_description": "Complete guide to DeepSeek V3 and R1 reasoning models in Pakistan. Review local PKR payment methods via EasyPaisa and JazzCash without card declines.",
            "primary_keyword": "DeepSeek AI Pakistan",
            "secondary_keywords": [
                "DeepSeek price in Pakistan",
                "DeepSeek R1 reasoning PKR",
                "DeepSeek API credits Pakistan",
                "DeepSeek vs ChatGPT Plus"
            ],
            "target_audience": "Pakistani software developers, data scientists, and university students",
            "primary_tool": "deepseek",
            "related_tools": [
                {"slug": "deepseek", "name": "DeepSeek V3 / R1"},
                {"slug": "chatgpt", "name": "ChatGPT Plus"},
                {"slug": "claude", "name": "Claude 3.5 Sonnet"}
            ],
            "official_sources": [
                "https://www.deepseek.com",
                "https://platform.deepseek.com/pricing"
            ],
            "pakistani_payment_support": ["EasyPaisa", "JazzCash", "SadaPay", "NayaPay", "Bank IBFT"],
            "approved_for_publishing": True,
            "priority": 7
        }

    def test_queue_approval_requires_explicit_boolean_true(self):
        """Require approved_for_publishing to be strictly boolean True (fail closed on false/missing/truthy)."""
        # 1. Explicit False
        item_false = dict(self.valid_sample_candidate, approved_for_publishing=False)
        ok, errs = validate_queue_candidate(item_false)
        self.assertFalse(ok)
        self.assertTrue(any("approved_for_publishing" in e for e in errs))

        # 2. Missing field
        item_missing = dict(self.valid_sample_candidate)
        del item_missing["approved_for_publishing"]
        ok, errs = validate_queue_candidate(item_missing)
        self.assertFalse(ok)
        self.assertTrue(any("approved_for_publishing" in e for e in errs))

        # 3. Truthy string or integer (not boolean True)
        item_string = dict(self.valid_sample_candidate, approved_for_publishing="true")
        ok, errs = validate_queue_candidate(item_string)
        self.assertFalse(ok)

        item_int = dict(self.valid_sample_candidate, approved_for_publishing=1)
        ok, errs = validate_queue_candidate(item_int)
        self.assertFalse(ok)

    def test_malformed_queue_entry_missing_required_fields(self):
        """Reject queue items missing required fields."""
        required = [
            "slug", "title", "meta_description", "primary_keyword",
            "secondary_keywords", "primary_tool", "related_tools",
            "pakistani_payment_support"
        ]
        for field in required:
            item = dict(self.valid_sample_candidate)
            del item[field]
            ok, errs = validate_queue_candidate(item)
            self.assertFalse(ok, f"Item missing '{field}' should fail validation.")
            self.assertTrue(any(field in e for e in errs))

    def test_malformed_queue_entry_invalid_slug_format(self):
        """Enforce strict lowercase kebab-case slug regex."""
        invalid_slugs = [
            "DeepSeek-AI",
            "deepseek_ai_pakistan",
            "deepseek ai pakistan",
            "-deepseek-pakistan",
            "deepseek-pakistan-",
            "deepseek--pakistan",
            "deepseek!@pakistan"
        ]
        for bad_slug in invalid_slugs:
            item = dict(self.valid_sample_candidate, slug=bad_slug)
            ok, errs = validate_queue_candidate(item)
            self.assertFalse(ok, f"Slug '{bad_slug}' should be rejected.")
            self.assertTrue(any("slug" in e.lower() for e in errs))

    def test_duplicate_slug_rejection(self):
        """Reject queue candidate if its slug is already present in published_slugs."""
        published = {"deepseek-ai-pakistan", "perplexity-ai-pakistan"}
        ok, errs = validate_queue_candidate(self.valid_sample_candidate, published_slugs=published)
        self.assertFalse(ok)
        self.assertTrue(any("already published" in e.lower() for e in errs))

    def test_title_and_meta_description_length_bounds(self):
        """Ensure title (20-70 chars) and meta description (70-170 chars) bounds are enforced."""
        # Short title
        item_short_title = dict(self.valid_sample_candidate, title="Short Title")
        ok, errs = validate_queue_candidate(item_short_title)
        self.assertFalse(ok)
        self.assertTrue(any("title length" in e.lower() for e in errs))

        # Long title
        item_long_title = dict(self.valid_sample_candidate, title="This is an extremely overly long title intended to exceed the 70-character SEO title threshold completely")
        ok, errs = validate_queue_candidate(item_long_title)
        self.assertFalse(ok)

        # Short meta description
        item_short_desc = dict(self.valid_sample_candidate, meta_description="Too short description.")
        ok, errs = validate_queue_candidate(item_short_desc)
        self.assertFalse(ok)
        self.assertTrue(any("meta description length" in e.lower() for e in errs))

    def test_secondary_keywords_count_and_payment_rails(self):
        """Require at least 3 secondary keywords and verified Pakistani payment rails."""
        item_few_kws = dict(self.valid_sample_candidate, secondary_keywords=["kw1", "kw2"])
        ok, errs = validate_queue_candidate(item_few_kws)
        self.assertFalse(ok)
        self.assertTrue(any("secondary keywords" in e.lower() for e in errs))

        item_no_pak_pay = dict(self.valid_sample_candidate, pakistani_payment_support=["Stripe", "PayPal"])
        ok, errs = validate_queue_candidate(item_no_pak_pay)
        self.assertFalse(ok)
        self.assertTrue(any("pakistani" in e.lower() for e in errs))

    def test_no_eligible_topics_handling(self):
        """When all topics are published or unapproved, publisher reports NO_ELIGIBLE_TOPIC distinctly without errors."""
        with patch("scripts.auto_blog_publisher.load_queue_candidate", return_value=(None, "NO_ELIGIBLE_TOPIC")):
            status = run_publisher(dry_run=True)
            self.assertEqual(status, "NO_ELIGIBLE_TOPIC")

    def test_failed_validation_cleans_up_temporary_files(self):
        """If article validation fails, temporary directory and file are completely cleaned up."""
        test_slug = "unit-test-fail-cleanup"
        mock_cand = dict(self.valid_sample_candidate, slug=test_slug)

        with patch("scripts.auto_blog_publisher.load_queue_candidate", return_value=(mock_cand, "CANDIDATE_FOUND")):
            with patch("scripts.auto_blog_publisher.validate_article_file", return_value=(False, ["Mock validation failure"])):
                status = run_publisher(dry_run=True)
                self.assertEqual(status, "VALIDATION_FAILED")

                # Verify file and directory do not exist
                temp_path = Path("guides") / test_slug / "index.html"
                self.assertFalse(temp_path.exists())
                self.assertFalse((Path("guides") / test_slug).exists())


class TestSitemapAutomationSafeguards(unittest.TestCase):
    """Test suite covering XML generation, escaping, date accuracy, and strict validation."""

    def test_collect_indexable_pages_excludes_noindex_and_admin(self):
        """Ensure admin, 404, checklist, and noindex pages are strictly excluded from indexable set."""
        pages = collect_indexable_pages()
        urls = [p["url"] for p in pages]

        # Ensure no excluded pages present
        for u in urls:
            self.assertFalse(u.endswith("admin.html"))
            self.assertFalse(u.endswith("404.html"))
            self.assertFalse(u.endswith("gsc_daily_checklist.html"))
            self.assertTrue(u.startswith("https://aitoolgems.tech/"))

        # Verify uniqueness
        self.assertEqual(len(urls), len(set(urls)), "Sitemap indexable URLs must be strictly unique.")

    def test_sitemap_xml_element_tree_validity_and_formatting(self):
        """Generate sitemap and verify XML well-formedness, namespace, and date formats."""
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tf:
            temp_sitemap_path = Path(tf.name)

        try:
            ok, msg, count = build_sitemap(output_file=temp_sitemap_path)
            self.assertTrue(ok, f"build_sitemap failed: {msg}")
            self.assertGreater(count, 50)

            # Re-parse generated XML with ElementTree
            tree = ET.parse(str(temp_sitemap_path))
            root = tree.getroot()
            self.assertTrue(root.tag.endswith("urlset"))

            # Validate each URL element
            urls_in_xml = []
            for url_el in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                loc_el = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                lastmod_el = url_el.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")

                self.assertIsNotNone(loc_el)
                self.assertIsNotNone(loc_el.text)
                self.assertTrue(loc_el.text.startswith("https://aitoolgems.tech/"))

                self.assertIsNotNone(lastmod_el)
                self.assertIsNotNone(lastmod_el.text)
                # Verify date format YYYY-MM-DD
                self.assertRegex(lastmod_el.text, r"^\d{4}-\d{2}-\d{2}$")

                urls_in_xml.append(loc_el.text)

            # Assert strict uniqueness
            self.assertEqual(len(urls_in_xml), len(set(urls_in_xml)))

            # Run strict validator
            valid_ok, errors = validate_sitemap_file(temp_sitemap_path)
            self.assertTrue(valid_ok, f"Sitemap validation failed with: {errors}")

        finally:
            if temp_sitemap_path.exists():
                temp_sitemap_path.unlink()


if __name__ == "__main__":
    unittest.main()
