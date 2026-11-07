"""
Unit tests for Section 19 Definition of Done (DoD).
Validates all 13 universal completion conditions and the 4 task-type specific invariants:
- Research tasks (source URLs + timestamps)
- Code tasks (changed files + test results + diff summary + rollback instructions)
- Release tasks (CI + configuration + deployment + post-deployment evidence)
- Catalogue tasks (factual evidence + commercial classification + publication state)
"""

import unittest
from hermes_core.contracts import (
    ApprovalRequirement,
    DefinitionOfDoneValidator,
    DefinitionOfDoneViolation,
    RiskClassification,
    TaskContract,
    TaskStatus,
    TaskType,
)


class TestDefinitionOfDone(unittest.TestCase):

    def _create_base_valid_task(self) -> TaskContract:
        """Helper creating a task satisfying all 13 universal DoD criteria."""
        return TaskContract(
            task_id="TASK-DOD-BASE-001",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-04-SEO",
            objective="Deliver verified Core Web Vitals speed audit",
            scope="pakistan_commercial",
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["audit_10_pages", "verify_cwv_thresholds"],
            expected_output="reports/performance_reliability_and_quality_audit.md",
            status=TaskStatus.VERIFIED,
            verification_evidence={
                "test_command": "python -m unittest tests/test_phase_i_performance_and_quality.py",
                "exit_code": 0,
                "tests_run": 7,
                "regressions_considered": "No regressions detected in bundle sizes or layout stability.",
                "security_and_privacy_checked": True,
                "remaining_risks": "CrUX field data requires 28-day Chrome user accumulation; lab probes verified.",
            }
        )

    def test_universal_thirteen_conditions_pass_on_valid_task(self):
        """DoD Universal: Verifies complete task satisfies all 13 universal criteria."""
        task = self._create_base_valid_task()
        self.assertTrue(task.validate_definition_of_done(TaskType.GENERAL))

    def test_universal_conditions_fail_closed_on_missing_fields(self):
        """DoD Universal: Fails closed when test command, exit code, or remaining risks missing."""
        task = self._create_base_valid_task()
        # Remove test command & exit code
        task.verification_evidence.pop("test_command")
        task.verification_evidence.pop("exit_code")

        with self.assertRaises(DefinitionOfDoneViolation) as ctx:
            task.validate_definition_of_done(TaskType.GENERAL)
        self.assertIn("Test commands and actual exit codes are not recorded", str(ctx.exception))

    def test_research_task_requires_urls_and_timestamps(self):
        """DoD Task-Type: Research tasks must include official source URLs and verification timestamps."""
        task = self._create_base_valid_task()

        # Missing research requirements
        with self.assertRaises(DefinitionOfDoneViolation) as ctx:
            task.validate_definition_of_done(TaskType.RESEARCH)
        self.assertIn("RESEARCH: Missing official source URLs", str(ctx.exception))

        # Supply research requirements
        task.verification_evidence.update({
            "source_urls": ["https://openai.com/chatgpt/pricing", "https://anthropic.com/pricing"],
            "verification_timestamp": "2026-11-07T05:00:00Z"
        })
        self.assertTrue(task.validate_definition_of_done(TaskType.RESEARCH))

    def test_code_task_requires_files_tests_diff_and_rollback(self):
        """DoD Task-Type: Code tasks must include changed files, test results, diff summary, and rollback instructions."""
        task = self._create_base_valid_task()

        # Missing code requirements
        with self.assertRaises(DefinitionOfDoneViolation) as ctx:
            task.validate_definition_of_done(TaskType.CODE)
        self.assertIn("CODE: Missing list of changed files", str(ctx.exception))

        # Supply code requirements
        task.verification_evidence.update({
            "changed_files": ["attribution.js", "ga4_agent/tests/test_ga4_agent.py"],
            "test_results": {"passed": 33, "failed": 0, "errors": 0},
            "diff_summary": "Added detectReferrer() supporting ChatGPT, Perplexity, Claude, Gemini, Copilot.",
            "rollback_instructions": "git revert <commit-sha> and redeploy static assets."
        })
        self.assertTrue(task.validate_definition_of_done(TaskType.CODE))

    def test_release_task_requires_ci_config_deploy_and_postdeploy(self):
        """DoD Task-Type: Release tasks must include CI, configuration, deployment, and post-deployment evidence."""
        task = self._create_base_valid_task()

        # Missing release requirements
        with self.assertRaises(DefinitionOfDoneViolation) as ctx:
            task.validate_definition_of_done(TaskType.RELEASE)
        self.assertIn("RELEASE: Missing CI evidence", str(ctx.exception))

        # Supply release requirements
        task.verification_evidence.update({
            "ci_status": "GitHub Actions Run #142 (Status: SUCCESS, Exit Code: 0)",
            "configuration": "Fastly CDN + GitHub Pages with CNAME aitoolgems.tech",
            "deployment": "SHA 7265eece deployed to gh-pages branch",
            "post_deployment_evidence": "HTTP 200 confirmed on https://aitoolgems.tech/ with TTFB 186.3ms."
        })
        self.assertTrue(task.validate_definition_of_done(TaskType.RELEASE))

    def test_catalogue_task_requires_factual_evidence_commercial_tier_and_state(self):
        """DoD Task-Type: Catalogue tasks must include factual evidence, commercial classification, and publication state."""
        task = self._create_base_valid_task()

        # Missing catalogue requirements
        with self.assertRaises(DefinitionOfDoneViolation) as ctx:
            task.validate_definition_of_done(TaskType.CATALOGUE)
        self.assertIn("CATALOGUE: Missing factual evidence", str(ctx.exception))

        # Supply catalogue requirements
        task.verification_evidence.update({
            "factual_evidence": "Verified official developer organization, product URL, and USD plan tiers.",
            "commercial_classification": "TIER_A_OUTBOUND_DIRECTORY_REFERENCE",
            "publication_state": "STAGED_LOCAL_DRAFT_PENDING_OWNER_PR"
        })
        self.assertTrue(task.validate_definition_of_done(TaskType.CATALOGUE))


if __name__ == "__main__":
    unittest.main()
