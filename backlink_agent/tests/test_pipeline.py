"""Unit tests for Autonomous Backlink Intelligence Pipeline."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from backlink_agent.pipeline import BacklinkIntelligencePipeline
from backlink_agent.telegram_delivery import TelegramOutboxManager


class TestBacklinkPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.outbox_dir = self.tmp_dir / "outbox"
        self.reports_dir = self.tmp_dir / "reports"

        self.outbox = TelegramOutboxManager(
            bot_token="test_token",
            chat_id="123456",
            outbox_dir=self.outbox_dir,
            dry_run=True,
        )
        self.pipeline = BacklinkIntelligencePipeline(
            outbox_manager=self.outbox,
            reports_dir=self.reports_dir,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_run_daily_intelligence_end_to_end(self):
        summary = self.pipeline.run_daily_intelligence(
            dispatch_telegram=True,
            export_reports=True,
        )

        self.assertIn("run_at", summary)
        self.assertGreater(summary["discovered_count"], 0)
        self.assertGreater(summary["scored_count"], 0)
        self.assertGreater(summary["drafts_generated_count"], 0)

        # Check tiers breakdown
        tiers = summary["tiers"]
        self.assertIn("high_priority", tiers)
        self.assertIn("investigate", tiers)
        self.assertIn("quarantine", tiers)

        # Check outbox flush in dry-run
        flush = summary["outbox_flush"]
        self.assertGreaterEqual(flush["sent"], 1)
        self.assertEqual(flush["failed"], 0)

        # Check exported reports exist
        rep_files = summary["report_files"]
        md_file = Path(rep_files["markdown"])
        json_file = Path(rep_files["json"])

        self.assertTrue(md_file.exists())
        self.assertTrue(json_file.exists())

        md_content = md_file.read_text(encoding="utf-8")
        self.assertIn("AI Tool Gems Autonomous Backlink Intelligence Daily Report", md_content)
        self.assertIn("High-Priority Draft Packages Generated", md_content)

        json_data = json.loads(json_file.read_text(encoding="utf-8"))
        self.assertEqual(json_data["total_discovered"], summary["discovered_count"])
        self.assertGreater(len(json_data["opportunities"]), 0)
        self.assertGreater(len(json_data["drafts"]), 0)


if __name__ == "__main__":
    unittest.main()
