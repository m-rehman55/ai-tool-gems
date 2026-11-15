"""Unit tests for WP15 Backlink Acquisition Lifecycle and State Machine."""

import shutil
import tempfile
import unittest
from pathlib import Path

from backlink_agent.lifecycle import (
    AcquisitionStateMachine,
    LifecycleState,
    LocalSQLiteLifecycleStore,
    ManualSubmissionEvidence,
)


class TestAcquisitionLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.tmp_dir / "lifecycle_test.db"
        self.store = LocalSQLiteLifecycleStore(self.db_path)
        self.machine = AcquisitionStateMachine(self.store)

        # Register seed prospect
        self.store.register_discovered_prospect(
            prospect_id="p_test_01",
            prospect_domain="dev.to",
            source_page_url="https://dev.to/new",
            target_asset_url="https://aitoolgems.tech/prices/",
            prospect_type="tech_publication",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_happy_path_lifecycle_progression(self):
        """Tests sequential progression from discovered to retained."""
        # 1. evidence_verified
        ok, err, rec = self.machine.transition(
            "p_test_01", LifecycleState.EVIDENCE_VERIFIED, "verifier_engine", "Page reachable"
        )
        self.assertTrue(ok, err)

        # 2. scored
        ok, err, rec = self.machine.transition(
            "p_test_01", LifecycleState.SCORED, "scoring_engine", "Scored 92/100"
        )
        self.assertTrue(ok, err)

        # 3. draft_ready
        ok, err, rec = self.machine.transition(
            "p_test_01", LifecycleState.DRAFT_READY, "drafting_engine", "Draft package generated"
        )
        self.assertTrue(ok, err)

        # Update draft hash in prospect record
        with self.store._get_connection() as conn:
            conn.execute(
                "UPDATE prospect_lifecycle SET draft_hash = 'hash123' WHERE prospect_id = 'p_test_01'"
            )

        # 4. owner_approved
        ok, err, rec = self.machine.transition(
            "p_test_01",
            LifecycleState.OWNER_APPROVED,
            "owner",
            "Approved via Telegram",
            evidence_data={"draft_hash": "hash123"},
        )
        self.assertTrue(ok, err)

        # Record manual submission evidence
        sub_evidence = ManualSubmissionEvidence(
            prospect_id="p_test_01",
            draft_id="d_01",
            draft_hash="hash123",
            submission_destination="https://dev.to/new",
            submission_method="editorial_pitch",
            evidence_ref="https://github.com/m-rehman55/ai-tool-gems/issues/42",
            optional_publication_url="https://dev.to/aitoolgems/ai-tools-pricing-case-study",
        )
        sub_id = self.store.record_manual_submission(sub_evidence)
        self.assertIsNotNone(sub_id)

        # 5. manually_submitted
        ok, err, rec = self.machine.transition(
            "p_test_01", LifecycleState.MANUALLY_SUBMITTED, "owner", "Submitted by owner"
        )
        self.assertTrue(ok, err)

        # 6. published (Requires publication URL)
        ok, err, rec = self.machine.transition(
            "p_test_01",
            LifecycleState.PUBLISHED,
            "verifier_engine",
            "Editorial post published",
            evidence_data={"publication_url": "https://dev.to/aitoolgems/ai-tools-pricing-case-study"},
        )
        self.assertTrue(ok, err)

        # 7. backlink_verified (Requires DOM anchor verification evidence)
        ok, err, rec = self.machine.transition(
            "p_test_01",
            LifecycleState.BACKLINK_VERIFIED,
            "verifier_engine",
            "Live DOM anchor confirmed",
            evidence_data={"anchor_verified": True, "target_url_matched": True},
        )
        self.assertTrue(ok, err)

        # 8. retained
        ok, err, rec = self.machine.transition(
            "p_test_01", LifecycleState.RETAINED, "retention_monitor", "7-Day milestone confirmed"
        )
        self.assertTrue(ok, err)

        p = self.store.get_prospect("p_test_01")
        self.assertEqual(p["current_state"], LifecycleState.RETAINED)

    def test_invalid_lifecycle_transition_rejected(self):
        """Attempts to jump directly from discovered to backlink_verified."""
        ok, err, rec = self.machine.transition(
            "p_test_01", LifecycleState.BACKLINK_VERIFIED, "hacker", "Illegal jump"
        )
        self.assertFalse(ok)
        self.assertIn("Invalid lifecycle transition", err)

    def test_publication_gate_rejects_missing_publication_url(self):
        """Cannot transition to published without publication URL."""
        # Fast forward to manually_submitted
        with self.store._get_connection() as conn:
            conn.execute(
                "UPDATE prospect_lifecycle SET current_state = 'manually_submitted' WHERE prospect_id = 'p_test_01'"
            )

        ok, err, rec = self.machine.transition(
            "p_test_01", LifecycleState.PUBLISHED, "verifier_engine", "Claim published without proof"
        )
        self.assertFalse(ok)
        self.assertIn("Publication URL or verification proof required", err)

    def test_backlink_verified_gate_rejects_without_dom_evidence(self):
        """Cannot transition to backlink_verified without anchor verification evidence."""
        with self.store._get_connection() as conn:
            conn.execute(
                "UPDATE prospect_lifecycle SET current_state = 'published', publication_url = 'https://dev.to/test' WHERE prospect_id = 'p_test_01'"
            )

        ok, err, rec = self.machine.transition(
            "p_test_01", LifecycleState.BACKLINK_VERIFIED, "verifier_engine", "Attempting verify without anchor evidence"
        )
        self.assertFalse(ok)
        self.assertIn("Independent DOM anchor verification evidence required", err)

    def test_manual_submission_evidence_blocks_secrets(self):
        """Adversarial security test: submission evidence cannot store passwords or tokens."""
        bad_evidence = ManualSubmissionEvidence(
            prospect_id="p_test_01",
            draft_id="d1",
            draft_hash="h1",
            submission_destination="https://example.com/login",
            submission_method="web_form",
            evidence_ref="screenshot.png",
            notes="Login with password secret123",
        )
        with self.assertRaises(ValueError) as ctx:
            self.store.record_manual_submission(bad_evidence)
        self.assertIn("Prohibited secret keyword", str(ctx.exception))

    def test_idempotent_transition_skips_duplicate(self):
        """Duplicate transition with same idempotency_key is safely ignored."""
        ok1, err1, _ = self.machine.transition(
            "p_test_01",
            LifecycleState.EVIDENCE_VERIFIED,
            "engine",
            "Run 1",
            idempotency_key="idemp_101",
        )
        self.assertTrue(ok1)

        ok2, err2, _ = self.machine.transition(
            "p_test_01",
            LifecycleState.EVIDENCE_VERIFIED,
            "engine",
            "Run 2 duplicate",
            idempotency_key="idemp_101",
        )
        self.assertFalse(ok2)  # Skipped safely


if __name__ == "__main__":
    unittest.main()
