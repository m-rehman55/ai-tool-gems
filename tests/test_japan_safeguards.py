import unittest
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from scripts.auto_blog_publisher import validate_queue_candidate
from scripts.generate_sitemap import collect_indexable_pages
from scripts.validate_content import validate_article_file
from importlib import import_module

scope_guard_mod = import_module("seo-agent.agent.scope_guard")
ScopeGuard = scope_guard_mod.ScopeGuard


class TestJapanSafeguards(unittest.TestCase):
    """Enforces permanent exclusion of all Japan-related URLs, content, and metadata."""

    def test_queue_candidate_rejects_japan_tokens(self):
        base_item = {
            "slug": "sample-ai-tool-pakistan",
            "title": "Best AI Tools in Pakistan (2026)",
            "meta_description": "Explore top AI tools available in Pakistan with flat PKR pricing and EasyPaisa JazzCash support.",
            "primary_keyword": "ai tools pakistan",
            "secondary_keywords": ["best ai tools", "pakistan software", "ai apps"],
            "primary_tool": "Gemini",
            "related_tools": ["ChatGPT"],
            "approved_for_publishing": True,
            "pakistani_payment_support": ["EasyPaisa", "JazzCash"]
        }

        # Clean item passes
        is_valid, errors = validate_queue_candidate(base_item)
        self.assertTrue(is_valid, f"Expected clean item to pass, got errors: {errors}")

        # Test each forbidden token
        forbidden_tokens = ["japan", "japanese", "tokyo", "osaka", "kyoto", "-jp-", "jpy", "¥"]
        for tok in forbidden_tokens:
            bad_item = dict(base_item)
            bad_item["title"] = f"Best AI Tools in {tok.capitalize()} (2026)"
            is_valid, errors = validate_queue_candidate(bad_item)
            self.assertFalse(is_valid, f"Expected token '{tok}' to be rejected")
            self.assertTrue(any("Foreign scope violation" in e for e in errors), f"Expected foreign scope error for '{tok}'")

    def test_sitemap_generator_excludes_japan_routes(self):
        pages = collect_indexable_pages(ROOT_DIR)
        urls = [p["url"] for p in pages]
        self.assertGreater(len(urls), 50, "Expected at least 50 indexable pages in repository")
        for u in urls:
            self.assertNotIn("/jp/", u, f"Prohibited /jp/ URL found in sitemap: {u}")
            self.assertFalse(u.rstrip("/").endswith("/jp"), f"Prohibited /jp root URL in sitemap: {u}")
            self.assertNotIn("japan", u.lower(), f"Prohibited 'japan' in sitemap URL: {u}")

    def test_scope_guard_blocks_all_japan_references(self):
        guard = ScopeGuard()
        prohibited_samples = [
            "https://aitoolgems.tech/jp/tools/gemini/",
            "Buy AI tools in Tokyo with JPY",
            "Total price: ¥3500",
            "Available in Osaka and Kyoto",
            "Japanese yen payment gateway"
        ]
        for sample in prohibited_samples:
            res = guard.check_text(sample, "test_sample")
            self.assertFalse(res.passed, f"Expected ScopeGuard to reject: '{sample}'")
            self.assertGreater(len(res.violations), 0)


if __name__ == "__main__":
    unittest.main()

