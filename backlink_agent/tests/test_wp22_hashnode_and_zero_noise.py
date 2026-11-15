"""Unit Tests for WP22: Hashnode Adapter, Target Matching Policies, and Zero-Noise Telegram Alerts."""

from __future__ import annotations

import io
import json
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from backlink_agent.advanced_verifier.models import (
    DetailedVerificationResult,
    LinkQualification,
    TargetMatchPolicy,
)
from backlink_agent.advanced_verifier.verifier import AdvancedBacklinkVerifier
from backlink_agent.execution.hashnode_adapter import HashnodeGraphQLAdapter
from backlink_agent.execution.manager import ExecutionManager
from backlink_agent.execution.models import ExecutionResult, ExecutionStatus
from backlink_agent.pipeline import BacklinkIntelligencePipeline
from backlink_agent.telegram_delivery.outcome_notifier import OutcomeNotificationFormatter
from backlink_agent.telegram_delivery.outbox_manager import TelegramOutboxManager


class MockHTTPResponse:
    def __init__(self, data_dict: dict, status: int = 200):
        self.data_bytes = json.dumps(data_dict).encode("utf-8")
        self.status = status
        self.headers = {"Content-Type": "application/json"}

    def read(self, *args, **kwargs):
        return self.data_bytes

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class TestWP22HashnodeAndZeroNoise(unittest.TestCase):
    def setUp(self):
        self.verifier = AdvancedBacklinkVerifier()

    def test_hashnode_adapter_dry_run_simulation(self):
        """Verifies Hashnode adapter runs in dry-run mode and populates 3 URLs."""
        adapter = HashnodeGraphQLAdapter(api_token=None)
        prospect = MagicMock()
        prospect.prospect_domain = "hashnode.com"
        prospect.draft = {
            "case_study_title": "Tracking Commercial AI Software Pricing in Pakistan",
            "dataset_citation_url": "https://aitoolgems.tech/prices/",
        }

        res = adapter.execute(prospect, dry_run=True)
        self.assertEqual(res.status, ExecutionStatus.DRY_RUN)
        self.assertEqual(res.adapter_name, "hashnode_graphql")
        self.assertTrue(res.is_successful())
        self.assertIn("hashnode.com", res.live_url)
        self.assertEqual(res.submission_url, "https://hashnode.com")
        self.assertEqual(res.submission_evidence_url, res.live_url)
        self.assertEqual(res.canonical_placement_url, res.live_url)
        self.assertEqual(res.get_effective_evidence_url(), res.live_url)

    def test_hashnode_adapter_mocked_success(self):
        """Mocks live GraphQL publishPost mutation and asserts post URL and 3 URLs."""
        adapter = HashnodeGraphQLAdapter(api_token="test_pat_token", publication_id="pub_123")
        prospect = MagicMock()
        prospect.prospect_domain = "hashnode.com"
        prospect.draft = {
            "case_study_title": "AI Tools Pricing in Emerging Markets",
            "dataset_citation_url": "https://aitoolgems.tech/prices/",
        }

        mock_gql_response = {
            "data": {
                "publishPost": {
                    "post": {
                        "id": "post_xyz789",
                        "slug": "ai-tools-pricing-in-emerging-markets",
                        "url": "https://blog.aitoolgems.tech/ai-tools-pricing-in-emerging-markets",
                        "title": "AI Tools Pricing in Emerging Markets",
                    }
                }
            }
        }

        with patch("urllib.request.urlopen", return_value=MockHTTPResponse(mock_gql_response)):
            res = adapter.execute(prospect, dry_run=False)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertEqual(res.live_url, "https://blog.aitoolgems.tech/ai-tools-pricing-in-emerging-markets")
        self.assertEqual(res.submission_url, "https://hashnode.com")
        self.assertEqual(res.submission_evidence_url, res.live_url)
        self.assertEqual(res.canonical_placement_url, res.live_url)

    def test_hashnode_adapter_publication_discovery(self):
        """Verifies publication ID auto-discovery via GraphQL 'me' query."""
        adapter = HashnodeGraphQLAdapter(api_token="valid_token")
        mock_discovery_response = {
            "data": {
                "me": {
                    "id": "user_456",
                    "username": "aitoolgems",
                    "publications": {
                        "edges": [
                            {"node": {"id": "pub_discovered_999", "title": "AI Tool Gems Tech Blog"}}
                        ]
                    },
                }
            }
        }

        with patch("urllib.request.urlopen", return_value=MockHTTPResponse(mock_discovery_response)):
            pub_id = adapter.discover_publication_id()

        self.assertEqual(pub_id, "pub_discovered_999")

    def test_execution_manager_routes_hashnode(self):
        """ExecutionManager correctly selects HashnodeGraphQLAdapter for hashnode domains."""
        manager = ExecutionManager()
        prospect = MagicMock()
        prospect.prospect_domain = "hashnode.com"
        prospect.prospect_type = "developer_publication"

        adapter = manager.resolve_adapter(prospect)
        self.assertIsInstance(adapter, HashnodeGraphQLAdapter)

    def test_target_match_policy_exact_url_and_allowed_urls(self):
        """Tests exact match policy and allowed alternative URLs."""
        html = '<html><body><a href="https://aitoolgems.tech/prices/" rel="ugc">Pricing Index</a></body></html>'
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://medium.com/post",
            target_url="https://aitoolgems.tech/prices/",
            match_policy=TargetMatchPolicy.EXACT_URL,
        )
        self.assertTrue(res.is_live_backlink)
        self.assertTrue(res.target_matches_approved)
        self.assertEqual(res.target_match_status, "live_exact_target")
        self.assertEqual(res.qualification, LinkQualification.USER_GENERATED_UGC)

        # Test allowed URL list
        html_guide = '<html><body><a href="https://aitoolgems.tech/guides/cursor-guide/" rel="nofollow">Cursor</a></body></html>'
        res_allowed = self.verifier.verify_html(
            html_text=html_guide,
            base_url="https://medium.com/post",
            target_url="https://aitoolgems.tech/prices/",
            match_policy=TargetMatchPolicy.ALLOWED_URLS,
            allowed_target_urls=["https://aitoolgems.tech/guides/cursor-guide/"],
        )
        self.assertTrue(res_allowed.is_live_backlink)
        self.assertTrue(res_allowed.target_matches_approved)
        self.assertEqual(res_allowed.target_match_status, "live_allowed_target")

    def test_target_match_policy_any_verified_canonical_asset(self):
        """Verifies ANY_VERIFIED_CANONICAL_ASSET accepts valid subpages on aitoolgems.tech as live backlinks."""
        html = '<html><body><p>Check <a href="https://aitoolgems.tech/guides/figma-ai-pakistan-guide/" rel="ugc nofollow">Figma Guide</a></p></body></html>'

        # Under ANY_VERIFIED_CANONICAL_ASSET, destination divergence is accepted as a live domain citation
        res = self.verifier.verify_html(
            html_text=html,
            base_url="https://medium.com/post",
            target_url="https://aitoolgems.tech/prices/",
            match_policy=TargetMatchPolicy.ANY_VERIFIED_CANONICAL_ASSET,
        )
        self.assertTrue(res.is_live_backlink)
        self.assertFalse(res.target_matches_approved)  # records that asset diverged
        self.assertEqual(res.target_match_status, "domain_asset_accepted")
        self.assertEqual(res.qualification, LinkQualification.DOMAIN_ASSET_ACCEPTED)
        self.assertEqual(res.actual_href, "https://aitoolgems.tech/guides/figma-ai-pakistan-guide/")

        # Under EXACT_URL, divergence is strictly WRONG_TARGET and NOT live
        res_strict = self.verifier.verify_html(
            html_text=html,
            base_url="https://medium.com/post",
            target_url="https://aitoolgems.tech/prices/",
            match_policy=TargetMatchPolicy.EXACT_URL,
        )
        self.assertFalse(res_strict.is_live_backlink)
        self.assertFalse(res_strict.target_matches_approved)
        self.assertEqual(res_strict.target_match_status, "wrong_target")
        self.assertEqual(res_strict.qualification, LinkQualification.WRONG_TARGET)

    def test_silent_discovery_suppresses_telegram_enqueuing(self):
        """Verifies silent_discovery=True suppresses daily summary and discovery card messages in outbox."""
        mock_discovery = MagicMock()
        mock_discovery.run_discovery.return_value = {"prospects": []}

        mock_outbox = MagicMock()

        pipeline = BacklinkIntelligencePipeline(
            discovery_orchestrator=mock_discovery,
            outbox_manager=mock_outbox,
            reports_dir=Path("seo-agent/reports/backlinks"),
        )

        res = pipeline.run_daily_intelligence(
            dispatch_telegram=False,
            export_reports=False,
            silent_discovery=True,
        )

        self.assertEqual(res["discovered_count"], 0)
        # Outbox enqueue should NOT be called at all
        mock_outbox.enqueue.assert_not_called()

    def test_outcome_notifier_format_backlink_won(self):
        """Verifies celebratory Backlink Won card formatting."""
        card = OutcomeNotificationFormatter.format_backlink_won(
            domain="medium.com",
            placement_url="https://medium.com/@mrehmanfarooq6/story-38a1b2f98754",
            target_url="https://aitoolgems.tech/prices/",
            anchor_text="AI Tool Gems Pricing Index",
            rel_tokens=["ugc", "nofollow"],
            qualification="user_generated_ugc",
            target_match_status="live_exact_target",
            http_status=200,
        )

        self.assertIn("🏆 *Backlink Won & Verified Live [DOM Verified]*", card)
        self.assertIn("medium.com", card)
        self.assertIn("https://aitoolgems.tech/prices/", card)
        self.assertIn("rel=\"ugc, nofollow\"", card)
        self.assertIn("live_exact_target", card)


if __name__ == "__main__":
    unittest.main()
