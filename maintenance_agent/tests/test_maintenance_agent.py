"""
Unit Tests for HERMES Operational Maintenance Agent (Phase K)
------------------------------------------------------------
Validates monitor registry, 15 continuous operational monitors,
the 8 mandatory monitor attributes, and the strict Rule K read-only invariant.
"""

import unittest
from pathlib import Path

from maintenance_agent.monitors import (
    MonitorRegistry,
    MonitorDefinition,
    MonitorFrequency,
    ActionNature,
    MonitorStatus
)
from maintenance_agent.executor import MaintenanceExecutor


class TestMaintenanceAgent(unittest.TestCase):

    def setUp(self):
        self.registry = MonitorRegistry()
        self.executor = MaintenanceExecutor()

    def test_all_fifteen_monitors_registered(self):
        """Phase K: Verifies exactly 15 operational monitors are registered."""
        monitors = self.registry.all_monitors()
        self.assertEqual(len(monitors), 15)

        expected_ids = {
            "MON-01-PRICING",
            "MON-02-DISCONTINUATION",
            "MON-03-FEATURES",
            "MON-04-URL-REDIRECTS",
            "MON-05-TERMS",
            "MON-06-REGIONAL-AVAILABILITY",
            "MON-07-BROKEN-LINKS",
            "MON-08-SITEMAP-INDEXING",
            "MON-09-SCHEMA",
            "MON-10-PERFORMANCE",
            "MON-11-SEARCH-CONSOLE",
            "MON-12-ANALYTICS-INGESTION",
            "MON-13-PROVIDER-APIS",
            "MON-14-SECURITY-ALERTS",
            "MON-15-PR-CI-FAILURES",
        }
        actual_ids = {m.id for m in monitors}
        self.assertEqual(actual_ids, expected_ids)

    def test_all_monitors_possess_eight_mandatory_attributes(self):
        """Phase K: Every automated monitor must specify all 8 core fields."""
        for m in self.registry.all_monitors():
            # 1. What it checks
            self.assertTrue(bool(m.what_it_checks), f"Missing what_it_checks in {m.id}")
            self.assertGreater(len(m.what_it_checks), 20)

            # 2. Frequency
            self.assertIsInstance(m.frequency, MonitorFrequency, f"Invalid frequency in {m.id}")

            # 3. Evidence source
            self.assertTrue(bool(m.evidence_source), f"Missing evidence_source in {m.id}")

            # 4. Change threshold
            self.assertTrue(bool(m.change_threshold), f"Missing change_threshold in {m.id}")

            # 5. False-positive handling
            self.assertTrue(bool(m.false_positive_handling), f"Missing false_positive_handling in {m.id}")

            # 6. Notification destination
            self.assertTrue(bool(m.notification_destination), f"Missing notification_destination in {m.id}")

            # 7. Required owner action
            self.assertTrue(bool(m.required_owner_action), f"Missing required_owner_action in {m.id}")

            # 8. Whether action is read-only or changes production
            self.assertIn(m.action_nature, (ActionNature.READ_ONLY_AUDIT, ActionNature.READ_ONLY_ALERT))

    def test_rule_k_read_only_invariant(self):
        """Rule K: Monitoring must not automatically change prices, publish content, alter indexing or deploy code."""
        for m in self.registry.all_monitors():
            # Invariant: action_nature must be READ_ONLY
            self.assertTrue(m.action_nature.value.startswith("READ_ONLY_"), f"Monitor {m.id} is not read-only: {m.action_nature}")
            # Ensure required action documents human review / PR workflow rather than silent automation
            action_text = m.required_owner_action.lower()
            self.assertTrue(
                "pr" in action_text or "review" in action_text or "verify" in action_text or "update" in action_text or "fix" in action_text,
                f"Action text in {m.id} does not require human/governed review: {m.required_owner_action}"
            )

    def test_manual_alternative_sops_provided(self):
        """Phase K: Where scheduled automation is unavailable or limited, provide a practical manual alternative SOP."""
        for m in self.registry.all_monitors():
            self.assertTrue(bool(m.manual_alternative_sop), f"Monitor {m.id} lacks manual_alternative_sop")
            self.assertTrue(m.manual_alternative_sop.startswith("Manual SOP-"), f"Invalid SOP format in {m.id}")

    def test_regional_availability_limitation_documented(self):
        """Phase K: Cloud runners cannot simulate local Pakistani ISP networks; limitation must be documented."""
        mon_06 = self.registry.get("MON-06-REGIONAL-AVAILABILITY")
        self.assertIsNotNone(mon_06)
        self.assertFalse(mon_06.is_automated)
        self.assertIn("Nayatel/PTCL", mon_06.manual_alternative_sop)

    def test_executor_audit_run_and_report_generation(self):
        """Phase K: Tests complete executor run across all 15 monitors."""
        results = self.executor.run_all()
        self.assertEqual(len(results), 15)

        for r in results:
            self.assertTrue(r.is_read_only)
            self.assertIn(r.status, (MonitorStatus.PASS, MonitorStatus.WARN, MonitorStatus.FAIL, MonitorStatus.MANUAL_FALLBACK_REQUIRED))

        report = self.executor.generate_report(results)
        self.assertEqual(report["monitors_total"], 15)
        self.assertEqual(report["rule_k_invariant_enforced"], True)
        self.assertEqual(report["read_only_mode"], True)
        self.assertIn("report_id", report)

    def test_executor_individual_monitor_execution(self):
        """Phase K: Tests executing specific monitors by ID."""
        pricing_res = self.executor.run_monitor("MON-01-PRICING")
        self.assertEqual(pricing_res.monitor_id, "MON-01-PRICING")
        self.assertEqual(pricing_res.status, MonitorStatus.PASS)
        self.assertTrue(pricing_res.is_read_only)

        link_res = self.executor.run_monitor("MON-07-BROKEN-LINKS")
        self.assertEqual(link_res.monitor_id, "MON-07-BROKEN-LINKS")
        self.assertEqual(link_res.status, MonitorStatus.PASS)
        self.assertTrue(link_res.is_read_only)

    def test_invalid_mutating_monitor_rejected(self):
        """Phase K: Enforces that registering a non-read-only monitor raises AssertionError."""
        with self.assertRaises(AssertionError):
            bad_monitor = MonitorDefinition(
                id="MON-BAD-MUTATE",
                name="Illegal Mutating Monitor",
                what_it_checks="Mutates prices directly",
                frequency=MonitorFrequency.DAILY,
                evidence_source="None",
                change_threshold="Any",
                false_positive_handling="None",
                notification_destination="None",
                required_owner_action="None",
                action_nature="AUTOMATIC_PRODUCTION_MUTATION"  # type: ignore
            )
            self.registry.register(bad_monitor)


if __name__ == "__main__":
    unittest.main()
