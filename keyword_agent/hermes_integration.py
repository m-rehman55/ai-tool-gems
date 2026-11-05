"""
hermes_integration.py - HERMES Executive Orchestrator Task Contract Handler for AGENT-03-KEYWORD.

Connects keyword_agent into the central HERMES-CEO multi-agent framework:
- Ingests TaskContracts dispatched to AGENT-03-KEYWORD.
- Executes evidence-backed keyword intelligence, intent classification, and gap detection.
- Emits structured verification evidence and outputs.
- Adheres strictly to security and safety approval gates.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from hermes_core.contracts import TaskContract, TaskStatus, RiskClassification
from keyword_agent.config import get_agent_settings
from keyword_agent.gsc_data import GSCDataEngine
from keyword_agent.discovery import KeywordDiscoveryEngine
from keyword_agent.page_mapper import PageMapper
from keyword_agent.regex_engine import GSCFilterLibrary
from keyword_agent.external_providers import MultiSourceKeywordEngine
from keyword_agent.declining_keywords import DecliningKeywordsEngine
from keyword_agent.competitor_gap import CompetitorGapAnalyzer
from keyword_agent.reporting import KeywordReportGenerator

logger = logging.getLogger("keyword_agent.hermes")


def execute_keyword_task(contract: TaskContract, project_dir: Optional[Path] = None) -> TaskContract:
    """
    Executes a task contract assigned to AGENT-03-KEYWORD.
    Returns the updated TaskContract with verification evidence.
    """
    settings = get_agent_settings()
    p_dir = project_dir or settings.project_dir
    reports_dir = p_dir / "data" / "reports" / "keyword_agent"
    reports_dir.mkdir(parents=True, exist_ok=True)

    contract.status = TaskStatus.IN_PROGRESS
    obj_lower = contract.objective.lower()

    try:
        # Initialize engines
        gsc_engine = GSCDataEngine(
            exports_dir=settings.exports_dir,
            history_dir=settings.history_dir,
            site_url=settings.site_url,
            auto_extract=False,
        )
        dataset = gsc_engine.load_dataset(allow_live=True)
        disc_engine = KeywordDiscoveryEngine()
        page_mapper = PageMapper(project_dir=p_dir)
        multi_engine = MultiSourceKeywordEngine(gsc_dataset=dataset)

        evidence: Dict[str, Any] = {
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "gsc_dataset_source": dataset.source,
            "gsc_total_clicks": dataset.total_clicks,
            "gsc_total_impressions": dataset.total_impressions,
            "providers_status": multi_engine.get_provider_status_matrix(),
        }

        # 1. Competitor Gap Analysis Task
        if "competitor" in obj_lower:
            gap_analyzer = CompetitorGapAnalyzer(project_dir=p_dir)
            gap_report = gap_analyzer.run_gap_analysis()
            report_file = gap_analyzer.export_markdown_report(gap_report)

            evidence["task_type"] = "COMPETITOR_GAP"
            evidence["competitor_analyzed"] = gap_report.competitor_domain
            evidence["total_competitor_urls"] = gap_report.total_competitor_urls
            evidence["uncovered_high_value_gaps"] = gap_report.uncovered_high_value_gaps
            evidence["report_path"] = str(report_file)

        # 2. Declining Keywords Task
        elif "declin" in obj_lower:
            prev_snapshot = gsc_engine.get_latest_historical_snapshot()
            declining_engine = DecliningKeywordsEngine(current_dataset=dataset, previous_dataset=prev_snapshot)
            declines = declining_engine.analyze()

            evidence["task_type"] = "DECLINING_KEYWORDS"
            evidence["declines_count"] = len(declines)
            evidence["critical_declines"] = [d.to_dict() for d in declines if d.severity == "CRITICAL_DECLINE"]
            evidence["dropouts"] = [d.to_dict() for d in declines if d.severity == "DROPOUT"]

        # 3. Comprehensive Keyword Intelligence & Audit
        else:
            # Process GSC queries or seed clusters
            candidates = disc_engine.process_gsc_queries(dataset) if dataset.queries else disc_engine.generate_seed_discovery_clusters()
            intl_candidates = disc_engine.generate_international_discovery_clusters()
            all_candidates = candidates + intl_candidates

            # Map to canonical routes & detect cannibalization
            mappings = [page_mapper.find_best_url(c.keyword, c.intent) for c in all_candidates]
            collisions = page_mapper.detect_cannibalization(mappings)
            missing_pages = page_mapper.detect_missing_landing_pages(all_candidates)
            content_gaps = page_mapper.detect_content_gaps(all_candidates)

            # Generate report
            filters = GSCFilterLibrary().get_core_filters()
            opportunities = disc_engine.segment_opportunities(all_candidates)
            reporter = KeywordReportGenerator(reports_dir=reports_dir, docs_dir=p_dir / "docs")
            md_rep, json_rep = reporter.generate_daily_report(
                gsc_dataset=dataset,
                filters=filters,
                opportunities=opportunities,
                collisions=collisions,
                briefs=[],
            )

            evidence["task_type"] = "KEYWORD_AUDIT"
            evidence["total_candidates"] = len(all_candidates)
            evidence["quick_wins_count"] = len(opportunities.get("high_impact_quick_wins", []))
            evidence["cannibalization_collisions_count"] = len(collisions)
            evidence["missing_landing_pages_count"] = len(missing_pages)
            evidence["content_gaps_count"] = len(content_gaps)
            evidence["markdown_report"] = str(md_rep)
            evidence["json_report"] = str(json_rep)

        # Output artifact path
        artifact_path = reports_dir / f"task_{contract.task_id}_evidence.json"
        artifact_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        evidence["artifact_file"] = str(artifact_path)

        contract.verification_evidence = evidence
        contract.status = TaskStatus.VERIFIED

    except Exception as e:
        logger.error(f"Failed executing keyword task {contract.task_id}: {e}", exc_info=True)
        contract.verification_evidence = {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        contract.status = TaskStatus.FAILED

    return contract


class KeywordHermesAgent:
    """Class wrapper for AGENT-03-KEYWORD task execution."""
    AGENT_ID = "AGENT-03-KEYWORD"

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent

    def execute_task(self, task: TaskContract) -> TaskContract:
        return execute_keyword_task(task, project_dir=self.repo_root)
