"""HERMES-CEO Orchestrator Integration for PageSpeed Agent (AGENT-07)."""

from __future__ import annotations

import time
from typing import Any, Dict

from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus
from pagespeed_agent.client import PageSpeedClient
from pagespeed_agent.regression_detector import detect_regressions
from pagespeed_agent.representative_urls import REPRESENTATIVE_TEMPLATES, get_representative_urls


class PageSpeedHermesAgent:
    """Agent 7 implementation for HERMES Omniscient."""

    AGENT_ID = "AGENT-07-PAGESPEED"

    def __init__(self, client: PageSpeedClient = None):
        self.client = client or PageSpeedClient()

    def execute_task(self, task: TaskContract) -> TaskContract:
        task.status = TaskStatus.IN_PROGRESS
        objective_lower = task.objective.lower()

        try:
            if "benchmark" in objective_lower or "templates" in objective_lower or "all" in objective_lower:
                return self._run_benchmark_all(task)
            elif "regression" in objective_lower and "audit" not in objective_lower:
                return self._run_regression_check(task)
            else:
                return self._run_single_audit(task)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence["error"] = str(e)
            return task

    def _run_single_audit(self, task: TaskContract) -> TaskContract:
        target_url = task.input_evidence.get("url") or "https://aitoolgems.tech/"
        strategy = task.input_evidence.get("strategy") or "mobile"

        result = self.client.audit_url(target_url, strategy=strategy)
        eval_res = detect_regressions(result)

        task.actual_output = {
            "url": target_url,
            "strategy": strategy,
            "audit": result.to_dict(),
            "evaluation": {
                "has_regressions": eval_res.has_regressions,
                "recommendations": eval_res.recommendations,
            },
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "performance_score": result.lab_data.performance_score,
            "lcp_ms": result.lab_data.lcp_ms,
            "cls": result.lab_data.cls,
            "tbt_ms": result.lab_data.tbt_ms,
            "data_source": result.data_source,
            "timestamp": time.time(),
        }
        return task

    def _run_regression_check(self, task: TaskContract) -> TaskContract:
        target_url = task.input_evidence.get("url") or "https://aitoolgems.tech/"
        current = self.client.audit_url(target_url, strategy="mobile")
        # Run regression against baseline
        evaluation = detect_regressions(current)

        task.actual_output = {
            "url": target_url,
            "has_regressions": evaluation.has_regressions,
            "incidents_count": len(evaluation.incidents),
            "recommendations": evaluation.recommendations,
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "has_regressions": evaluation.has_regressions,
            "incidents_count": len(evaluation.incidents),
            "timestamp": time.time(),
        }
        return task

    def _run_benchmark_all(self, task: TaskContract) -> TaskContract:
        results = []
        for template in REPRESENTATIVE_TEMPLATES:
            for strategy in ["mobile", "desktop"]:
                res = self.client.audit_url(template["url"], strategy=strategy)
                results.append({
                    "template_id": template["template_id"],
                    "url": template["url"],
                    "strategy": strategy,
                    "score": res.lab_data.performance_score,
                    "lcp_ms": res.lab_data.lcp_ms,
                    "cls": res.lab_data.cls,
                })

        task.actual_output = {
            "benchmarks": results,
            "templates_count": len(REPRESENTATIVE_TEMPLATES),
            "total_audits": len(results),
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "audits_completed": len(results),
            "avg_mobile_score": sum(r["score"] for r in results if r["strategy"] == "mobile") / len(REPRESENTATIVE_TEMPLATES),
            "timestamp": time.time(),
        }
        return task
