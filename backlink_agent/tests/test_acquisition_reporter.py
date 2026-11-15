"""Unit tests for WP15 Acquisition Performance Reporter."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from backlink_agent.lifecycle.models import LifecycleState
from backlink_agent.lifecycle.store import LocalSQLiteLifecycleStore
from backlink_agent.reporting import AcquisitionReporter


class TestAcquisitionReporter(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.tmp_dir / "reporter_lifecycle.db"
        self.reports_dir = self.tmp_dir / "reports"

        self.store = LocalSQLiteLifecycleStore(self.db_path)
        self.reporter = AcquisitionReporter(
            lifecycle_store=self.store,
            reports_dir=self.reports_dir,
        )

        # Seed test prospects in various lifecycle states
        for i in range(5):
            self.store.register_discovered_prospect(
                f"p_{i}", f"domain{i}.com", f"https://domain{i}.com/p", "https://aitoolgems.tech/", "dir"
            )

        # Advance some prospects
        with self.store._get_connection() as conn:
            conn.execute("UPDATE prospect_lifecycle SET current_state = 'owner_approved' WHERE prospect_id = 'p_1'")
            conn.execute("UPDATE prospect_lifecycle SET current_state = 'manually_submitted' WHERE prospect_id = 'p_2'")
            conn.execute("UPDATE prospect_lifecycle SET current_state = 'backlink_verified' WHERE prospect_id = 'p_3'")
            conn.execute("UPDATE prospect_lifecycle SET current_state = 'retained' WHERE prospect_id = 'p_4'")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_generate_acquisition_report_schema_and_metrics(self):
        report = self.reporter.generate_acquisition_report()

        self.assertIn("generated_at", report)
        self.assertIn("funnel_metrics", report)
        self.assertIn("conversion_rates", report)

        # Invariant: Discovered prospects are NOT backlinks!
        # Only p_3 (backlink_verified) and p_4 (retained) count as actual backlinks
        self.assertEqual(report["actual_earned_backlinks_count"], 2)

        files = report["report_files"]
        md_path = Path(files["markdown"])
        json_path = Path(files["json"])

        self.assertTrue(md_path.exists())
        self.assertTrue(json_path.exists())

        md_content = md_path.read_text(encoding="utf-8")
        self.assertIn("HERMES Backlink Acquisition & Outcome Intelligence Report", md_content)
        self.assertIn("**Actual Verified Earned Backlinks:** **`2`**", md_content)

        data = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(data["actual_earned_backlinks_count"], 2)
        self.assertEqual(data["funnel_metrics"]["retained_clean"], 1)


if __name__ == "__main__":
    unittest.main()
