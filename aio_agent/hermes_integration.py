"""HERMES-CEO Orchestrator Integration for GEO/AEO & AI Search Agent (AGENT-08)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

from aio_agent.ai_visibility import AIVisibilityTracker
from aio_agent.answer_readiness import AnswerReadinessEvaluator
from aio_agent.grounding_scorer import GroundingScorer
from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus


class AIOHermesAgent:
    """Agent 8 implementation for HERMES Omniscient."""

    AGENT_ID = "AGENT-08-GEO-AEO"

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path(".")
        self.readiness_evaluator = AnswerReadinessEvaluator()
        self.visibility_tracker = AIVisibilityTracker()
        self.grounding_scorer = GroundingScorer(self.project_dir)

    def execute_task(self, task: TaskContract) -> TaskContract:
        task.status = TaskStatus.IN_PROGRESS
        obj_lower = task.objective.lower()

        try:
            if "audit" in obj_lower or "geo" in obj_lower:
                return self._run_comprehensive_geo_audit(task)
            elif "citation" in obj_lower or "visibility" in obj_lower:
                return self._run_citation_tracking(task)
            elif "readiness" in obj_lower or "page" in obj_lower:
                return self._run_page_readiness(task)
            else:
                return self._run_comprehensive_geo_audit(task)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence["error"] = str(e)
            return task

    def _run_page_readiness(self, task: TaskContract) -> TaskContract:
        target_path_str = task.input_evidence.get("file_path") or "tools/chatgpt/index.html"
        target_path = self.project_dir / target_path_str
        if not target_path.exists():
            target_path = self.project_dir / "index.html"

        report = self.readiness_evaluator.evaluate_file(target_path)
        task.actual_output = {
            "file": str(target_path),
            "readiness_report": report.to_dict(),
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "total_score": report.total_score,
            "grade": report.grade,
            "criteria_count": len(report.criteria),
            "timestamp": time.time(),
        }
        return task

    def _run_citation_tracking(self, task: TaskContract) -> TaskContract:
        summary = self.visibility_tracker.compute_visibility_summary()
        status = self.visibility_tracker.get_provider_status()

        task.actual_output = {
            "provider_status": status,
            "visibility_summary": summary.to_dict(),
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "total_queries": summary.total_queries_audited,
            "brand_mention_rate": summary.brand_mention_rate_pct,
            "citation_rate": summary.citation_frequency_pct,
            "evidence_status": summary.evidence_status,
            "timestamp": time.time(),
        }
        return task

    def _run_comprehensive_geo_audit(self, task: TaskContract) -> TaskContract:
        # 1. On-Page readiness for homepage and key tool page
        sample_pages = [self.project_dir / "index.html", self.project_dir / "tools" / "chatgpt" / "index.html"]
        readiness_reports = []
        for p in sample_pages:
            if p.exists():
                rep = self.readiness_evaluator.evaluate_file(p)
                readiness_reports.append(rep.to_dict())

        # 2. Measured AI visibility summary
        vis_summary = self.visibility_tracker.compute_visibility_summary()
        provider_status = self.visibility_tracker.get_provider_status()

        task.actual_output = {
            "agent": self.AGENT_ID,
            "provider_status": provider_status,
            "measured_ai_visibility": vis_summary.to_dict(),
            "on_page_answer_readiness": readiness_reports,
            "separation_enforced": "Strict separation between on-page direct answer readiness and verified external search engine citations",
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "audited_pages": len(readiness_reports),
            "pakistan_visibility_score": vis_summary.pakistan_visibility_score,
            "evidence_status": vis_summary.evidence_status,
            "timestamp": time.time(),
        }
        return task
