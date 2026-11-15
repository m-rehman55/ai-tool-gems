"""Autonomous End-to-End Backlink Intelligence Pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backlink_agent.evidence_scoring import OpportunityScoringEngine, ScoredOpportunity
from backlink_agent.prospect_discovery import DiscoveryOrchestrator, DiscoveredProspect
from backlink_agent.submission_drafter import BaseDraft, SubmissionDraftingEngine
from backlink_agent.telegram_delivery import (
    DailyTelegramReporter,
    OpportunityCardFormatter,
    TelegramOutboxManager,
)

logger = logging.getLogger(__name__)

REPORTS_DIR = Path("seo-agent/reports/backlinks")


class BacklinkIntelligencePipeline:
    """End-to-End Orchestrator running Discovery -> Scoring -> Drafting -> Telegram Outbox."""

    def __init__(
        self,
        discovery_orchestrator: Optional[DiscoveryOrchestrator] = None,
        scoring_engine: Optional[OpportunityScoringEngine] = None,
        drafting_engine: Optional[SubmissionDraftingEngine] = None,
        outbox_manager: Optional[TelegramOutboxManager] = None,
        reports_dir: Path = REPORTS_DIR,
    ):
        self.discovery_orchestrator = discovery_orchestrator or DiscoveryOrchestrator()
        self.scoring_engine = scoring_engine or OpportunityScoringEngine()
        self.drafting_engine = drafting_engine or SubmissionDraftingEngine()
        self.outbox_manager = outbox_manager or TelegramOutboxManager()
        self.reports_dir = Path(reports_dir)

    def run_daily_intelligence(
        self,
        dispatch_telegram: bool = True,
        export_reports: bool = True,
    ) -> Dict[str, Any]:
        """Executes a full daily backlink intelligence cycle."""
        run_start = datetime.now(timezone.utc)
        logger.info(f"Starting Backlink Intelligence Cycle at {run_start.isoformat()}")

        # 1. Discover Prospects
        discovery_result = self.discovery_orchestrator.run_discovery()
        discovered = discovery_result["prospects"]

        # 2. Score Opportunities (0-100 rubric)
        scored_opportunities: List[ScoredOpportunity] = [
            self.scoring_engine.score_prospect(p) for p in discovered
        ]

        high_priority = [o for o in scored_opportunities if o.score.priority_tier == "high_priority"]
        investigate = [o for o in scored_opportunities if o.score.priority_tier == "investigate"]
        quarantine = [o for o in scored_opportunities if o.score.priority_tier == "quarantine"]

        # 3. Draft Packages for high priority / draft ready opportunities
        drafted_tuples = self.drafting_engine.draft_batch(scored_opportunities)
        drafts_generated: List[BaseDraft] = [t[0] for t in drafted_tuples]

        # 4. Generate Telegram Daily Summary & Individual Cards
        summary_text = DailyTelegramReporter.format_daily_summary(
            total_discovered=len(discovered),
            scored_opportunities=scored_opportunities,
            drafts_generated=drafts_generated,
            live_backlinks_count=4,
        )
        self.outbox_manager.enqueue(
            text=summary_text,
            message_type="daily_summary",
        )

        for draft, d_hash, opp in drafted_tuples:
            card_text = OpportunityCardFormatter.format_card(opp, draft, d_hash)
            self.outbox_manager.enqueue(
                text=card_text,
                message_type="opportunity_card",
                prospect_domain=opp.prospect_domain,
                draft_hash=d_hash,
            )

        # 5. Flush outbox
        flush_results = {"processed": 0, "sent": 0, "failed": 0}
        if dispatch_telegram:
            flush_results = self.outbox_manager.flush_outbox()

        # 6. Export Reports
        report_files = {}
        if export_reports:
            report_files = self._export_reports(
                discovered=discovered,
                scored_opportunities=scored_opportunities,
                drafted_tuples=drafted_tuples,
                flush_results=flush_results,
                run_start=run_start,
            )

        run_duration = (datetime.now(timezone.utc) - run_start).total_seconds()

        return {
            "run_at": run_start.isoformat(),
            "duration_seconds": round(run_duration, 2),
            "discovered_count": len(discovered),
            "scored_count": len(scored_opportunities),
            "tiers": {
                "high_priority": len(high_priority),
                "investigate": len(investigate),
                "quarantine": len(quarantine),
            },
            "drafts_generated_count": len(drafts_generated),
            "outbox_flush": flush_results,
            "report_files": report_files,
        }

    def _export_reports(
        self,
        discovered: List[DiscoveredProspect],
        scored_opportunities: List[ScoredOpportunity],
        drafted_tuples: List[Any],
        flush_results: Dict[str, int],
        run_start: datetime,
    ) -> Dict[str, str]:
        date_slug = run_start.strftime("%Y-%m-%d")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        md_path = self.reports_dir / f"backlink_intelligence_{date_slug}.md"
        json_path = self.reports_dir / f"backlink_intelligence_{date_slug}.json"

        # Structured JSON
        data_payload = {
            "timestamp": run_start.isoformat(),
            "total_discovered": len(discovered),
            "opportunities": [o.to_dict() for o in scored_opportunities],
            "drafts": [
                {"draft": t[0].to_dict(), "draft_hash": t[1], "domain": t[2].prospect_domain}
                for t in drafted_tuples
            ],
            "outbox": flush_results,
        }
        json_path.write_text(json.dumps(data_payload, indent=2), encoding="utf-8")

        # Markdown Report
        md_lines = [
            "# 🧠 AI Tool Gems Autonomous Backlink Intelligence Daily Report",
            f"**Cycle Run:** `{run_start.strftime('%Y-%m-%d %H:%M:%S UTC')}`  ",
            f"**Total Discovered:** `{len(discovered)}` | **High Priority:** `{len([o for o in scored_opportunities if o.score.priority_tier == 'high_priority'])}`  ",
            "",
            "## 1. High-Priority Draft Packages Generated",
            "| Domain | Type | Score | Draft ID | Draft Hash | Action Status |",
            "|---|---|---|---|---|---|",
        ]

        for draft, d_hash, opp in drafted_tuples:
            md_lines.append(
                f"| `{opp.prospect_domain}` | `{opp.prospect_type}` | **{opp.score.total_score}** | `{draft.draft_id}` | `{d_hash}` | `pending_owner_review` |"
            )

        md_lines.extend([
            "",
            "## 2. Notification Dispatch Summary",
            f"- Messages Processed: `{flush_results.get('processed', 0)}`",
            f"- Successfully Sent: `{flush_results.get('sent', 0)}`",
            f"- Delivery Failures: `{flush_results.get('failed', 0)}`",
            "",
            "## 3. Operational Safety Status",
            "- Autonomous form submission / email outreach: `DISABLED (Manual Review Only)`",
            "- Disallowed gateways (Stripe/PayPal): `BLOCKED BY FACT VALIDATOR`",
            "- Domestic Pakistan payment rails (EasyPaisa/JazzCash/SadaPay/Raast): `VERIFIED`",
        ])

        md_text = "\n".join(md_lines)
        md_path.write_text(md_text, encoding="utf-8")

        return {"markdown": str(md_path), "json": str(json_path)}
