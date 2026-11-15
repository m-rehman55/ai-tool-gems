"""Unit tests for WP21 Autonomous Enterprise Hardening & Zero-Noise Architecture."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from backlink_agent.advanced_verifier.models import DetailedVerificationResult, LinkQualification
from backlink_agent.advanced_verifier.verifier import AdvancedBacklinkVerifier
from backlink_agent.execution.browser_adapter import DirectoryBrowserAdapter
from backlink_agent.execution.devto_adapter import DevtoAPIAdapter
from backlink_agent.execution.email_adapter import EmailPitchAdapter
from backlink_agent.execution.github_adapter import GitHubPRAdapter
from backlink_agent.execution.models import ExecutionResult, ExecutionStatus
from backlink_agent.prospect_repository import ProspectRepository
from backlink_agent.retention.models import RetentionSnapshot, RetentionStatus
from backlink_agent.retention.monitor import RetentionMonitor


class TestWP21Hardening(unittest.TestCase):

    def setUp(self):
        self.repository = ProspectRepository()

    # -------------------------------------------------------------------------
    # 1. Three-URL Data Model Tests
    # -------------------------------------------------------------------------
    def test_three_url_data_model_defaults_and_effective_url(self):
        res = ExecutionResult(
            prospect_domain="example.com",
            adapter_name="test_adapter",
            status=ExecutionStatus.SUCCESS,
            submission_url="https://example.com/submit",
            submission_evidence_url="https://example.com/receipt/123",
            canonical_placement_url="https://example.com/p/ai-tool-gems",
        )
        self.assertEqual(res.submission_url, "https://example.com/submit")
        self.assertEqual(res.submission_evidence_url, "https://example.com/receipt/123")
        self.assertEqual(res.canonical_placement_url, "https://example.com/p/ai-tool-gems")
        self.assertEqual(res.get_effective_evidence_url(), "https://example.com/receipt/123")

    def test_github_adapter_populates_three_urls(self):
        adapter = GitHubPRAdapter()
        prospect = self.repository.resolve("github.com")
        self.assertIsNotNone(prospect)

        res = adapter.execute(prospect, dry_run=True)
        self.assertIsNotNone(res.submission_url)
        self.assertIsNotNone(res.submission_evidence_url)
        self.assertIsNotNone(res.canonical_placement_url)
        self.assertIn("github.com", res.submission_url)
        self.assertIn("pull", res.submission_evidence_url)
        self.assertIn("README.md", res.canonical_placement_url)

    def test_devto_adapter_populates_three_urls(self):
        adapter = DevtoAPIAdapter()
        prospect = self.repository.resolve("dev.to")
        self.assertIsNotNone(prospect)

        res = adapter.execute(prospect, dry_run=True)
        self.assertEqual(res.submission_url, "https://dev.to/new")
        self.assertIn("dev.to", res.submission_evidence_url)
        self.assertIn("dev.to", res.canonical_placement_url)

    def test_directory_and_email_adapters_populate_three_urls(self):
        browser_adapter = DirectoryBrowserAdapter()
        saas_p = self.repository.resolve("saashub.com")
        res_saas = browser_adapter.execute(saas_p, dry_run=True)
        self.assertIn("submit", res_saas.submission_url)
        self.assertIn("added", res_saas.submission_evidence_url)
        self.assertIn("ai-tool-gems", res_saas.canonical_placement_url)

        email_adapter = EmailPitchAdapter()
        tech_p = self.repository.resolve("techjuice.pk")
        res_tech = email_adapter.execute(tech_p, dry_run=True)
        self.assertIn("contact", res_tech.submission_url)
        self.assertIn("editors@techjuice.pk", res_tech.submission_evidence_url)
        self.assertIn("techjuice.pk", res_tech.canonical_placement_url)

    # -------------------------------------------------------------------------
    # 2. WAF & Bot Protection Classification Tests
    # -------------------------------------------------------------------------
    def test_waf_blocked_classification_on_http_403(self):
        verifier = AdvancedBacklinkVerifier()
        mock_http_err = urllib.error.HTTPError(
            url="https://medium.com/@user/story",
            code=403,
            msg="Forbidden / Cloudflare Challenge",
            hdrs={},
            fp=None,
        )

        with patch("urllib.request.OpenerDirector.open", side_effect=mock_http_err):
            with patch("backlink_agent.advanced_verifier.verifier.validate_and_sanitize_url", return_value=("https://medium.com/@user/story", [("104.16.1.1", 443)])):
                res = verifier.verify_url(
                    source_page_url="https://medium.com/@user/story",
                    target_asset_url="https://aitoolgems.tech/",
                )

        self.assertEqual(res.http_status, 403)
        self.assertEqual(res.qualification, LinkQualification.BLOCKED_WAF)
        self.assertFalse(res.is_live_backlink)
        self.assertNotEqual(res.qualification, LinkQualification.ANCHOR_MISSING)

    def test_retention_monitor_preserves_status_on_blocked_waf(self):
        monitor = RetentionMonitor()
        prev_snapshot = RetentionSnapshot(
            prospect_id="medium.com",
            verification_date="2026-11-01T00:00:00Z",
            days_since_first_verified=14,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            anchor_text="AI Tool Gems",
            target_destination="https://aitoolgems.tech/",
            content_hash="abc123hash",
            status_detected=RetentionStatus.RETAINED,
            consecutive_failures=0,
        )

        waf_result = DetailedVerificationResult(
            prospect_id="medium.com",
            source_page_url="https://medium.com/@user/story",
            target_asset_url="https://aitoolgems.tech/",
            http_status=403,
            final_page_url="https://medium.com/@user/story",
            qualification=LinkQualification.BLOCKED_WAF,
            is_live_backlink=False,
            error_message="WAF / Bot Protection Active (HTTP 403)",
        )

        new_snapshot = monitor.evaluate_retention(
            current_result=waf_result,
            days_active=15,
            previous_snapshot=prev_snapshot,
        )

        # Status must be inconclusive access restricted, NOT link removed
        self.assertEqual(new_snapshot.status_detected, RetentionStatus.INCONCLUSIVE_ACCESS_RESTRICTED)
        self.assertEqual(new_snapshot.consecutive_failures, 0)
        self.assertEqual(new_snapshot.anchor_text, "AI Tool Gems")


if __name__ == "__main__":
    unittest.main()
