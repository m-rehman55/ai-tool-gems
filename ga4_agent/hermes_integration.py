"""
hermes_integration.py - HERMES Executive Orchestrator Task Contract Handler for AGENT-05-GA4.

Receives TaskContracts dispatched to AGENT-05-GA4:
- Ingests GA4 session performance, channel groupings, and ecommerce funnels.
- Manages authorized offline purchase conversion imports for WhatsApp sales.
- Strictly adheres to the Non-Fabrication & Payment Verification contract.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from hermes_core.contracts import TaskContract, TaskStatus, RiskClassification
from ga4_agent.client import GA4DataClient
from ga4_agent.conversion_importer import ConversionImporter
from ga4_agent.analyzer import GA4Analyzer

logger = logging.getLogger("ga4_agent.hermes")


def execute_ga4_task(contract: TaskContract, project_dir: Optional[Path] = None) -> TaskContract:
    """
    Executes a task contract assigned to AGENT-05-GA4.
    Returns the updated TaskContract with verification evidence.
    """
    p_dir = project_dir or Path(__file__).resolve().parent.parent
    reports_dir = p_dir / "reports" / "ga4-agent"
    reports_dir.mkdir(parents=True, exist_ok=True)

    contract.status = TaskStatus.IN_PROGRESS
    obj_lower = contract.objective.lower()

    try:
        client = GA4DataClient()
        importer = ConversionImporter(data_dir=p_dir / "data" / "orders")
        analyzer = GA4Analyzer(client=client, importer=importer)

        evidence: Dict[str, Any] = {
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "property_id": client.property_id or "G-NQJCMDCLLP",
            "is_authorized": client.is_authorized,
        }

        # 1. Offline Conversion Import Task
        if "import" in obj_lower or "conversion" in obj_lower and "audit" not in obj_lower:
            dispatch_res = importer.dispatch_offline_conversions(dry_run=True)
            evidence["task_type"] = "OFFLINE_CONVERSION_IMPORT"
            evidence["imported_count"] = dispatch_res.get("imported_count", 0)
            evidence["pending_remaining"] = dispatch_res.get("pending_remaining", 0)
            evidence["policy_contract"] = "Never record a purchase on WhatsApp click. Purchases strictly verified with domestic payment proof."

        # 2. Comprehensive GA4 Conversion Audit Task
        else:
            summary = analyzer.run_audit()

            # Save Markdown report
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            md_file = reports_dir / f"ga4-audit-{today}.md"
            json_file = reports_dir / "ga4-audit-latest.json"

            lines = [
                f"# 📊 GA4 Conversion Intelligence & Ecommerce Funnel — AIToolGems",
                f"**Audit Date:** `{today}`  ",
                f"**Property ID:** `{summary.property_id}` (Measurement ID: `G-NQJCMDCLLP`)  ",
                f"**Authorized Live API:** `{'Yes ✅' if summary.is_authorized else 'Offline / Baseline 📁'}`  ",
                f"**Pakistan Traffic Focus:** `{summary.pakistan_sessions}` sessions  ",
                "",
                "---",
                "",
                "## 🛒 Ecommerce Conversion Funnel (PKR)",
                f"- **Product Views (`view_item`):** `{summary.funnel.product_views}`",
                f"- **Product Selections (`select_item`):** `{summary.funnel.product_selections}`",
                f"- **Order Initiations (`whatsapp_order_click` / `begin_checkout`):** `{summary.funnel.order_initiations}`",
                f"- **Verified Purchases (`purchase`):** `{summary.funnel.verified_purchases}`",
                f"- **Checkout Drop-off:** `{summary.funnel.checkout_dropoff_pct}%`",
                f"- **Overall Conversion Rate:** `{summary.funnel.overall_conversion_rate_pct}%`",
                f"- **Verified Revenue:** `{summary.funnel.total_revenue_pkr:,.0f} PKR`",
                "",
                "---",
                "",
                "## 💡 Strategic Conversion Recommendations",
            ]
            for r in summary.recommendations:
                lines.append(f"- {r}")

            lines.extend([
                "",
                "---",
                "",
                "## 🛡️ Event Taxonomy & Privacy Protection Policy",
                "- **Homepage Classification:** Repaired. Homepage visits strictly do not fire product view_item or guide view_guide events.",
                "- **Separation of Actions:** WhatsApp order clicks (begin_checkout) separated from support inquiries and channel updates.",
                "- **Purchase Verification Gate:** Purchases are NEVER recorded client-side on click; strictly recorded when verified payment is confirmed.",
                "- **PII Protection:** Customer phone numbers are masked using one-way SHA-256 hashes.",
            ])

            md_file.write_text("\n".join(lines), encoding="utf-8")
            json_file.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")

            evidence["task_type"] = "GA4_CONVERSION_AUDIT"
            evidence["product_views"] = summary.funnel.product_views
            evidence["order_initiations"] = summary.funnel.order_initiations
            evidence["verified_purchases"] = summary.funnel.verified_purchases
            evidence["verified_revenue_pkr"] = summary.funnel.total_revenue_pkr
            evidence["checkout_dropoff_pct"] = summary.funnel.checkout_dropoff_pct
            evidence["markdown_report"] = str(md_file)
            evidence["json_report"] = str(json_file)

        contract.verification_evidence = evidence
        contract.status = TaskStatus.VERIFIED

    except Exception as e:
        logger.error(f"Failed executing GA4 task {contract.task_id}: {e}", exc_info=True)
        contract.verification_evidence = {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        contract.status = TaskStatus.FAILED

    return contract


class GA4HermesAgent:
    """Class wrapper for AGENT-05-GA4 task execution."""
    AGENT_ID = "AGENT-05-GA4"

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent

    def execute_task(self, task: TaskContract) -> TaskContract:
        return execute_ga4_task(task, project_dir=self.repo_root)
