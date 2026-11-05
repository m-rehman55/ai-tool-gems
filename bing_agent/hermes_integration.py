"""
hermes_integration.py - HERMES Executive Orchestrator Task Contract Handler for AGENT-04-BING.

Receives TaskContracts dispatched to AGENT-04-BING:
- Ingests empirical Bing Webmaster Tools API metrics.
- Manages delta-diffed IndexNow queue submissions.
- Produces cross-engine diagnostics for HERMES-CEO, Technical SEO, and Keyword agents.
- Strictly adheres to the Non-Fabrication & Google Exclusion policy.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from hermes_core.contracts import TaskContract, TaskStatus, RiskClassification
from bing_agent.client import BingWebmasterClient
from bing_agent.indexnow_queue import IndexNowQueueEngine
from bing_agent.analyzer import BingWebmasterAnalyzer

logger = logging.getLogger("bing_agent.hermes")


def execute_bing_task(contract: TaskContract, project_dir: Optional[Path] = None) -> TaskContract:
    """
    Executes a task contract assigned to AGENT-04-BING.
    Returns the updated TaskContract with verification evidence.
    """
    p_dir = project_dir or Path(__file__).resolve().parent.parent
    reports_dir = p_dir / "reports" / "bing-agent"
    reports_dir.mkdir(parents=True, exist_ok=True)

    contract.status = TaskStatus.IN_PROGRESS
    obj_lower = contract.objective.lower()

    try:
        client = BingWebmasterClient()
        queue_engine = IndexNowQueueEngine(project_dir=p_dir)
        analyzer = BingWebmasterAnalyzer(client=client)

        evidence: Dict[str, Any] = {
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "is_authorized": client.is_authorized,
            "site_url": client.default_site_url,
        }

        # 1. Delta IndexNow Dispatch Task
        if ("indexnow" in obj_lower or "delta" in obj_lower or "submit" in obj_lower) and "audit" not in obj_lower:
            deltas = queue_engine.detect_deltas()
            records = queue_engine.dispatch_pending(dry_run=False, batch_limit=50)

            evidence["task_type"] = "INDEXNOW_DELTA_DISPATCH"
            evidence["deltas_detected"] = len(deltas)
            evidence["submissions_count"] = len(records)
            evidence["accepted_count"] = sum(1 for r in records if r.is_accepted)
            evidence["policy_contract"] = "Google excluded from IndexNow protocol. Submissions strictly notify Bing, Yandex, Seznam, and Naver."

        # 2. Comprehensive Bing Webmaster Audit Task
        else:
            summary = analyzer.run_audit()

            # Save Markdown report
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            md_file = reports_dir / f"bing-audit-{today}.md"
            json_file = reports_dir / "bing-audit-latest.json"

            lines = [
                f"# 🌐 Bing Webmaster Tools & IndexNow Intelligence — AIToolGems",
                f"**Audit Date:** `{today}`  ",
                f"**Target Site:** `{summary.site_url}`  ",
                f"**Bing Verified Property:** `{'Yes ✅' if summary.is_verified else 'No ❌'}`  ",
                f"**IndexNow Daily Quota:** `{summary.daily_quota}` (Monthly: `{summary.monthly_quota}`)  ",
                f"**Pages in Bing Index:** `{summary.current_pages_in_index}`  ",
                f"**Tracked Bing Queries:** `{summary.total_bing_queries}` (Imp: `{summary.total_bing_impressions}`, Clicks: `{summary.total_bing_clicks}`, Avg Pos: `{summary.average_bing_position}`)  ",
                "",
                "---",
                "",
                "## 🏆 Top Bing Empirical Queries (Pakistan & Commercial Focus)",
                "| Query | Bing Imp | Bing Clicks | Bing Pos | Opportunity Type | Strategic Recommendation |",
                "|---|---|---|---|---|---|",
            ]

            for q in summary.cross_engine_insights[:15]:
                lines.append(f"| `{q.query}` | {q.bing_impressions} | {q.bing_clicks} | {q.bing_position:.1f} | `{q.opportunity_type}` | {q.recommendation} |")

            lines.extend([
                "",
                "---",
                "",
                "## 💡 Actionable Strategic Recommendations",
            ])
            for r in summary.recommendations:
                lines.append(f"- {r}")

            lines.extend([
                "",
                "---",
                "",
                "## 🛡️ Operating Integrity & Governance Policy",
                "- **Non-Fabrication:** All metrics pulled directly from authenticated Bing Webmaster Tools API.",
                "- **IndexNow Policy:** Submissions inform Bing, Yandex, Seznam, and Naver. Google does not participate in IndexNow.",
                "- **Acceptance vs Indexing:** HTTP 200/202 confirms endpoint queuing only, not guaranteed indexing.",
            ])

            md_file.write_text("\n".join(lines), encoding="utf-8")
            json_file.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")

            evidence["task_type"] = "BING_WEBMASTER_AUDIT"
            evidence["is_verified"] = summary.is_verified
            evidence["pages_in_index"] = summary.current_pages_in_index
            evidence["total_queries"] = summary.total_bing_queries
            evidence["total_impressions"] = summary.total_bing_impressions
            evidence["markdown_report"] = str(md_file)
            evidence["json_report"] = str(json_file)

        contract.verification_evidence = evidence
        contract.status = TaskStatus.VERIFIED

    except Exception as e:
        logger.error(f"Failed executing Bing task {contract.task_id}: {e}", exc_info=True)
        contract.verification_evidence = {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        contract.status = TaskStatus.FAILED

    return contract


class BingHermesAgent:
    """Class wrapper for AGENT-04-BING task execution."""
    AGENT_ID = "AGENT-04-BING"

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent

    def execute_task(self, task: TaskContract) -> TaskContract:
        return execute_bing_task(task, project_dir=self.repo_root)
