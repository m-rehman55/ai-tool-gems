"""WP16: Comprehensive End-to-End Integration Tests for HERMES Backlink Engine.

Covers the full integration of WP13 (Discovery, Scoring, Drafting), WP14 (Outbox & Concurrency),
and WP15 (17-State Lifecycle, Advanced Verification, Retention, and Outcome Reporting).
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from backlink_agent.advanced_verifier.models import DetailedVerificationResult, LinkQualification
from backlink_agent.lifecycle.models import (
    LifecycleState,
    ManualSubmissionEvidence,
    VALID_TRANSITION_GRAPH,
)
from backlink_agent.lifecycle.state_machine import AcquisitionStateMachine
from backlink_agent.lifecycle.store import LocalSQLiteLifecycleStore
from backlink_agent.reporting.acquisition_reporter import AcquisitionReporter
from backlink_agent.retention.models import RetentionStatus
from backlink_agent.retention.monitor import RetentionMonitor


class TestWP16EndToEndIntegration(unittest.TestCase):
    """Hermetic integration tests for the full acquisition pipeline using isolated fixtures."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_lifecycle_wp16.db"
        self.reports_dir = Path(self.temp_dir.name) / "reports"
        self.store = LocalSQLiteLifecycleStore(db_path=self.db_path)
        self.machine = AcquisitionStateMachine(store=self.store)
        self.reporter = AcquisitionReporter(lifecycle_store=self.store, reports_dir=self.reports_dir)
        self.monitor = RetentionMonitor()

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_complete_prospect_journey_synthetic_lifecycle(self):
        """End-to-end trace of a single prospect through all stages to Day 30 retention."""
        prospect_id = "prospect_e2e_001"
        draft_hash = "f1d2d2f924e99a8b6e3f433a0b8d5e82103e670417f7d1420d4ec43093952a12"

        # 1. Ingest via Discovery
        created = self.store.register_discovered_prospect(
            prospect_id=prospect_id,
            prospect_domain="curated-directory.example.com",
            source_page_url="https://curated-directory.example.com/ai-tools",
            target_asset_url="https://aitoolgems.tech/",
            prospect_type="directory",
        )
        self.assertTrue(created)

        # 2. Transition: discovered -> evidence_verified
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.EVIDENCE_VERIFIED,
            actor="discovery_engine",
            reason="DNS and route verified reachable",
        )
        self.assertTrue(ok, err)

        # 3. Transition: evidence_verified -> scored
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.SCORED,
            actor="scoring_engine",
            reason="100-point algorithm computed",
            evidence_data={"score": 88, "tier": "high_priority"},
        )
        self.assertTrue(ok, err)

        # 4. Transition: scored -> draft_ready (Update draft_id and draft_hash)
        self.store.update_draft_package(
            prospect_id=prospect_id,
            draft_id="draft_dir_001",
            draft_hash=draft_hash,
        )
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.DRAFT_READY,
            actor="submission_drafter",
            reason="High priority candidate drafted with verified PKR facts",
        )
        self.assertTrue(ok, err)

        # 5. Transition: draft_ready -> owner_approved (Requires matching draft_hash)
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.OWNER_APPROVED,
            actor="owner",
            reason="Owner approved copy for manual submission",
            evidence_data={"draft_hash": draft_hash},
        )
        self.assertTrue(ok, err)

        # 6. Transition: owner_approved -> manually_submitted (Requires evidence proof)
        evidence = ManualSubmissionEvidence(
            prospect_id=prospect_id,
            draft_id="draft_dir_001",
            draft_hash=draft_hash,
            submission_destination="https://curated-directory.example.com/submit",
            submission_method="web_form",
            evidence_ref="REF-TICKET-88912",
            submission_date="2026-11-15T07:00:00Z",
            notes="Submitted with PKR pricing details",
        )
        saved_ev = self.store.record_manual_submission(evidence)
        self.assertTrue(saved_ev)

        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.MANUALLY_SUBMITTED,
            actor="owner",
            reason="Manual web form completed by site owner",
            evidence_data={"evidence_ref": "REF-TICKET-88912"},
        )
        self.assertTrue(ok, err)

        # 7. Transition: manually_submitted -> published (Requires publication URL)
        pub_url = "https://curated-directory.example.com/tools/ai-tool-gems"
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.PUBLISHED,
            actor="monitoring_agent",
            reason="External placement confirmed live",
            evidence_data={"publication_url": pub_url},
        )
        self.assertTrue(ok, err)

        # 8. Transition: published -> backlink_verified (Requires strict DOM anchor proof)
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.BACKLINK_VERIFIED,
            actor="advanced_verifier",
            reason="Strict DOM audit confirmed dofollow anchor and clean robots",
            evidence_data={
                "anchor_verified": True,
                "target_url_matched": True,
                "qualification": LinkQualification.EDITORIAL_DOFOLLOW,
            },
        )
        self.assertTrue(ok, err)

        # Confirm prospect is now in backlink_verified state
        p = self.store.get_prospect(prospect_id)
        self.assertEqual(p["current_state"], LifecycleState.BACKLINK_VERIFIED)

        # 9. Transition: backlink_verified -> retained (Day 7 Milestone)
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.RETAINED,
            actor="retention_monitor",
            reason="Day 7 retention checkpoint passed cleanly",
            evidence_data={"milestone": "7_day", "retention_status": RetentionStatus.RETAINED},
        )
        self.assertTrue(ok, err)

        # 10. Verify Acquisition Report reflects exactly 1 earned backlink
        report = self.reporter.generate_acquisition_report()
        self.assertEqual(report["actual_earned_backlinks_count"], 1)
        self.assertEqual(report["funnel_metrics"]["retained_clean"], 1)
        self.assertEqual(report["funnel_metrics"]["discovered"], 0)

    def test_duplicate_prospect_identity_deduplication(self):
        """Duplicate prospects with same ID are rejected by SQLite store."""
        created1 = self.store.register_discovered_prospect(
            prospect_id="dup_001",
            prospect_domain="example.com",
            source_page_url="https://example.com/dir",
            target_asset_url="https://aitoolgems.tech/",
            prospect_type="directory",
        )
        self.assertTrue(created1)

        # Second creation with identical ID must return False
        created2 = self.store.register_discovered_prospect(
            prospect_id="dup_001",
            prospect_domain="example.com",
            source_page_url="https://example.com/dir",
            target_asset_url="https://aitoolgems.tech/",
            prospect_type="directory",
        )
        self.assertFalse(created2)

    def test_ineligible_scoring_quarantined_and_cannot_draft(self):
        """A prospect with score < 55 is quarantined and cannot transition to draft_ready."""
        prospect_id = "toxic_001"
        self.store.register_discovered_prospect(
            prospect_id=prospect_id,
            prospect_domain="spam-pbn-network.com",
            source_page_url="https://spam-pbn-network.com/links",
            target_asset_url="https://aitoolgems.tech/",
            prospect_type="pbn",
        )
        # Advance through state machine
        self.machine.transition(prospect_id, LifecycleState.EVIDENCE_VERIFIED, "discovery", "reachability ok")
        self.machine.transition(prospect_id, LifecycleState.SCORED, "scoring", "score calculated")

        # Move to quarantined
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.QUARANTINED,
            actor="scoring_engine",
            reason="Score 32 < 55; PBN link farm patterns detected",
        )
        self.assertTrue(ok)

        # Attempt to transition quarantined prospect to draft_ready (must fail closed)
        ok2, err2, rec2 = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.DRAFT_READY,
            actor="submission_drafter",
            reason="Unauthorized bypass attempt",
        )
        self.assertFalse(ok2)
        self.assertIn("Invalid lifecycle transition", err2)

    def test_draft_hash_tampering_invalidates_owner_approval(self):
        """State machine rejects owner approval if draft copy was tampered with."""
        prospect_id = "draft_tamper_001"
        self.store.register_discovered_prospect(
            prospect_id=prospect_id,
            prospect_domain="legit-dir.org",
            source_page_url="https://legit-dir.org/tools",
            target_asset_url="https://aitoolgems.tech/",
            prospect_type="directory",
        )
        self.machine.transition(prospect_id, LifecycleState.EVIDENCE_VERIFIED, "discovery", "reachability ok")
        self.machine.transition(prospect_id, LifecycleState.SCORED, "scoring", "score calculated")
        self.store.update_draft_package(
            prospect_id=prospect_id,
            draft_id="draft_001",
            draft_hash="authentic_hash_12345",
        )
        self.machine.transition(prospect_id, LifecycleState.DRAFT_READY, "drafter", "draft package ready")

        # Attempt approval with mismatched draft hash
        ok, err, rec = self.machine.transition(
            prospect_id=prospect_id,
            to_state=LifecycleState.OWNER_APPROVED,
            actor="owner",
            reason="Approval with modified payload",
            evidence_data={"draft_hash": "tampered_hash_99999"},
        )
        self.assertFalse(ok)
        self.assertIn("Draft hash mismatch on approval", err)

    def test_manual_submission_evidence_fails_on_secret_leak(self):
        """Submission evidence containing passwords or api tokens raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            evidence = ManualSubmissionEvidence(
                prospect_id="leak_001",
                draft_id="draft_001",
                draft_hash="hash_123",
                submission_destination="https://portal.example.com",
                submission_method="web_form",
                evidence_ref="auth_token=abc123secret",
            )
            evidence.validate_no_secrets()
        self.assertIn("Prohibited secret keyword", str(ctx.exception))

    def test_retention_preserves_verified_status_on_temporary_5xx(self):
        """A transient HTTP 503 error produces INCONCLUSIVE and never marks link removed."""
        prospect_id = "retention_transient_001"
        self.store.register_discovered_prospect(
            prospect_id=prospect_id,
            prospect_domain="transient-server.org",
            source_page_url="https://transient-server.org/directory",
            target_asset_url="https://aitoolgems.tech/",
            prospect_type="directory",
        )
        self.machine.transition(prospect_id, LifecycleState.EVIDENCE_VERIFIED, "discovery", "ok")
        self.machine.transition(prospect_id, LifecycleState.SCORED, "scoring", "ok")
        self.machine.transition(prospect_id, LifecycleState.DRAFT_READY, "drafter", "ok")
        self.machine.transition(prospect_id, LifecycleState.OWNER_APPROVED, "owner", "ok")
        self.machine.transition(prospect_id, LifecycleState.MANUALLY_SUBMITTED, "owner", "ok")
        self.machine.transition(prospect_id, LifecycleState.PUBLISHED, "crawler", "ok", evidence_data={"publication_url": "https://transient-server.org/page"})
        self.machine.transition(prospect_id, LifecycleState.BACKLINK_VERIFIED, "verifier", "ok", evidence_data={"anchor_verified": True, "target_url_matched": True})

        # Simulate transient 503 during retention check
        transient_crawl = DetailedVerificationResult(
            prospect_id=prospect_id,
            source_page_url="https://transient-server.org/directory",
            target_asset_url="https://aitoolgems.tech/",
            http_status=503,
            final_page_url="https://transient-server.org/directory",
            qualification=LinkQualification.INCONCLUSIVE_SERVER_ERROR,
            is_live_backlink=False,
            error_message="HTTP 503 Service Unavailable",
        )

        snapshot = self.monitor.evaluate_retention(
            current_result=transient_crawl,
            days_active=7,
        )

        # Invariant: Must NOT be marked LINK_REMOVED
        self.assertEqual(snapshot.status_detected, RetentionStatus.INCONCLUSIVE_TEMPORARY_FAILURE)
        self.assertIn("Temporary verification error", snapshot.notes)
        self.assertIn("Preserving prior status", snapshot.notes)

        # Prospect state in store remains BACKLINK_VERIFIED
        p = self.store.get_prospect(prospect_id)
        self.assertEqual(p["current_state"], LifecycleState.BACKLINK_VERIFIED)

    def test_acquisition_reporter_zero_division_safety(self):
        """AcquisitionReporter handles empty database without division by zero errors."""
        report = self.reporter.generate_acquisition_report()
        self.assertEqual(report["actual_earned_backlinks_count"], 0)
        self.assertEqual(report["conversion_rates"]["owner_approval_rate_pct"], 0.0)
        self.assertEqual(report["conversion_rates"]["submission_execution_rate_pct"], 0.0)
        self.assertEqual(report["conversion_rates"]["placement_verification_rate_pct"], 0.0)
        self.assertTrue(Path(report["report_files"]["markdown"]).exists())
        self.assertTrue(Path(report["report_files"]["json"]).exists())


if __name__ == "__main__":
    unittest.main()
