from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from marketing_agent.catalog import load_products
from marketing_agent.buffer import (
    BufferClient,
    connection_status,
    learned_audience_for,
    publish_daily_deal,
    refresh_performance,
    scheduled_time,
)
from marketing_agent.config import Settings, resolve_timezone
from marketing_agent.content import build_drafts, generate_days
from marketing_agent.db import connect, database_status, initialize
from marketing_agent.metrics import record_metrics
from marketing_agent.posting import approve_posts
from marketing_agent.reporting import build_report
from marketing_agent.seo_monitor import inspect_homepage
from marketing_agent.social import audience_for, caption_for_platform, daily_pack, deal_of_the_day, send_daily_pack
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
            buffer_api_key="",
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
        for platform in ("INSTAGRAM", "FACEBOOK", "WHATSAPP STATUS", "TIKTOK/REEL"):
            self.assertIn(platform, pack)
        for source in ("instagram", "facebook", "whatsapp", "tiktok"):
            self.assertIn(f"utm_source={source}", pack)

    def test_social_pack_continues_after_trial_and_uses_one_daily_deal(self):
        day = date(2026, 10, 20)
        product = deal_of_the_day(day)
        pack = daily_pack(self.settings, day)
        self.assertEqual(len(pack), 5)
        self.assertTrue(all(product.name in message for message in pack))

    def test_already_sent_social_pack_is_skipped_without_api_call(self):
        state = Path(self.temp.name) / "social-state.json"
        state.write_text('{"sent_dates":{"2026-09-12":{"messages":5}}}', encoding="utf-8")
        self.assertEqual(send_daily_pack(self.settings, date(2026, 9, 12), state), 0)

    def test_buffer_discovers_exact_owned_channels_without_exposing_key(self):
        def transport(query: str) -> dict:
            if "AccountOrganizations" in query:
                return {"data": {"account": {"organizations": [{"id": "org1", "name": "My organization"}]}}}
            return {"data": {"channels": [
                {"id": "ig1", "name": "aitoolgemspak", "displayName": "aitoolgemspak", "service": "instagram", "isQueuePaused": False},
                {"id": "fb1", "name": "AI Tool Gems Pakistan", "displayName": "AI Tool Gems Pakistan", "service": "facebook", "isQueuePaused": False},
                {"id": "tt1", "name": "aitoolgems", "displayName": "aitoolgems", "service": "tiktok", "isQueuePaused": False},
            ]}}

        result = connection_status(self.settings, BufferClient("private-key", transport))
        self.assertEqual(set(result["channels"]), {"instagram", "facebook", "tiktok"})
        self.assertNotIn("private-key", json.dumps(result))

    def test_buffer_publish_is_duplicate_safe_across_all_three_channels(self):
        class FakeClient:
            def __init__(self):
                self.calls = []

            def owned_channels(self):
                return {service: {"id": service + "-id"} for service in ("instagram", "facebook", "tiktok")}

            def create_image_post(self, channel_id, service, text, image_url, due_at, title):
                self.calls.append((service, "image", text, image_url, due_at, title))
                return {"id": service + "-post", "dueAt": due_at.isoformat()}

            def create_video_post(self, channel_id, service, text, video_url, due_at, title):
                self.calls.append((service, "video", text, video_url, due_at, title))
                return {"id": service + "-post", "dueAt": due_at.isoformat()}

        state = Path(self.temp.name) / "buffer-state.json"
        client = FakeClient()
        now = datetime(2026, 9, 12, 2, 0, tzinfo=timezone.utc)
        first = publish_daily_deal(self.settings, date(2026, 9, 12), state, client, now)
        second = publish_daily_deal(self.settings, date(2026, 9, 12), state, client, now)
        self.assertEqual(set(first["scheduled"]), {"instagram", "facebook", "tiktok"})
        self.assertEqual(set(second["skipped"]), {"instagram", "facebook", "tiktok"})
        self.assertEqual(len(client.calls), 3)
        self.assertTrue(all("Independent reseller" in call[2] for call in client.calls))

    def test_buffer_post_types_are_explicit_for_meta_channels(self):
        queries = []

        def transport(query: str) -> dict:
            queries.append(query)
            return {"data": {"createPost": {"post": {"id": "post1", "dueAt": "2026-09-12T04:00:00Z"}}}}

        client = BufferClient("private-key", transport)
        due_at = datetime(2026, 9, 12, 4, 0, tzinfo=timezone.utc)
        client.create_image_post("ig1", "instagram", "caption", "https://example.com/card.jpg", due_at, "Deal")
        client.create_image_post("fb1", "facebook", "caption", "https://example.com/card.jpg", due_at, "Deal")
        client.create_video_post("ig1", "instagram", "caption", "https://example.com/reel.mp4", due_at, "Deal")
        client.create_video_post("tt1", "tiktok", "caption", "https://example.com/video.mp4", due_at, "Deal")
        self.assertIn("instagram: { type: post, shouldShareToFeed: true }", queries[0])
        self.assertIn("facebook: { type: post }", queries[1])
        self.assertIn("instagram: { type: reel, shouldShareToFeed: true }", queries[2])
        self.assertIn("assets: [{ video:", queries[2])
        self.assertIn("tiktok: { isAiGenerated: false }", queries[3])

    def test_buffer_schedules_audience_windows_or_safely_in_future(self):
        early = datetime(2026, 9, 12, 2, 0, tzinfo=timezone.utc)
        late = datetime(2026, 9, 12, 17, 0, tzinfo=timezone.utc)
        self.assertEqual(scheduled_time(self.settings, date(2026, 9, 12), early, "facebook").hour, 14)
        self.assertEqual(scheduled_time(self.settings, date(2026, 9, 12), early, "instagram").hour, 14)
        self.assertEqual(scheduled_time(self.settings, date(2026, 9, 12), early, "instagram").minute, 30)
        self.assertEqual(scheduled_time(self.settings, date(2026, 9, 12), early, "tiktok").hour, 15)
        self.assertEqual(scheduled_time(self.settings, date(2026, 9, 12), late, "facebook"), late.replace(minute=10))
        self.assertEqual(scheduled_time(self.settings, date(2026, 9, 12), late, "tiktok"), late.replace(minute=18))

    def test_automatic_captions_have_platform_tracking(self):
        for service in ("instagram", "facebook", "tiktok"):
            caption = caption_for_platform(self.settings, date(2026, 9, 12), service)
            self.assertIn(f"utm_source={service}", caption)

    def test_captions_target_relevant_pakistan_audience_without_spam_tags(self):
        day = date(2026, 9, 12)
        audience = audience_for(deal_of_the_day(day), day)
        self.assertEqual(audience.id, "students")
        for service in ("instagram", "facebook", "tiktok"):
            caption = caption_for_platform(self.settings, day, service)
            self.assertIn("Pakistan", caption)
            self.assertIn("PRICE: Rs.", caption)
            self.assertIn("LISTED SAVING:", caption)
            self.assertNotIn("#fyp", caption.lower())
            self.assertNotIn("#viral", caption.lower())

    def test_social_learning_waits_for_evidence_then_uses_relevant_winner(self):
        product = deal_of_the_day(date(2026, 9, 12))
        state = {"published_dates": {}}
        for index, (audience, reactions, clicks) in enumerate((
            ("students", 2, 0), ("students", 3, 0),
            ("developers", 5, 4), ("developers", 6, 5),
            ("office", 1, 0), ("office", 2, 0),
        )):
            state["published_dates"][f"2026-10-{index + 1:02d}"] = {"instagram": {
                "audience": audience,
                "metrics": {"impressions": 100, "reactions": reactions, "clicks": clicks},
            }}
        winner, mode = learned_audience_for(product, date(2026, 9, 12), state)
        self.assertEqual(winner.id, "developers")
        self.assertEqual(mode, "metrics-winner")

    def test_buffer_performance_refresh_records_real_metrics_without_rescheduling(self):
        class MetricsClient:
            def post_metrics(self, post_id):
                return {
                    "id": post_id,
                    "status": "sent",
                    "metrics": [
                        {"type": "reactions", "name": "Reactions", "value": 7, "unit": "count"},
                        {"type": "comments", "name": "Comments", "value": 2, "unit": "count"},
                    ],
                    "metricsUpdatedAt": "2026-09-13T00:00:00Z",
                }

        state = Path(self.temp.name) / "buffer-state.json"
        state.write_text(json.dumps({"published_dates": {"2026-09-12": {
            "instagram": {
                "post_id": "ig-post",
                "scheduled_for": "2026-09-12T14:30:00+00:00",
                "audience": "students",
            }
        }}}), encoding="utf-8")
        result = refresh_performance(
            self.settings,
            state,
            MetricsClient(),
            datetime(2026, 9, 13, 2, 0, tzinfo=timezone.utc),
        )
        stored = json.loads(state.read_text(encoding="utf-8"))
        record = stored["published_dates"]["2026-09-12"]["instagram"]
        self.assertEqual(result["updated"], 1)
        self.assertEqual(record["delivery_status"], "sent")
        self.assertEqual(record["metrics"]["reactions"], 7)


if __name__ == "__main__":
    unittest.main()
