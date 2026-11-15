"""Comprehensive Acceptance Test Suite for WP14 Operations, Reliability & Observability."""

from datetime import datetime, timezone, timedelta
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from backlink_agent.evidence_scoring.models import ScoreBreakdown, ScoredOpportunity
from backlink_agent.pipeline import BacklinkIntelligencePipeline
from backlink_agent.prospect_discovery.competitor_gap_discovery import CompetitorGapDiscoverer
from backlink_agent.submission_drafter import SubmissionDraftingEngine
from backlink_agent.telegram_delivery import (
    DailyTelegramReporter,
    OpportunityCardFormatter,
    OutboxMessage,
    TelegramOutboxManager,
    LocalSQLiteOutboxStore,
)


class TestWP14Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.tmp_dir / "wp14_outbox.db"
        self.reports_dir = self.tmp_dir / "reports"
        self.store = LocalSQLiteOutboxStore(self.db_path)
        self.outbox_manager = TelegramOutboxManager(
            bot_token="test_bot_token",
            chat_id="987654321",
            store=self.store,
            dry_run=True,
        )
        self.pipeline = BacklinkIntelligencePipeline(
            outbox_manager=self.outbox_manager,
            reports_dir=self.reports_dir,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_wp14_tld_false_positive_avoidance(self):
        """WP14-A: Legitimate .shop/.site domains must not be blanket-rejected as PBNs."""
        gap = CompetitorGapDiscoverer()

        # Legitimate domains on modern gTLDs
        self.assertFalse(gap.is_toxic_pbn("creativetools.shop"))
        self.assertFalse(gap.is_toxic_pbn("ai-portfolio.site"))
        self.assertFalse(gap.is_toxic_pbn("developer-community.site"))

        # Confirmed spam / PBN blast footprints
        self.assertTrue(gap.is_toxic_pbn("searchwins.shop"))
        self.assertTrue(gap.is_toxic_pbn("solidlinkpro.shop"))
        self.assertTrue(gap.is_toxic_pbn("serpvilo.shop"))
        self.assertTrue(gap.is_toxic_pbn("spammy-directory.site"))
        self.assertTrue(gap.is_toxic_pbn("seo-pbn-blast.xyz"))

    def test_wp14_draft_eligibility_gating(self):
        """WP14-A: Only prospects with score >= 75 and high_priority tier can be drafted."""
        drafter = SubmissionDraftingEngine()

        # High priority prospect (score 85) -> draft allowed
        opp_high = ScoredOpportunity(
            prospect_id="p_high",
            prospect_domain="saashub.com",
            source_page_url="https://saashub.com/submit",
            prospect_type="directory_class1",
            target_asset_url="https://aitoolgems.tech/",
            score=ScoreBreakdown(22, 22, 18, 11, 12),  # Total: 85
            action_recommendation="draft_ready",
        )
        res_high = drafter.draft_for_opportunity(opp_high)
        self.assertIsNotNone(res_high)
        draft, d_hash = res_high
        self.assertEqual(len(d_hash), 16)

        # Investigate tier prospect (score 65) -> drafting suppressed
        opp_investigate = ScoredOpportunity(
            prospect_id="p_mid",
            prospect_domain="average-dir.com",
            source_page_url="https://average-dir.com/submit",
            prospect_type="directory_class2",
            target_asset_url="https://aitoolgems.tech/",
            score=ScoreBreakdown(15, 15, 15, 10, 10),  # Total: 65
            action_recommendation="investigate",
        )
        self.assertIsNone(drafter.draft_for_opportunity(opp_investigate))

        # Quarantine tier prospect (score 40) -> drafting strictly suppressed
        opp_quarantine = ScoredOpportunity(
            prospect_id="p_low",
            prospect_domain="spammy-links.com",
            source_page_url="https://spammy-links.com/add",
            prospect_type="directory_class3",
            target_asset_url="https://aitoolgems.tech/",
            score=ScoreBreakdown(10, 10, 10, 5, 5),  # Total: 40
            action_recommendation="quarantine",
        )
        self.assertIsNone(drafter.draft_for_opportunity(opp_quarantine))

    def test_wp14_dry_run_isolation_and_semantics(self):
        """WP14-B: Dry-run mode transitions messages to dry_run_simulated with zero external HTTP calls."""
        messages = self.outbox_manager.enqueue(
            text="Simulated test message",
            message_type="alert",
            prospect_domain="saashub.com",
        )
        self.assertEqual(len(messages), 1)
        msg_id = messages[0].message_id

        # Flush in dry-run mode
        flush_res = self.outbox_manager.flush_outbox()
        self.assertEqual(flush_res["dry_run_simulated"], 1)
        self.assertEqual(flush_res["sent"], 1)
        self.assertEqual(flush_res["failed"], 0)

        stored = self.store.get(msg_id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.status, "dry_run_simulated")
        self.assertIsNotNone(stored.delivered_at)

    def test_wp14_outbox_persistence_across_instances(self):
        """WP14-B: Messages enqueued in instance A survive restart and can be claimed by instance B."""
        # Instance A enqueues
        msg = OutboxMessage(chat_id="987654321", text="Persistent message", prospect_domain="dev.to")
        self.store.enqueue(msg)

        # Instance B opens database independently
        store_b = LocalSQLiteOutboxStore(self.db_path)
        manager_b = TelegramOutboxManager(
            bot_token="test_token",
            chat_id="987654321",
            store=store_b,
            dry_run=True,
        )

        pending = manager_b.list_pending()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].message_id, msg.message_id)

        # Instance B flushes successfully
        flush_res = manager_b.flush_outbox()
        self.assertEqual(flush_res["dry_run_simulated"], 1)

    def test_wp14_concurrent_worker_disjoint_leases(self):
        """WP14-B: Multiple workers claiming pending messages receive disjoint sets."""
        for i in range(10):
            self.store.enqueue(OutboxMessage(chat_id="987654321", text=f"Item {i}"))

        claimed_w1 = self.store.claim_pending_messages(worker_id="worker_alpha", limit=6)
        claimed_w2 = self.store.claim_pending_messages(worker_id="worker_beta", limit=6)

        self.assertEqual(len(claimed_w1), 6)
        self.assertEqual(len(claimed_w2), 4)

        set1 = {m.message_id for m in claimed_w1}
        set2 = {m.message_id for m in claimed_w2}
        self.assertTrue(set1.isdisjoint(set2))

    def test_wp14_stale_lease_recovery(self):
        """WP14-B: Crashed worker leases (> 300s) are automatically recovered to retry_pending."""
        msg = OutboxMessage(chat_id="987654321", text="Stale lease message")
        self.store.enqueue(msg)

        claimed = self.store.claim_pending_messages(worker_id="crashed_worker", limit=1)
        self.assertEqual(len(claimed), 1)

        # Artificially age the lease by 400 seconds
        past_time = (datetime.now(timezone.utc) - timedelta(seconds=400)).isoformat()
        with self.store._get_connection() as conn:
            conn.execute(
                "UPDATE outbox_messages SET locked_at = ? WHERE message_id = ?",
                (past_time, msg.message_id),
            )

        # Recover stale leases
        recovered = self.store.recover_stale_leases(lease_timeout_seconds=300)
        self.assertEqual(recovered, 1)

        updated = self.store.get(msg.message_id)
        self.assertEqual(updated.status, "retry_pending")
        self.assertEqual(updated.retry_count, 1)

    def test_wp14_full_pipeline_artifacts_generation(self):
        """WP14-E & F: Full pipeline generates valid markdown and JSON reports matching schema."""
        summary = self.pipeline.run_daily_intelligence(
            dispatch_telegram=True,
            export_reports=True,
        )

        self.assertGreater(summary["discovered_count"], 0)
        self.assertGreater(summary["drafts_generated_count"], 0)
        self.assertEqual(summary["outbox_flush"]["failed"], 0)

        rep_files = summary["report_files"]
        json_file = Path(rep_files["json"])
        md_file = Path(rep_files["markdown"])

        self.assertTrue(json_file.exists())
        self.assertTrue(md_file.exists())

        # Verify JSON report schema
        data = json.loads(json_file.read_text(encoding="utf-8"))
        self.assertIn("timestamp", data)
        self.assertIn("total_discovered", data)
        self.assertIn("opportunities", data)
        self.assertIn("drafts", data)
        self.assertIn("outbox", data)

        # Verify Markdown report content
        md_content = md_file.read_text(encoding="utf-8")
        self.assertIn("Autonomous Backlink Intelligence Daily Report", md_content)
        self.assertIn("High-Priority Draft Packages Generated", md_content)


if __name__ == "__main__":
    unittest.main()
