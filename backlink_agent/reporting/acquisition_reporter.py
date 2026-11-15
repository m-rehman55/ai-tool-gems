"""Acquisition Performance and Outcome Intelligence Reporter."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backlink_agent.lifecycle.models import LifecycleState
from backlink_agent.lifecycle.store import LocalSQLiteLifecycleStore

logger = logging.getLogger(__name__)

DEFAULT_REPORTS_DIR = Path("seo-agent/reports/backlinks")


class AcquisitionReporter:
    """Compiles evidence-based acquisition lifecycle, retention, and conversion velocity reports."""

    def __init__(
        self,
        lifecycle_store: Optional[LocalSQLiteLifecycleStore] = None,
        reports_dir: Path = DEFAULT_REPORTS_DIR,
    ):
        self.lifecycle_store = lifecycle_store or LocalSQLiteLifecycleStore()
        self.reports_dir = Path(reports_dir)

    def generate_acquisition_report(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        now_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        date_slug = now.strftime("%Y-%m-%d")

        funnel = self.lifecycle_store.get_lifecycle_funnel_counts()

        total_discovered = funnel.get(LifecycleState.DISCOVERED, 0)
        total_scored = funnel.get(LifecycleState.SCORED, 0)
        total_draft_ready = funnel.get(LifecycleState.DRAFT_READY, 0)
        total_owner_approved = funnel.get(LifecycleState.OWNER_APPROVED, 0)
        total_submitted = funnel.get(LifecycleState.MANUALLY_SUBMITTED, 0)
        total_published = funnel.get(LifecycleState.PUBLISHED, 0)
        total_verified = funnel.get(LifecycleState.BACKLINK_VERIFIED, 0)
        total_retained = funnel.get(LifecycleState.RETAINED, 0)

        # Invariant: Discovered prospects are NOT backlinks
        actual_active_backlinks = total_verified + total_retained

        # Funnel conversion calculation
        approval_rate = (
            round((total_owner_approved / total_draft_ready) * 100, 1)
            if total_draft_ready > 0
            else 0.0
        )
        submission_rate = (
            round((total_submitted / total_owner_approved) * 100, 1)
            if total_owner_approved > 0
            else 0.0
        )
        verification_rate = (
            round((actual_active_backlinks / total_submitted) * 100, 1)
            if total_submitted > 0
            else 0.0
        )

        report_data = {
            "generated_at": now_str,
            "funnel_metrics": {
                "discovered": total_discovered,
                "scored": total_scored,
                "draft_ready": total_draft_ready,
                "owner_approved": total_owner_approved,
                "manually_submitted": total_submitted,
                "published_pending_audit": total_published,
                "backlink_verified": total_verified,
                "retained_clean": total_retained,
                "quarantined": funnel.get(LifecycleState.QUARANTINED, 0),
                "rejected_by_owner": funnel.get(LifecycleState.REJECTED, 0),
                "link_removed": funnel.get(LifecycleState.LINK_REMOVED, 0),
                "expired": funnel.get(LifecycleState.EXPIRED, 0),
            },
            "conversion_rates": {
                "owner_approval_rate_pct": approval_rate,
                "submission_execution_rate_pct": submission_rate,
                "placement_verification_rate_pct": verification_rate,
            },
            "actual_earned_backlinks_count": actual_active_backlinks,
            "retention_milestones": {
                "7_day_confirmed": total_retained,
                "30_day_confirmed": total_retained,
                "90_day_confirmed": total_retained,
            },
        }

        # Build Markdown report
        md_lines = [
            "# 🎯 HERMES Backlink Acquisition & Outcome Intelligence Report",
            f"**Report Generated:** `{now_str}`  ",
            "**Core Standard:** *A prospect discovered is NOT a backlink. A draft approved is NOT a backlink. Only independently verified DOM anchors are earned backlinks.*  ",
            "",
            "## 1. Executive Placement Scorecard",
            f"- **Actual Verified Earned Backlinks:** **`{actual_active_backlinks}`**",
            f"- **Owner Approved & Pending Manual Submission:** `{total_owner_approved}`",
            f"- **Submitted & In Editorial Queue:** `{total_submitted}`",
            f"- **Quarantined / Low-Quality Rejections:** `{funnel.get(LifecycleState.QUARANTINED, 0)}`",
            "",
            "## 2. Acquisition Funnel Velocity & Conversions",
            f"- **Draft-to-Approval Conversion:** `{approval_rate}%` ({total_owner_approved}/{total_draft_ready})",
            f"- **Approval-to-Submission Conversion:** `{submission_rate}%` ({total_submitted}/{total_owner_approved})",
            f"- **Submission-to-Verified Conversion:** `{verification_rate}%` ({actual_active_backlinks}/{total_submitted})",
            "",
            "## 3. Link Retention & Long-Term Health",
            f"- **7-Day Retention:** `{total_retained}` verified links active",
            f"- **30-Day Retention:** `{total_retained}` verified links active",
            f"- **90-Day Retention:** `{total_retained}` verified links active",
            f"- **Lost / Removed Links:** `{funnel.get(LifecycleState.LINK_REMOVED, 0)}`",
            "",
            "## 4. Operational Boundaries",
            "- Autonomous form submission: `DISABLED (Owner Operated Only)`",
            "- Payment gateway claims: `PKR Domestic Rails Strictly Enforced`",
            "- Cloudflare Edge Staging: `48-Hour Burn-In Observation Active`",
        ]

        md_text = "\n".join(md_lines)

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        md_path = self.reports_dir / f"acquisition_performance_{date_slug}.md"
        json_path = self.reports_dir / f"acquisition_performance_{date_slug}.json"

        md_path.write_text(md_text, encoding="utf-8")
        json_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

        report_data["markdown_report"] = md_text
        report_data["report_files"] = {"markdown": str(md_path), "json": str(json_path)}
        return report_data
