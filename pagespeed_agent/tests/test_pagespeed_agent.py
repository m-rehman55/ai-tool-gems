"""Unit tests for PageSpeed & Core Web Vitals Agent (AGENT-07)."""

import unittest
from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus
from pagespeed_agent.client import (
    FieldExperience,
    LabDiagnostics,
    PageSpeedAuditResult,
    PageSpeedClient,
)
from pagespeed_agent.hermes_integration import PageSpeedHermesAgent
from pagespeed_agent.regression_detector import detect_regressions
from pagespeed_agent.representative_urls import get_representative_urls
from pagespeed_agent.thresholds import Rating, classify_metric


class TestPageSpeedAgent(unittest.TestCase):
    def test_cwv_classification_thresholds(self):
        # LCP: Good <= 2500ms, Needs <= 4000ms, Poor > 4000ms
        self.assertEqual(classify_metric("lcp", 1200.0), Rating.GOOD)
        self.assertEqual(classify_metric("lcp", 2500.0), Rating.GOOD)
        self.assertEqual(classify_metric("lcp", 3200.0), Rating.NEEDS_IMPROVEMENT)
        self.assertEqual(classify_metric("lcp", 4500.0), Rating.POOR)

        # CLS: Good <= 0.10, Needs <= 0.25, Poor > 0.25
        self.assertEqual(classify_metric("cls", 0.02), Rating.GOOD)
        self.assertEqual(classify_metric("cls", 0.15), Rating.NEEDS_IMPROVEMENT)
        self.assertEqual(classify_metric("cls", 0.35), Rating.POOR)

        # INP: Good <= 200ms, Needs <= 500ms, Poor > 500ms
        self.assertEqual(classify_metric("inp", 80.0), Rating.GOOD)
        self.assertEqual(classify_metric("inp", 350.0), Rating.NEEDS_IMPROVEMENT)
        self.assertEqual(classify_metric("inp", 600.0), Rating.POOR)

        # TBT: Good <= 200ms, Needs <= 600ms, Poor > 600ms
        self.assertEqual(classify_metric("tbt", 50.0), Rating.GOOD)
        self.assertEqual(classify_metric("tbt", 400.0), Rating.NEEDS_IMPROVEMENT)
        self.assertEqual(classify_metric("tbt", 800.0), Rating.POOR)

    def test_lab_vs_field_separation(self):
        field_exp = FieldExperience(
            has_data=True,
            lcp_ms=2200.0,
            lcp_rating=Rating.GOOD,
            inp_ms=150.0,
            inp_rating=Rating.GOOD,
            cls=0.04,
            cls_rating=Rating.GOOD,
        )
        lab_diag = LabDiagnostics(
            performance_score=99.0,
            lcp_ms=1100.0,
            lcp_rating=Rating.GOOD,
            tbt_ms=30.0,
            tbt_rating=Rating.GOOD,
            cls=0.01,
            cls_rating=Rating.GOOD,
            fcp_ms=750.0,
            fcp_rating=Rating.GOOD,
            speed_index_ms=1200.0,
            speed_index_rating=Rating.GOOD,
            ttfb_ms=210.0,
            ttfb_rating=Rating.GOOD,
        )
        result = PageSpeedAuditResult(
            url="https://aitoolgems.tech/",
            strategy="mobile",
            timestamp=1700000000.0,
            data_source="TEST_SEPARATION",
            field_data=field_exp,
            lab_data=lab_diag,
        )
        d = result.to_dict()
        # Verify lab and field are in completely separate dictionaries
        self.assertIn("field_data", d)
        self.assertIn("lab_data", d)
        self.assertEqual(d["field_data"]["lcp_ms"], 2200.0)
        self.assertEqual(d["lab_data"]["lcp_ms"], 1100.0)

    def test_regression_detector_identifies_degradation(self):
        baseline = PageSpeedAuditResult(
            url="https://aitoolgems.tech/",
            strategy="mobile",
            timestamp=1700000000.0,
            data_source="BASELINE",
            field_data=FieldExperience(has_data=False),
            lab_data=LabDiagnostics(
                performance_score=98.0,
                lcp_ms=1500.0,
                lcp_rating=Rating.GOOD,
                tbt_ms=50.0,
                tbt_rating=Rating.GOOD,
                cls=0.01,
                cls_rating=Rating.GOOD,
                fcp_ms=800.0,
                fcp_rating=Rating.GOOD,
                speed_index_ms=1400.0,
                speed_index_rating=Rating.GOOD,
                ttfb_ms=250.0,
                ttfb_rating=Rating.GOOD,
            ),
        )

        regressed = PageSpeedAuditResult(
            url="https://aitoolgems.tech/",
            strategy="mobile",
            timestamp=1700001000.0,
            data_source="DEGRADED",
            field_data=FieldExperience(has_data=False),
            lab_data=LabDiagnostics(
                performance_score=75.0,  # Dropped 23 points!
                lcp_ms=3800.0,          # Degraded by 2300ms!
                lcp_rating=Rating.NEEDS_IMPROVEMENT,
                tbt_ms=450.0,           # Degraded by 400ms!
                tbt_rating=Rating.NEEDS_IMPROVEMENT,
                cls=0.18,               # Degraded by 0.17!
                cls_rating=Rating.NEEDS_IMPROVEMENT,
                fcp_ms=1900.0,
                fcp_rating=Rating.NEEDS_IMPROVEMENT,
                speed_index_ms=3500.0,
                speed_index_rating=Rating.NEEDS_IMPROVEMENT,
                ttfb_ms=500.0,
                ttfb_rating=Rating.GOOD,
            ),
        )

        evaluation = detect_regressions(regressed, baseline)
        self.assertTrue(evaluation.has_regressions)
        metrics_flagged = [inc.metric for inc in evaluation.incidents]
        self.assertIn("performance_score", metrics_flagged)
        self.assertIn("lcp_ms", metrics_flagged)
        self.assertIn("cls", metrics_flagged)
        self.assertIn("tbt_ms", metrics_flagged)

    def test_representative_urls_defined(self):
        urls = get_representative_urls()
        self.assertGreaterEqual(len(urls), 4)
        self.assertIn("https://aitoolgems.tech/", urls)
        self.assertIn("https://aitoolgems.tech/tools/chatgpt/", urls)

    def test_client_fallback_on_unconfigured_or_ratelimited(self):
        client = PageSpeedClient(api_key="invalid_test_key")
        result = client.audit_url("https://aitoolgems.tech/", strategy="mobile")
        self.assertEqual(result.url, "https://aitoolgems.tech/")
        self.assertEqual(result.strategy, "mobile")
        self.assertTrue(result.lab_data.performance_score > 0)
        self.assertIn("BASELINE", result.data_source)

    def test_hermes_integration_tasks(self):
        agent = PageSpeedHermesAgent()
        task = TaskContract(
            task_id="TEST-PS-01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-07-PAGESPEED",
            objective="Audit representative site performance and check for regressions",
            scope="Performance",
            input_evidence={"url": "https://aitoolgems.tech/", "strategy": "mobile"},
            required_tools=["pagespeed_client"],
            expected_output={"audit": "dict"},
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid PageSpeed audit report"],
        )
        completed = agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("performance_score", completed.verification_evidence)
        self.assertGreaterEqual(completed.verification_evidence["performance_score"], 80.0)


if __name__ == "__main__":
    unittest.main()
