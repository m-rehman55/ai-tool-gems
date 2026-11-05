"""Unit tests for PostHog Product & Behavioural Intelligence Agent (AGENT-06)."""

import json
import os
import unittest
from pathlib import Path

from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus
from posthog_agent.client import PostHogClient
from posthog_agent.events import (
    PostHogEvent,
    make_dead_click_event,
    make_pageview_event,
    make_product_view_event,
    make_rage_click_event,
    make_whatsapp_order_event,
)
from posthog_agent.funnels import analyze_ecom_funnel, validate_ab_experiment_policy
from posthog_agent.hermes_integration import PostHogHermesAgent
from posthog_agent.privacy import get_privacy_replay_config, sanitize_event_properties, sanitize_text


class TestPostHogAgent(unittest.TestCase):
    def test_privacy_masking_phone_and_email(self):
        text = "Contact customer at 0323-6715731 or user@example.com for order verification"
        sanitized = sanitize_text(text)
        self.assertNotIn("0323-6715731", sanitized)
        self.assertNotIn("user@example.com", sanitized)
        self.assertIn("[PHONE_REDACTED]", sanitized)
        self.assertIn("[EMAIL_REDACTED]", sanitized)

    def test_privacy_masking_sensitive_dict_keys(self):
        props = {
            "tool_id": "chatgpt-plus",
            "password": "supersecretpassword123",
            "otp_code": "987654",
            "customer_phone": "03001234567",
            "payment_receipt": "receipt_image_base64_data",
        }
        clean = sanitize_event_properties(props)
        self.assertEqual(clean["tool_id"], "chatgpt-plus")
        self.assertEqual(clean["password"], "[REDACTED_SENSITIVE_DATA]")
        self.assertEqual(clean["otp_code"], "[REDACTED_SENSITIVE_DATA]")
        self.assertEqual(clean["customer_phone"], "[REDACTED_SENSITIVE_DATA]")
        self.assertEqual(clean["payment_receipt"], "[REDACTED_SENSITIVE_DATA]")

    def test_privacy_replay_config(self):
        cfg = get_privacy_replay_config()
        self.assertTrue(cfg["mask_all_text"])
        self.assertTrue(cfg["mask_all_element_attributes"])
        self.assertIn("input", cfg["mask_custom_selectors"])
        self.assertIn(".pii-mask", cfg["mask_custom_selectors"])
        self.assertFalse(cfg["record_cross_origin_iframes"])

    def test_event_builders(self):
        pv = make_pageview_event("anon-123", "https://aitoolgems.tech/tools/chatgpt/", "ChatGPT Plus Pakistan")
        d_pv = pv.to_dict()
        self.assertEqual(d_pv["event"], "$pageview")
        self.assertEqual(d_pv["properties"]["currency"], "PKR")
        self.assertEqual(d_pv["properties"]["market"], "PK")

        rage = make_rage_click_event("anon-123", "button.order-btn", 5, 800, "https://aitoolgems.tech/")
        d_rage = rage.to_dict()
        self.assertEqual(d_rage["event"], "rage_click")
        self.assertEqual(d_rage["properties"]["click_count"], 5)

        dead = make_dead_click_event("anon-123", "div.fake-badge", "Instant Delivery", "https://aitoolgems.tech/")
        d_dead = dead.to_dict()
        self.assertEqual(d_dead["event"], "dead_click")

    def test_funnel_analysis_bottleneck(self):
        counts = {
            "landing_page": 1000,
            "product_view": 800,
            "product_selection": 200,  # 75% drop-off here
            "whatsapp_order": 50,
            "payment_confirmation": 25,
        }
        report = analyze_ecom_funnel(counts)
        self.assertEqual(report.total_starters, 1000)
        self.assertEqual(report.total_converters, 25)
        self.assertEqual(report.overall_conversion_pct, 2.5)
        self.assertEqual(len(report.steps), 5)
        self.assertEqual(report.bottleneck_step, "Product Selection")
        self.assertTrue(any("Product Selection" in d for d in report.diagnostics))

    def test_ab_experiment_safety_rules(self):
        # 1. Price discrimination rejected
        res1 = validate_ab_experiment_policy("Pricing Test", ["A", "B"], 1500, involves_pricing_diff=True)
        self.assertFalse(res1["is_safe"])
        self.assertEqual(res1["status"], "REJECTED")

        # 2. Insufficient sample size rejected
        res2 = validate_ab_experiment_policy("CTA Color", ["Blue", "Green"], 250)
        self.assertFalse(res2["is_safe"])
        self.assertTrue(any("INSUFFICIENT_POWER" in v for v in res2["violations"]))

        # 3. Valid experiment approved
        res3 = validate_ab_experiment_policy("Hero Layout Test", ["A", "B"], 2000)
        self.assertTrue(res3["is_safe"])
        self.assertEqual(res3["status"], "APPROVED")

    def test_client_unconfigured_offline_queue(self):
        # Client without API key queues offline
        client = PostHogClient(api_key="")
        status = client.get_auth_status()
        self.assertEqual(status["status"], "BLOCKED_PENDING_CREDENTIALS")
        self.assertFalse(status["configured"])

        event = make_pageview_event("test-usr", "https://aitoolgems.tech/", "Home")
        res = client.capture_event(event)
        self.assertEqual(res["status"], "QUEUED_OFFLINE")
        self.assertTrue(client.offline_events_path.exists())

    def test_hermes_integration_tasks(self):
        agent = PostHogHermesAgent()
        task = TaskContract(
            task_id="TEST-PH-01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-06-POSTHOG",
            objective="Run conversion funnel and drop-off analysis",
            scope="Website Funnel",
            input_evidence={},
            required_tools=["posthog_client"],
            expected_output={"funnel": "dict"},
            risk_classification=RiskClassification.LOW_REVERSIBLE,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid funnel report"],
        )
        completed = agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("funnel", completed.actual_output)
        self.assertGreaterEqual(completed.verification_evidence["conversion_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
