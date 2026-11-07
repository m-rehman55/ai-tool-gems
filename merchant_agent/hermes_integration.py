"""HERMES-CEO Orchestrator Integration for Google Merchant Center Agent (AGENT-13)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus
from merchant_agent.client import GoogleMerchantClient
from merchant_agent.feed_generator import MerchantFeedGenerator
from merchant_agent.validator import MerchantValidator


class MerchantHermesAgent:
    """Agent 13 implementation for HERMES Omniscient."""

    AGENT_ID = "AGENT-13-MERCHANT"

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path(".")
        self.feed_generator = MerchantFeedGenerator(self.project_dir)
        self.validator = MerchantValidator(self.project_dir)
        self.client = GoogleMerchantClient()

    def execute_task(self, task: TaskContract) -> TaskContract:
        task.status = TaskStatus.IN_PROGRESS
        obj_lower = task.objective.lower()

        try:
            if "generate" in obj_lower or "feed" in obj_lower:
                return self._run_feed_generation(task)
            elif "parity" in obj_lower or "schema" in obj_lower:
                return self._run_schema_parity(task)
            else:
                return self._run_feed_health_audit(task)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence["error"] = str(e)
            return task

    def _run_feed_generation(self, task: TaskContract) -> TaskContract:
        # Strictly enforce eligibility gate: do not submit every catalogue item to Merchant Center
        items = self.feed_generator.extract_catalog_items(eligible_only=True)
        xml_path = self.feed_generator.generate_xml_feed(items)
        tsv_path = self.feed_generator.generate_tsv_feed(items)
        hold_path, ads_path = self.feed_generator.export_eligibility_registers()

        task.actual_output = {
            "eligible_items_count": len(items),
            "xml_feed_path": str(xml_path),
            "tsv_feed_path": str(tsv_path),
            "hold_register_path": str(hold_path),
            "ads_matrix_path": str(ads_path),
            "currency": "PKR",
            "country": "PK",
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "products_in_feed": len(items),
            "xml_exists": xml_path.exists(),
            "tsv_exists": tsv_path.exists(),
            "timestamp": time.time(),
        }
        return task

    def _run_schema_parity(self, task: TaskContract) -> TaskContract:
        items = self.feed_generator.extract_catalog_items(eligible_only=False)
        report = self.validator.validate_feed_items(items)

        task.actual_output = {
            "validation_report": report.to_dict(),
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "checked_products": report.total_products_checked,
            "issues_count": len(report.issues),
            "digital_warranty_verified": report.digital_warranty_verified,
            "timestamp": time.time(),
        }
        return task

    def _run_feed_health_audit(self, task: TaskContract) -> TaskContract:
        items = self.feed_generator.extract_catalog_items()
        xml_path = self.feed_generator.generate_xml_feed(items)
        report = self.validator.validate_feed_items(items)
        acct_status = self.client.get_account_status()

        task.actual_output = {
            "agent": self.AGENT_ID,
            "merchant_account": acct_status,
            "products_feed_items": len(items),
            "xml_feed": str(xml_path),
            "validation_summary": report.summary,
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "products_feed_items": len(items),
            "account_configured": acct_status.get("status") == "AUTHENTICATED",
            "timestamp": time.time(),
        }
        return task

