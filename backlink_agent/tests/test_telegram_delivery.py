"""Unit tests for Telegram Delivery Outbox, Card Formatter, and Daily Digest."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from backlink_agent.evidence_scoring.models import ScoreBreakdown, ScoredOpportunity
from backlink_agent.submission_drafter.models import (
    DirectorySubmissionDraft,
    GitHubAwesomePRDraft,
    PublicationPitchDraft,
)
from backlink_agent.telegram_delivery import (
    DailyTelegramReporter,
    OpportunityCardFormatter,
    OutboxMessage,
    TelegramOutboxManager,
)


class TestTelegramDelivery(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.outbox_dir = self.tmp_dir / "outbox"

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_outbox_message_lifecycle_and_serialization(self):
        msg = OutboxMessage(chat_id="12345", text="Test message", prospect_domain="dev.to")
        self.assertEqual(msg.status, "pending")
        self.assertEqual(msg.retry_count, 0)

        # Mark delivered
        msg.mark_delivered()
        self.assertEqual(msg.status, "delivered")
        self.assertIsNotNone(msg.delivered_at)

        # Serialization roundtrip
        d = msg.to_dict()
        restored = OutboxMessage.from_dict(d)
        self.assertEqual(restored.message_id, msg.message_id)
        self.assertEqual(restored.status, "delivered")
        self.assertEqual(restored.prospect_domain, "dev.to")

        # Retry failure logic
        msg2 = OutboxMessage(chat_id="12345", text="Fail test", max_retries=2)
        msg2.mark_retry_pending("Network timeout")
        self.assertEqual(msg2.status, "retry_pending")
        self.assertEqual(msg2.retry_count, 1)

        msg2.mark_retry_pending("Second timeout")
        self.assertEqual(msg2.status, "failed")
        self.assertEqual(msg2.retry_count, 2)

    def test_opportunity_card_formatter_directory(self):
        breakdown = ScoreBreakdown(22, 22, 20, 15, 15)
        opp = ScoredOpportunity(
            prospect_id="p_dir",
            prospect_domain="saashub.com",
            source_page_url="https://saashub.com/submit",
            prospect_type="directory_class1",
            target_asset_url="https://aitoolgems.tech/",
            score=breakdown,
            rationale=["Verified editorial review process"],
        )
        draft = DirectorySubmissionDraft(
            draft_id="d_01",
            prospect_id="p_dir",
            short_tagline="AI Tools Directory",
            category="AI & Developer Tools",
        )
        card = OpportunityCardFormatter.format_card(opp, draft, draft_hash="abc12345def67890")

        self.assertIn("🎯 *New Backlink Opportunity: saashub.com*", card)
        self.assertIn("Score: 94/100", card)
        self.assertIn("Relevance: `22/25`", card)
        self.assertIn("Draft Hash: `abc12345def67890`", card)
        self.assertIn("`/approve saashub.com abc12345def67890`", card)

    def test_opportunity_card_formatter_github(self):
        breakdown = ScoreBreakdown(20, 25, 18, 15, 15)
        opp = ScoredOpportunity(
            prospect_id="p_gh",
            prospect_domain="github.com",
            source_page_url="https://github.com/eudk/awesome-ai-tools",
            prospect_type="github_awesome",
            target_asset_url="https://aitoolgems.tech/",
            score=breakdown,
        )
        draft = GitHubAwesomePRDraft(
            draft_id="d_02",
            prospect_id="p_gh",
            repository_name="eudk/awesome-ai-tools",
            pr_title="Add AI Tool Gems",
            proposed_markdown_entry="- [AI Tool Gems](https://aitoolgems.tech/)",
        )
        card = OpportunityCardFormatter.format_card(opp, draft)
        self.assertIn("🐙 GitHub Awesome", card)
        self.assertIn("eudk/awesome-ai-tools", card)
        self.assertIn("`/approve github.com", card)

    def test_daily_reporter_summary(self):
        breakdown_high = ScoreBreakdown(22, 22, 20, 15, 15)
        breakdown_low = ScoreBreakdown(10, 10, 5, 0, 5)
        opp_high = ScoredOpportunity(
            prospect_id="p1",
            prospect_domain="saashub.com",
            source_page_url="https://saashub.com",
            prospect_type="directory_class1",
            target_asset_url="https://aitoolgems.tech/",
            score=breakdown_high,
        )
        opp_low = ScoredOpportunity(
            prospect_id="p2",
            prospect_domain="spam.net",
            source_page_url="https://spam.net",
            prospect_type="directory_class3",
            target_asset_url="https://aitoolgems.tech/",
            score=breakdown_low,
        )
        draft = DirectorySubmissionDraft(draft_id="d1", prospect_id="p1")

        summary = DailyTelegramReporter.format_daily_summary(
            total_discovered=10,
            scored_opportunities=[opp_high, opp_low],
            drafts_generated=[draft],
            live_backlinks_count=4,
        )

        self.assertIn("AI Tool Gems Backlink Intelligence Daily Digest", summary)
        self.assertIn("Confirmed Live Placements: `4`", summary)
        self.assertIn("Newly Discovered Prospects: `10`", summary)
        self.assertIn("High Priority (Score >= 75): `1`", summary)
        self.assertIn("Quarantined / Spam (< 55): `1`", summary)

    def test_outbox_manager_lifecycle(self):
        db_file = self.tmp_dir / "test_outbox.db"
        manager = TelegramOutboxManager(
            bot_token="fake_bot_token",
            chat_id="123456789",
            db_path=db_file,
            dry_run=True,
        )

        messages = manager.enqueue(
            text="Short alert message",
            message_type="alert",
            prospect_domain="saashub.com",
        )
        self.assertEqual(len(messages), 1)

        pending = manager.list_pending()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].text, "Short alert message")

        # Flush outbox in dry-run mode
        result = manager.flush_outbox()
        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["dry_run_simulated"], 1)
        self.assertEqual(result["sent"], 1)
        self.assertEqual(result["failed"], 0)

        # Check pending is empty and store has 1 message in dry_run_simulated state
        self.assertEqual(len(manager.list_pending()), 0)
        counts = manager.store.get_status_counts()
        self.assertEqual(counts["dry_run_simulated"], 1)
        self.assertEqual(counts["pending"], 0)

    def test_opportunity_card_formatter_markdown_safety(self):
        """WP17: Card formatter must not produce unclosed brackets or raw underscore triggers."""
        breakdown = ScoreBreakdown(22, 22, 20, 15, 15)
        opp = ScoredOpportunity(
            prospect_id="p_dir",
            prospect_domain="startups.pasha.org.pk",
            source_page_url="https://startups.pasha.org.pk/",
            prospect_type="directory_class3",
            target_asset_url="https://aitoolgems.tech/",
            score=breakdown,
            rationale=["Verified editorial review on submissions_and_listings"],
            risk_factors=["Minor_delay_in_review"],
        )
        draft = DirectorySubmissionDraft(
            draft_id="d_01",
            prospect_id="p_dir",
            short_tagline="AI Tools Directory for Pakistan with flat PKR pricing",
            category="AI & Developer Tools",
        )
        card = OpportunityCardFormatter.format_card(opp, draft, draft_hash="abc12345def67890")

        # Check that [Curated Directory] or [GitHub Awesome] link-syntax brackets are absent
        self.assertNotIn("[Curated Directory]", card)
        self.assertIn("📁 Curated Directory", card)
        # Check tier display is safe and has no raw underscore trigger outside backticks
        self.assertIn("`HIGH PRIORITY`", card)
        self.assertNotIn("(HIGH_PRIORITY)", card)
        # Rationale with underscore sanitized
        self.assertIn("submissions and listings", card)
        self.assertIn("Minor delay in review", card)

    def test_dispatch_message_auto_healing_fallback_on_400(self):
        """WP17: When Telegram returns HTTP 400 Bad Request entity error, fallback sends as plain text."""
        import io
        import urllib.error
        from unittest.mock import patch, MagicMock

        db_file = self.tmp_dir / "fallback_outbox.db"
        manager = TelegramOutboxManager(
            bot_token="test_bot_token",
            chat_id="123456789",
            db_path=db_file,
            dry_run=False,
        )
        msg = OutboxMessage(chat_id="123456789", text="Card with bad markdown formatting")
        manager.store.enqueue(msg)

        # Mock first call: HTTPError 400 Bad Request can't parse entities
        err_fp = io.BytesIO(b'{"ok":false,"error_code":400,"description":"Bad Request: can\'t parse entities"}')
        http_error = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=err_fp,
        )

        # Mock second call: successful HTTP 200 response
        mock_success_resp = MagicMock()
        mock_success_resp.status = 200
        mock_success_resp.read.return_value = b'{"ok":true,"result":{"message_id":998877}}'
        mock_success_resp.__enter__.return_value = mock_success_resp

        with patch("urllib.request.urlopen", side_effect=[http_error, mock_success_resp]):
            success = manager.dispatch_message(msg)

        self.assertTrue(success)
        self.assertEqual(msg.status, "accepted_by_telegram")
        self.assertEqual(msg.telegram_message_id, 998877)


if __name__ == "__main__":
    unittest.main()
