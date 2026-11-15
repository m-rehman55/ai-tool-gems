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
        # First check when anchor vanishes is SUSPECTED_REMOVAL (recheck scheduled)
        snap1 = RetentionMonitor.evaluate_retention(curr, days_active=60)
        self.assertEqual(snap1.status_detected, RetentionStatus.SUSPECTED_REMOVAL)

        # Repeat confirmation confirms LINK_REMOVED
        snap2 = RetentionMonitor.evaluate_retention(curr, days_active=61, previous_snapshot=snap1)
        self.assertEqual(snap2.status_detected, RetentionStatus.LINK_REMOVED)

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

    def test_http_404_410_removal_confirmation(self):
        """Initial 404 flags SUSPECTED_REMOVAL; 410 flags STRONG_REMOVAL; repeat check confirms LINK_REMOVED."""
        curr_404 = DetailedVerificationResult(
            prospect_id="p1",
            source_page_url="https://site.example/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=404,
            final_page_url="https://site.example/page",
            anchor_found=False,
            qualification=LinkQualification.ANCHOR_MISSING,
        )
        # 1. First 404: Suspected removal (not yet confirmed)
        snap1 = RetentionMonitor.evaluate_retention(curr_404, days_active=14)
        self.assertEqual(snap1.status_detected, RetentionStatus.SUSPECTED_REMOVAL)
        self.assertIn("Suspected removal", snap1.notes)

        # 2. Second consecutive 404: Confirmed removal
        snap2 = RetentionMonitor.evaluate_retention(curr_404, days_active=15, previous_snapshot=snap1)
        self.assertEqual(snap2.status_detected, RetentionStatus.LINK_REMOVED)
        self.assertIn("Confirmed removal", snap2.notes)

        # 3. First 410: Strong removal evidence
        curr_410 = DetailedVerificationResult(
            prospect_id="p1",
            source_page_url="https://site.example/page",
            target_asset_url="https://aitoolgems.tech/",
            http_status=410,
            final_page_url="https://site.example/page",
            anchor_found=False,
            qualification=LinkQualification.ANCHOR_MISSING,
        )
        snap_410_1 = RetentionMonitor.evaluate_retention(curr_410, days_active=16)
        self.assertEqual(snap_410_1.status_detected, RetentionStatus.STRONG_REMOVAL_EVIDENCE)

        # 4. Repeat 410: Confirmed removal
        snap_410_2 = RetentionMonitor.evaluate_retention(curr_410, days_active=17, previous_snapshot=snap_410_1)
        self.assertEqual(snap_410_2.status_detected, RetentionStatus.LINK_REMOVED)

    def test_http_403_access_restricted_preserves_status(self):
        """HTTP 403 Access Restricted / WAF challenge preserves status as inconclusive."""
        prev = RetentionSnapshot(
            prospect_id="p3",
            verification_date="2026-11-01T00:00:00Z",
            days_since_first_verified=30,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            anchor_text="AI Tool Gems",
            target_destination="https://aitoolgems.tech/",
            content_hash="hash_p3",
        )
        curr_403 = DetailedVerificationResult(
            prospect_id="p3",
            source_page_url="https://site.example/waf-blocked",
            target_asset_url="https://aitoolgems.tech/",
            http_status=403,
            final_page_url="https://site.example/waf-blocked",
            anchor_found=False,
            qualification=LinkQualification.ANCHOR_MISSING,
        )
        snap = RetentionMonitor.evaluate_retention(curr_403, days_active=35, previous_snapshot=prev)
        self.assertEqual(snap.status_detected, RetentionStatus.INCONCLUSIVE_ACCESS_RESTRICTED)
        self.assertEqual(snap.anchor_text, "AI Tool Gems")
        self.assertIn("HTTP 403", snap.notes)

    def test_placement_recovery_after_degradation(self):
        """A placement previously in SUSPECTED_REMOVAL transitions to RECOVERED when anchor reappears."""
        suspected_snap = RetentionSnapshot(
            prospect_id="p4",
            verification_date="2026-11-01T00:00:00Z",
            days_since_first_verified=30,
            qualification=LinkQualification.ANCHOR_MISSING,
            anchor_text="AI Tool Gems",
            target_destination="https://aitoolgems.tech/",
            content_hash="hash_old",
            status_detected=RetentionStatus.SUSPECTED_REMOVAL,
        )
        recovered_curr = DetailedVerificationResult(
            prospect_id="p4",
            source_page_url="https://site.example/recovered",
            target_asset_url="https://aitoolgems.tech/",
            http_status=200,
            final_page_url="https://site.example/recovered",
            anchor_found=True,
            actual_anchor_text="AI Tool Gems",
            actual_href="https://aitoolgems.tech/",
            final_target_destination="https://aitoolgems.tech/",
            target_matches_approved=True,
            is_indexable=True,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            is_live_backlink=True,
        )
        snap = RetentionMonitor.evaluate_retention(recovered_curr, days_active=35, previous_snapshot=suspected_snap)
        self.assertEqual(snap.status_detected, RetentionStatus.RECOVERED)
        self.assertIn("Placement successfully re-verified as healthy", snap.notes)

    def test_http_429_rate_limit_preserves_status(self):
        """HTTP 429 Too Many Requests is a temporary rate limit and must preserve prior status."""
        prev = RetentionSnapshot(
            prospect_id="p2",
            verification_date="2026-11-01T00:00:00Z",
            days_since_first_verified=30,
            qualification=LinkQualification.EDITORIAL_DOFOLLOW,
            anchor_text="AI Tool Gems",
            target_destination="https://aitoolgems.tech/",
            content_hash="hash_p2",
        )
        curr_429 = DetailedVerificationResult(
            prospect_id="p2",
            source_page_url="https://site.example/rate-limited",
            target_asset_url="https://aitoolgems.tech/",
            http_status=429,
            final_page_url="https://site.example/rate-limited",
            anchor_found=False,
            qualification=LinkQualification.ANCHOR_MISSING,
        )
        snap = RetentionMonitor.evaluate_retention(curr_429, days_active=35, previous_snapshot=prev)
        self.assertEqual(snap.status_detected, RetentionStatus.INCONCLUSIVE_TEMPORARY_FAILURE)
        self.assertEqual(snap.anchor_text, "AI Tool Gems")
        self.assertIn("HTTP 429", snap.notes)


if __name__ == "__main__":
    unittest.main()
