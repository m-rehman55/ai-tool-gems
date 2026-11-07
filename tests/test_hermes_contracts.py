"""
Unit tests for HERMES Executive Task & Evidence Contracts.
Verifies compliance with H1 (Task Contract) and H2 (Evidence Contract) standards.
"""

import unittest
from hermes_core.contracts import (
    ApprovalRequirement,
    EvidenceContract,
    EvidenceTier,
    EvidenceUpgradeViolation,
    RiskClassification,
    TaskContract,
    TaskStatus,
    PriorityLevel,
)


class TestHermesContracts(unittest.TestCase):
    """Verifies H1 TaskContract and H2 EvidenceContract compliance."""

    def test_task_contract_contains_all_fifteen_required_fields(self):
        """H1: Verifies TaskContract possesses all 15 mandatory governance fields."""
        task = TaskContract(
            task_id="TASK-SEO-TEST-001",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-01-AIO",
            objective="Audit site-wide Google AI Overviews extractability",
            scope="pakistan_commercial",
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["score_80_pages", "export_evidence_matrix"],
            input_evidence={"sample_url": "https://aitoolgems.tech/tools/chatgpt/"},
            required_tools=["aio_agent", "grounding_scorer"],
            dependencies=["TASK-BASELINE-001"],
            expected_output="Durable report in reports/aeo_geo_visibility_audit.md",
            permission_level="READ_ONLY",
            verification_method="AUTOMATED_UNIT_TEST",
            blocker=None,
        )

        # 1. Unique task ID
        self.assertEqual(task.task_id, "TASK-SEO-TEST-001")
        # 2. Objective
        self.assertEqual(task.objective, "Audit site-wide Google AI Overviews extractability")
        # 3. Owner agent
        self.assertEqual(task.owner_agent, "AGENT-01-AIO")
        # 4. Input evidence
        self.assertIn("sample_url", task.input_evidence)
        # 5. Required tools
        self.assertIn("aio_agent", task.required_tools)
        # 6. Dependencies
        self.assertIn("TASK-BASELINE-001", task.dependencies)
        # 7. Risk level
        self.assertEqual(task.risk_level, RiskClassification.READ_ONLY)
        # 8. Permission level
        self.assertEqual(task.permission_level, "READ_ONLY")
        # 9. Expected output
        self.assertEqual(task.expected_output, "Durable report in reports/aeo_geo_visibility_audit.md")
        # 10. Acceptance criteria
        self.assertIn("score_80_pages", task.acceptance_criteria)
        # 11. Verification method
        self.assertEqual(task.verification_method, "AUTOMATED_UNIT_TEST")
        # 12. Timestamps
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
        # 13. Status
        self.assertEqual(task.status, TaskStatus.NOT_STARTED)
        # 14. Blocker
        self.assertIsNone(task.blocker)
        # 15. Approval requirement
        self.assertEqual(task.approval_requirement, ApprovalRequirement.AUTONOMOUS_APPROVED)

    def test_evidence_contract_eight_tiers_supported(self):
        """H2: Verifies all 8 distinct evidence tiers are supported."""
        expected_tiers = {
            "LIVE_API",
            "LIVE_BROWSER",
            "LIVE_REPOSITORY",
            "CACHED",
            "HISTORICAL",
            "ESTIMATED",
            "INFERRED",
            "UNVERIFIED",
        }
        actual_tiers = {tier.value for tier in EvidenceTier}
        self.assertEqual(expected_tiers, actual_tiers)

    def test_evidence_upgrade_violation_raised_on_illegal_promotion(self):
        """H2: An agent must never upgrade an estimate or inference into verified evidence."""
        # Valid: Live API verified as Live API
        self.assertTrue(EvidenceContract.validate_evidence_upgrade(EvidenceTier.LIVE_API, EvidenceTier.LIVE_API))

        # Illegal: ESTIMATED upgraded to LIVE_API
        with self.assertRaises(EvidenceUpgradeViolation):
            EvidenceContract.validate_evidence_upgrade(EvidenceTier.ESTIMATED, EvidenceTier.LIVE_API)

        # Illegal: INFERRED upgraded to LIVE_REPOSITORY
        with self.assertRaises(EvidenceUpgradeViolation):
            EvidenceContract.validate_evidence_upgrade(EvidenceTier.INFERRED, EvidenceTier.LIVE_REPOSITORY)

        # Illegal: UNVERIFIED upgraded to LIVE_BROWSER
        with self.assertRaises(EvidenceUpgradeViolation):
            EvidenceContract.validate_evidence_upgrade(EvidenceTier.UNVERIFIED, EvidenceTier.LIVE_BROWSER)

    def test_estimated_evidence_cannot_be_verified_flagged(self):
        """H2: Inferred and estimated evidence cannot have is_verified=True."""
        ev = EvidenceContract(
            evidence_id="EV-TEST-001",
            source_agent="AGENT-03-KEYWORD",
            tier=EvidenceTier.ESTIMATED,
            description="Estimated organic CTR based on impression volume",
            is_verified=True,  # Attempting to verify an estimate
        )
        self.assertFalse(ev.is_verified, "Estimated evidence must never be flagged is_verified=True")

    def test_task_status_eleven_statuses_supported(self):
        """Section 18: Verifies all 11 standardized task statuses are supported."""
        expected_statuses = {
            "NOT_STARTED",
            "IN_PROGRESS",
            "BLOCKED_PENDING_CREDENTIALS",
            "BLOCKED_PENDING_APPROVAL",
            "BLOCKED_EXTERNAL_DEPENDENCY",
            "IMPLEMENTED",
            "TESTED",
            "VERIFIED",
            "DEPLOYED",
            "FAILED",
            "NOT_APPLICABLE",
        }
        actual_statuses = {status.value for status in TaskStatus}
        self.assertEqual(expected_statuses, actual_statuses)

    def test_priority_levels_five_tiers_supported(self):
        """Section 18: Verifies all 5 standardized priority levels are supported."""
        expected_priorities = {"P0", "P1", "P2", "P3", "P4"}
        actual_priorities = {p.value for p in PriorityLevel}
        self.assertEqual(expected_priorities, actual_priorities)

    def test_mark_verified_requires_independent_evidence(self):
        """Section 18: Do not mark an item VERIFIED merely because code exists."""
        task = TaskContract(
            task_id="TASK-VERIFY-TEST",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-04-SEO",
            objective="Verify Core Web Vitals target",
            scope="pakistan_commercial",
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["lcp_under_2_5s"],
        )

        # Attempting to mark VERIFIED with empty evidence must fail
        with self.assertRaises(ValueError):
            task.mark_verified({})

        # Valid: Marked VERIFIED with authentic empirical evidence
        task.mark_verified({"edge_lcp_seconds": 1.12, "edge_cls": 0.000, "probe_runs": 3})
        self.assertEqual(task.status, TaskStatus.VERIFIED)
        self.assertIn("verification", task.verification_evidence)

    def test_mark_blocked_external_dependency_and_deployment(self):
        """Section 18: Tests blocked external dependency and deployment transitions."""
        task = TaskContract(
            task_id="TASK-STATUS-TEST",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-05-GA4",
            objective="Test status transitions",
            scope="pakistan_commercial",
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["criteria_met"],
        )

        task.mark_blocked_external_dependency("CrUX API quota requires GCP API Key")
        self.assertEqual(task.status, TaskStatus.BLOCKED_EXTERNAL_DEPENDENCY)
        self.assertIn("CrUX API", task.error_message)

        task.mark_deployed({"deploy_url": "https://aitoolgems.tech/", "git_commit": "e306efd3"})
        self.assertEqual(task.status, TaskStatus.DEPLOYED)
        self.assertEqual(task.verification_evidence["deployment"]["git_commit"], "e306efd3")


if __name__ == "__main__":
    unittest.main()
