from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketing_agent.catalog import load_products
from marketing_agent.config import Settings, resolve_timezone
from marketing_agent.content import build_drafts, generate_days
from marketing_agent.db import connect, database_status, initialize
from marketing_agent.metrics import record_metrics
from marketing_agent.posting import approve_posts
from marketing_agent.reporting import build_report
from marketing_agent.seo_monitor import inspect_homepage
from marketing_agent.social import daily_pack, send_daily_pack
from marketing_agent.tracking import product_url
from marketing_agent.trial import claim_slot, trial_plan


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(
            database_path=Path(self.temp.name) / "agent.db",
            site_url="https://aitoolgems.tech",
            whatsapp_number="923476242709",
            timezone=resolve_timezone("Asia/Karachi"),
            telegram_bot_token="",
            telegram_channel_id="",
            telegram_owner_chat_id="",
            posts_per_day=3,
            auto_approve=False,
        )
        initialize(self.settings.database_path)

    def tearDown(self):
        self.temp.cleanup()

    def test_catalog_has_all_products(self):
        self.assertEqual(len(load_products()), 20)
        self.assertEqual(database_status(self.settings.database_path)["products"], 20)

    def test_generation_is_unique_and_rotates(self):
        inserted, duplicates = generate_days(self.settings, date(2026, 9, 12), 3)
        self.assertEqual((inserted, duplicates), (9, 0))
        with connect(self.settings.database_path) as connection:
            rows = connection.execute("SELECT product_id, caption_hash, tracking_code FROM posts").fetchall()
        self.assertEqual(len({row["caption_hash"] for row in rows}), 9)
        self.assertEqual(len({row["tracking_code"] for row in rows}), 9)
        self.assertEqual(len({row["product_id"] for row in rows}), 9)

    def test_duplicate_generation_is_skipped(self):
        first = generate_days(self.settings, date(2026, 9, 12), 1)
        second = generate_days(self.settings, date(2026, 9, 12), 1)
        self.assertEqual(first, (3, 0))
        self.assertEqual(second, (0, 3))

    def test_approval_metrics_and_report(self):
        generate_days(self.settings, date.today(), 1)
        self.assertEqual(approve_posts(self.settings), 3)
        with connect(self.settings.database_path) as connection:
            post_id = connection.execute("SELECT id FROM posts LIMIT 1").fetchone()[0]
            connection.execute("UPDATE posts SET status='published' WHERE id=?", (post_id,))
        record_metrics(self.settings, post_id, clicks=5, orders=1, revenue=2300, source="test")
        report = build_report(self.settings, date.today())
        self.assertIn("Orders: 1", report)
        self.assertIn("Rs. 2,300", report)

    def test_tracking_url_contains_source(self):
        url = product_url("https://aitoolgems.tech", "chatgpt", "tg-chatgpt-20260912-a")
        self.assertIn("utm_source=telegram", url)
        self.assertIn("src=tg-chatgpt-20260912-a", url)

    def test_captions_disclose_independence(self):
        draft = build_drafts(self.settings, date(2026, 9, 12), 1)[0]
        self.assertIn("Independent reseller", draft.caption)
        self.assertIn("Rs.", draft.caption)

    def test_trial_plan_has_nine_unique_tracked_posts(self):
        plan = trial_plan(self.settings)
        self.assertEqual(len(plan), 9)
        self.assertEqual(len({row["key"] for row in plan}), 9)
        self.assertEqual(len({row["product_id"] for row in plan}), 9)
        self.assertTrue(all("utm_source=telegram" in row["target_url"] for row in plan))

    def test_seo_monitor_accepts_complete_homepage_signals(self):
        html = '''<!doctype html><html><head>
        <title>AI Tool Gems Pakistan Marketplace</title>
        <meta name="description" content="Compare AI tools and digital subscriptions in Pakistan with clear PKR prices, access terms, delivery details and direct support before ordering.">
        <link rel="canonical" href="https://aitoolgems.tech/">
        <script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization"},{"@type":"WebSite"},{"@type":"ItemList"}]}</script>
        </head><body><h1>AI tools in Pakistan</h1></body></html>'''
        self.assertEqual(inspect_homepage(html, "https://aitoolgems.tech/"), [])

    def test_trial_claim_is_duplicate_safe(self):
        ledger = Path(self.temp.name) / "ledger.json"
        payload = Path(self.temp.name) / "payload.json"
        first = claim_slot(self.settings, date(2026, 9, 12), 0, payload, ledger)
        second = claim_slot(self.settings, date(2026, 9, 12), 0, payload, ledger)
        self.assertIsNotNone(first)
        self.assertIsNone(second)

    def test_social_pack_covers_owned_platforms(self):
        pack = "\n".join(daily_pack(self.settings, date(2026, 9, 12)))
        for platform in ("INSTAGRAM", "FACEBOOK", "WHATSAPP STATUS", "REEL/TIKTOK"):
            self.assertIn(platform, pack)
        for source in ("instagram", "facebook", "whatsapp", "tiktok"):
            self.assertIn(f"utm_source={source}", pack)

    def test_already_sent_social_pack_is_skipped_without_api_call(self):
        state = Path(self.temp.name) / "social-state.json"
        state.write_text('{"sent_dates":{"2026-09-12":{"messages":5}}}', encoding="utf-8")
        self.assertEqual(send_daily_pack(self.settings, date(2026, 9, 12), state), 0)


if __name__ == "__main__":
    unittest.main()
