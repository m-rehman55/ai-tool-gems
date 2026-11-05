"""
Unit and Integration Tests for HERMES Core Executive Framework
--------------------------------------------------------------
Tests TaskContract lifecycle, TaskRegistry dependency graph,
duplicate task detection, conflict resolution, and evidence validation.
"""

import json
import unittest
import tempfile
import shutil
from pathlib import Path

from hermes_core.contracts import (
    TaskContract,
    TaskStatus,
    RiskClassification,
    ApprovalRequirement,
    TaskRegistry,
)
from hermes_core.orchestrator import HermesCEO


class TestHermesCoreContracts(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.registry_file = Path(self.test_dir) / "registry.json"
        self.ceo = HermesCEO(base_dir=self.test_dir, registry_path=self.registry_file)
        self.registry = self.ceo.registry

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_task_contract_serialization_and_deserialization(self):
        task = self.registry.create_task(
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-01-GSC",
            objective="Query Pakistan Search Analytics",
            scope="https://aitoolgems.tech/",
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Retrieve 28d Pakistan query dataset", "Extract CTR opportunities"],
            expected_output="JSON performance dataset"
        )
        self.assertTrue(task.task_id.startswith("TASK-01"))
        self.assertEqual(task.status, TaskStatus.NOT_STARTED)

        # Reload from disk
        new_reg = TaskRegistry(storage_path=self.registry_file)
        loaded = new_reg.get_task(task.task_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.objective, "Query Pakistan Search Analytics")
        self.assertEqual(loaded.risk_classification, RiskClassification.READ_ONLY)

    def test_dependency_graph_validation(self):
        # Create Task A
        task_a = self.registry.create_task(
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-01-GSC",
            objective="Audit GSC",
            scope="site",
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Audit complete"],
        )
        # Create Task B depending on Task A
        task_b = self.registry.create_task(
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-09-EDITORIAL",
            objective="Generate Guide Patch",
            scope="guide",
            risk_classification=RiskClassification.MEDIUM_CODE,
            approval_requirement=ApprovalRequirement.PULL_REQUEST_REQUIRED,
            completion_criteria=["Patch generated"],
            dependencies=[task_a.task_id]
        )

        # Before Task A is verified, Task B cannot execute
        can_exec, reason = self.registry.can_execute(task_b.task_id)
        self.assertFalse(can_exec)
        self.assertIn("expected VERIFIED/DEPLOYED", reason)

        # Mark Task A verified
        task_a.mark_verified({"gsc_audit": "passed"})
        self.registry.save()

        can_exec_after, _ = self.registry.can_execute(task_b.task_id)
        self.assertTrue(can_exec_after)

    def test_duplicate_task_detection(self):
        t1 = self.ceo.delegate_task(
            responsible_agent="AGENT-01-GSC",
            objective="Extract High Imp Low CTR",
            scope="site",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["Extracted"]
        )
        # Delegate identical task
        t2 = self.ceo.delegate_task(
            responsible_agent="AGENT-01-GSC",
            objective="Extract High Imp Low CTR",
            scope="site",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["Extracted"]
        )
        self.assertEqual(t1.task_id, t2.task_id)

    def test_conflict_resolution_security_firewall_priority(self):
        task_code = self.registry.create_task(
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-09-EDITORIAL",
            objective="Publish Auto Article",
            scope="blog",
            risk_classification=RiskClassification.MEDIUM_CODE,
            approval_requirement=ApprovalRequirement.PULL_REQUEST_REQUIRED,
            completion_criteria=["HTML generated"],
        )
        task_sec = self.registry.create_task(
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-15-SECURITY",
            objective="Block Unauthorized Foreign Content",
            scope="blog",
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Firewall enforced"],
        )

        winner = self.ceo.resolve_conflicting_recommendations(task_code, task_sec)
        self.assertEqual(winner.task_id, task_sec.task_id)

    def test_independent_evidence_validation_rejects_missing_tests(self):
        task = self.registry.create_task(
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-09-EDITORIAL",
            objective="Modify Tool Pricing",
            scope="tools/chatgpt",
            risk_classification=RiskClassification.HIGH_COMMERCIAL,
            approval_requirement=ApprovalRequirement.HUMAN_EXPLICIT_REQUIRED,
            completion_criteria=["Update price", "Run tests"],
        )
        task.mark_implemented({"price": 2300})
        # Fails independent validation because test results are absent
        valid, msg = self.ceo.validate_task_evidence(task.task_id)
        self.assertFalse(valid)
        self.assertIn("Missing verified passing test artifact", msg)

        # Now attach passing test evidence
        task.mark_tested({"passed": True, "test_count": 50})
        valid_after, _ = self.ceo.validate_task_evidence(task.task_id)
        self.assertTrue(valid_after)


if __name__ == "__main__":
    unittest.main()
