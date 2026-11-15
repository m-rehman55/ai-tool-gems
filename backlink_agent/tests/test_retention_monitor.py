"""Unit tests for WP15 Retention Monitor and Multi-Milestone Rechecks."""

import unittest

from backlink_agent.advanced_verifier.models import DetailedVerificationResult, LinkQualification
from backlink_agent.retention import RetentionMonitor, RetentionSnapshot, RetentionStatus


class TestRetentionMonitor(unittest.TestCase):
    def _create_verified_result(
        self,
        anchor_text: str = "AI Tool Gems",
        target: str = "https://aitoolgems.tech/prices/",
        qualification: str = LinkQualification.EDITORIAL_DOFOLLOW,
        is_indexable: bool = True,
        anchor_found: bool = True,
        target_matches: bool = True,
    ) -> DetailedVerificationResult:
        res = DetailedVerificationResult(
            prospect_id="p1",
            source_page_url="https://dev.to/article",
            target_asset_url=target,
            http_status=200,
            final_page_url="https://dev.to/article",
            is_indexable=is_indexable,
            anchor_found=anchor_found,
            actual_anchor_text=anchor_text,
            actual_href=target,
            final_target_destination=target,
            target_matches_approved=target_matches,
            qualification=qualification,
            is_live_backlink=(anchor_found and target_matches and is_indexable),
        )
        res.content_hash = res.compute_content_hash()
        return res

    def test_clean_retention_7_day_milestone(self):
        curr = self._create_verified_result()
        snap = RetentionMonitor.evaluate_retention(curr, days_active=7)
        self.assertEqual(snap.status_detected, RetentionStatus.RETAINED)
        self.assertEqual(snap.days_since_first_verified, 7)

    def test_anchor_text_alteration_detected(self):
        prev = RetentionSnapshot(
            prospect_id="p1",
            verification_date="2026-11-01T00:00:00Z",
            days_since_first_verified=7,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            anchor_text="Old Anchor Text",
            target_destination="https://aitoolgems.tech/prices/",
            content_hash="old_hash_123",
        )
        curr = self._create_verified_result(anchor_text="Modified Anchor Text")
        snap = RetentionMonitor.evaluate_retention(curr, days_active=14, previous_snapshot=prev)

        self.assertEqual(snap.status_detected, RetentionStatus.ANCHOR_CHANGED)
        self.assertIn("Modified Anchor Text", snap.anchor_text)
        self.assertIn("Old Anchor Text", snap.notes)

    def test_target_destination_altered(self):
        curr = self._create_verified_result(
            target="https://other-competitor.com",
            target_matches=False,
            qualification=LinkQualification.WRONG_TARGET,
        )
        snap = RetentionMonitor.evaluate_retention(curr, days_active=30)
        self.assertEqual(snap.status_detected, RetentionStatus.TARGET_CHANGED)

    def test_noindex_directive_added_flagged(self):
        curr = self._create_verified_result(
            is_indexable=False,
            qualification=LinkQualification.SOURCE_NOINDEX,
        )
        curr.noindex_source = "meta_robots"
        snap = RetentionMonitor.evaluate_retention(curr, days_active=30)
        self.assertEqual(snap.status_detected, RetentionStatus.NOINDEX_ADDED)

    def test_anchor_removed_flagged(self):
        curr = self._create_verified_result(
            anchor_found=False,
            qualification=LinkQualification.ANCHOR_MISSING,
        )
        snap = RetentionMonitor.evaluate_retention(curr, days_active=60)
        self.assertEqual(snap.status_detected, RetentionStatus.LINK_REMOVED)

    def test_temporary_server_error_preserves_prior_status(self):
        """Temporary 503 or socket timeout must NOT falsely mark backlink as removed."""
        prev = RetentionSnapshot(
            prospect_id="p1",
            verification_date="2026-11-01T00:00:00Z",
            days_since_first_verified=30,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            anchor_text="AI Tool Gems",
            target_destination="https://aitoolgems.tech/prices/",
            content_hash="active_hash",
        )
        temp_err_res = DetailedVerificationResult(
            prospect_id="p1",
            source_page_url="https://dev.to/article",
            target_asset_url="https://aitoolgems.tech/prices/",
            http_status=503,
            final_page_url="https://dev.to/article",
            qualification=LinkQualification.INCONCLUSIVE_SERVER_ERROR,
            is_live_backlink=False,
            error_message="HTTP 503 Service Unavailable",
        )
        snap = RetentionMonitor.evaluate_retention(temp_err_res, days_active=31, previous_snapshot=prev)

        self.assertEqual(snap.status_detected, RetentionStatus.INCONCLUSIVE_TEMPORARY_FAILURE)
        self.assertEqual(snap.anchor_text, "AI Tool Gems")  # Preserved from previous snapshot!
        self.assertIn("Temporary verification error", snap.notes)


if __name__ == "__main__":
    unittest.main()
