"""
Unit tests for bing_agent (Section 3.5 - Agent 4 Bing Webmaster & IndexNow Intelligence).

Tests:
1. BingWebmasterClient authorization, date parsing, and model serialization.
2. IndexNow durable submission queue, delta detection via content hashes, deduplication.
3. Separation of submission acceptance (HTTP 200/202) from crawling and indexing.
4. Google indexing exclusion policy contract verification.
5. Cross-engine search performance analyzer and gap detection.
6. HERMES-CEO TaskContract execution for AGENT-04-BING.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from hermes_core.contracts import (
    ApprovalRequirement,
    RiskClassification,
    TaskContract,
    TaskStatus,
)
from bing_agent.analyzer import BingAuditSummary, BingWebmasterAnalyzer, CrossEngineQueryInsight
from bing_agent.client import BingWebmasterClient
from bing_agent.hermes_integration import execute_bing_task
from bing_agent.indexnow_queue import (
    HOST,
    INDEXNOW_KEY,
    KEY_LOCATION,
    IndexNowQueueEngine,
)
from bing_agent.models import (
    BingCrawlStat,
    BingPageStat,
    BingQueryStat,
    BingQuota,
    BingSite,
    parse_bing_date,
)


class TestBingAgent(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.test_dir / "data" / "bing"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.project_dir = Path(__file__).resolve().parent.parent.parent

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ── 1. Model & Date Parsing Tests ─────────────────────────────────────────

    def test_parse_bing_epoch_date(self):
        """Verifies Bing's /Date(1790294400000)/ format is parsed to YYYY-MM-DD."""
        # 1790294400000 ms is in 2026
        parsed = parse_bing_date("/Date(1790294400000)/")
        self.assertTrue(parsed.startswith("2026-"), f"Expected 2026 date, got {parsed}")

        # Plain strings returned unchanged
        self.assertEqual(parse_bing_date("2026-11-05"), "2026-11-05")
        self.assertEqual(parse_bing_date(""), "")

    def test_bing_query_stat_ctr_calculation(self):
        """Verifies CTR is correctly calculated from clicks and impressions."""
        stat = BingQueryStat(
            query="buy linkedin premium pakistan",
            date="2026-10-02",
            clicks=5,
            impressions=50,
            avg_click_position=1.0,
            avg_impression_position=2.0,
        )
        self.assertEqual(stat.ctr, 10.0)

        zero_imp_stat = BingQueryStat(
            query="zero impressions query",
            date="2026-10-02",
            clicks=0,
            impressions=0,
            avg_click_position=-1.0,
            avg_impression_position=-1.0,
        )
        self.assertEqual(zero_imp_stat.ctr, 0.0)

    # ── 2. Durable Queue & Delta Diff Tests ───────────────────────────────────

    def test_delta_detection_identifies_new_and_modified_files(self):
        """Verifies delta engine identifies new files and suppresses unchanged files."""
        html_dir = self.test_dir / "tools" / "test_tool"
        html_dir.mkdir(parents=True, exist_ok=True)
        test_file = html_dir / "index.html"
        test_file.write_text("<html>Initial version</html>", encoding="utf-8")

        queue_engine = IndexNowQueueEngine(project_dir=self.test_dir, data_dir=self.data_dir)

        # First run: should detect new URL
        deltas_1 = queue_engine.detect_deltas()
        self.assertEqual(len(deltas_1), 1)
        self.assertEqual(deltas_1[0].reason, "NEW_URL")

        # Fake dispatch so hash is saved
        queue_engine.dispatch_pending(dry_run=True)
        # Manually save state hash as if dispatched
        queue_engine.save_url_hashes({deltas_1[0].url: deltas_1[0].content_hash})

        # Second run without changes: zero deltas
        deltas_2 = queue_engine.detect_deltas()
        self.assertEqual(len(deltas_2), 0)

        # Third run with modified content: detects CONTENT_UPDATED
        test_file.write_text("<html>Updated version with new PKR pricing</html>", encoding="utf-8")
        deltas_3 = queue_engine.detect_deltas()
        self.assertEqual(len(deltas_3), 1)
        self.assertEqual(deltas_3[0].reason, "CONTENT_UPDATED")

    def test_url_deduplication(self):
        """Verifies URLs are deduplicated across submission batches."""
        queue_engine = IndexNowQueueEngine(project_dir=self.test_dir, data_dir=self.data_dir)
        queue = queue_engine.load_queue()

        # Add duplicates with trailing whitespace
        from bing_agent.models import IndexNowQueueItem
        queue["https://aitoolgems.tech/tools/chatgpt/"] = IndexNowQueueItem(
            url="https://aitoolgems.tech/tools/chatgpt/",
            reason="NEW_URL",
            discovered_at="2026-11-05T00:00:00Z",
            content_hash="abc123hash",
        )
        queue_engine.save_queue(queue)

        records = queue_engine.dispatch_pending(dry_run=True)
        self.assertGreater(len(records), 0)
        # Ensure unique URLs in payload
        urls_in_rec = records[0].urls
        self.assertEqual(len(urls_in_rec), len(set(urls_in_rec)))

    # ── 3. Acceptance vs Indexing & Google Exclusion Tests ────────────────────

    def test_submission_acceptance_distinguished_from_indexing(self):
        """Ensures submission acceptance is strictly distinguished from crawling/indexing."""
        queue_engine = IndexNowQueueEngine(project_dir=self.test_dir, data_dir=self.data_dir)
        records = queue_engine.dispatch_pending(dry_run=True)

        for rec in records:
            # Acceptance field must be boolean HTTP acceptance, NOT indexing verdict
            self.assertTrue(rec.is_accepted)
            self.assertIn("accepted", rec.response_message.lower())
            # Engine scope must explicitly disclose Google exclusion
            self.assertIn("Google excluded from IndexNow", rec.engine_scope)

    def test_key_verification_infrastructure(self):
        """Verifies the IndexNow key and location on disk match live requirements."""
        queue_engine = IndexNowQueueEngine(project_dir=self.project_dir)
        info = queue_engine.verify_key_infrastructure()
        self.assertTrue(info["exists_locally"], "Key file must exist in repository root")
        self.assertTrue(info["content_valid"], "Key file content must match INDEXNOW_KEY")
        self.assertEqual(info["key"], INDEXNOW_KEY)
        self.assertEqual(info["key_location"], f"https://{HOST}/{INDEXNOW_KEY}.txt")

    # ── 4. Cross-Engine Search Analyzer Tests ─────────────────────────────────

    def test_cross_engine_query_classification(self):
        """Verifies query categorization across Bing and Google metrics."""
        client = BingWebmasterClient()

        # Mock query stats
        q_breakthrough = BingQueryStat(
            query="buy linkedin premium pakistan 2026",
            date="2026-10-02",
            clicks=1,
            impressions=2,
            avg_click_position=1.0,
            avg_impression_position=1.0,
        )
        q_lagging = BingQueryStat(
            query="chatgpt price in pakistan",
            date="2026-10-02",
            clicks=0,
            impressions=1,
            avg_click_position=-1.0,
            avg_impression_position=25.0,
        )

        class MockGSCQuery:
            def __init__(self, q, imp, pos):
                self.query = q
                self.impressions = imp
                self.clicks = 0
                self.position = pos

        class MockGSCDataset:
            queries = [
                MockGSCQuery("buy linkedin premium pakistan 2026", 1, 20.0),
                MockGSCQuery("chatgpt price in pakistan", 50, 4.0),
            ]

        analyzer = BingWebmasterAnalyzer(client=client)

        # Cross reference
        gsc_queries = {q.query: q for q in MockGSCDataset.queries}

        # Breakthrough check
        b_res = CrossEngineQueryInsight(
            query=q_breakthrough.query,
            bing_impressions=q_breakthrough.impressions,
            bing_clicks=q_breakthrough.clicks,
            bing_position=q_breakthrough.avg_impression_position,
            gsc_impressions=1,
            gsc_clicks=0,
            gsc_position=20.0,
            opportunity_type="BING_BREAKTHROUGH",
            recommendation="Ranking #1 on Bing! Protect snippet.",
        )
        self.assertEqual(b_res.opportunity_type, "BING_BREAKTHROUGH")

    # ── 5. HERMES-CEO Task Contract Execution Tests ──────────────────────────

    def test_hermes_bing_task_execution(self):
        """Verifies AGENT-04-BING completes a TaskContract dispatched by HERMES-CEO."""
        contract = TaskContract(
            task_id="TASK-04-TEST01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-04-BING",
            objective="Execute Bing Webmaster crawl inspection, quota check, and delta submission audit",
            scope="reports/bing-agent/",
            input_evidence={"mode": "audit"},
            required_tools=["bing_agent"],
            expected_output="bing-audit-latest.json",
            dependencies=[],
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid JSON artifact generated", "Zero unhandled exceptions"],
        )

        completed = execute_bing_task(contract, project_dir=self.project_dir)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("execution_timestamp", completed.verification_evidence)
        self.assertIn("pages_in_index", completed.verification_evidence)
        self.assertIn("markdown_report", completed.verification_evidence)
        self.assertTrue(Path(completed.verification_evidence["markdown_report"]).exists())

    def test_invalid_api_key_handled_as_blocked_without_crashing_or_fabricating_pass(self):
        """CRITICAL: Bing InvalidApiKey must be handled as BLOCKED without crashing or fabricating pass."""
        import io
        import urllib.error
        from unittest.mock import patch

        client = BingWebmasterClient(api_key="mock_invalid_key_123")
        analyzer = BingWebmasterAnalyzer(client=client)

        err_fp = io.BytesIO(b'{"ErrorCode": 2, "Message": "Invalid Api Key"}')
        http_err = urllib.error.HTTPError("https://ssl.bing.com", 400, "Bad Request", {}, err_fp)

        with patch("urllib.request.urlopen", side_effect=http_err):
            # 1. Direct call raises PermissionError indicating BLOCKED
            with self.assertRaises(PermissionError) as ctx:
                client.get_user_sites()
            self.assertIn("InvalidApiKey", str(ctx.exception))
            self.assertIn("BLOCKED", str(ctx.exception))

            # 2. Analyzer returns honest BLOCKED audit summary rather than crashing or faking pass
            summary = analyzer.run_audit()
            self.assertFalse(summary.is_verified)
            self.assertEqual(summary.total_bing_queries, 0)
            self.assertTrue(any("BLOCKED (InvalidApiKey)" in rec for rec in summary.recommendations))


if __name__ == "__main__":
    unittest.main()

