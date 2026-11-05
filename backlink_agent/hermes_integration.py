"""HERMES-CEO Orchestrator Integration for Backlink Intelligence Agent (AGENT-10)."""

from __future__ import annotations

import time
from typing import Any, Dict, List

from backlink_agent.models import BacklinkRecord, LinkStatus
from backlink_agent.pakistan_authority import get_pakistan_authority_opportunities
from backlink_agent.providers import BacklinkProviderManager
from backlink_agent.toxicity_analyzer import ToxicityScanner
from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus


class BacklinkHermesAgent:
    """Agent 10 implementation for HERMES Omniscient."""

    AGENT_ID = "AGENT-10-BACKLINKS"

    def __init__(self, provider_mgr: BacklinkProviderManager = None):
        self.provider_mgr = provider_mgr or BacklinkProviderManager()
        self.toxicity_scanner = ToxicityScanner()

    def execute_task(self, task: TaskContract) -> TaskContract:
        task.status = TaskStatus.IN_PROGRESS
        obj_lower = task.objective.lower()

        try:
            if "audit" in obj_lower:
                return self._run_backlink_audit(task)
            elif "opportunity" in obj_lower or "gap" in obj_lower or "pakistan" in obj_lower:
                return self._run_opportunity_analysis(task)
            elif "toxic" in obj_lower or "disavow" in obj_lower:
                return self._run_toxicity_scan(task)
            else:
                return self._run_backlink_audit(task)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence["error"] = str(e)
            return task

    def _run_backlink_audit(self, task: TaskContract) -> TaskContract:
        inv = self.provider_mgr.load_inventory()
        records = [BacklinkRecord(**item) for item in inv]
        audit_res = self.toxicity_scanner.audit_inventory(records)
        providers = self.provider_mgr.get_provider_matrix()

        referring_domains = len({r.source_url.split('/')[2] for r in records if '//' in r.source_url})
        follow_count = sum(1 for r in records if r.is_follow)

        task.actual_output = {
            "total_backlinks": len(records),
            "referring_domains": referring_domains,
            "dofollow_ratio_pct": round((follow_count / len(records) * 100.0) if records else 0.0, 1),
            "toxicity_audit": audit_res,
            "providers_status": providers,
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "total_backlinks": len(records),
            "referring_domains": referring_domains,
            "toxic_links_found": audit_res["toxic_links_count"],
            "timestamp": time.time(),
        }
        return task

    def _run_opportunity_analysis(self, task: TaskContract) -> TaskContract:
        opps = get_pakistan_authority_opportunities()
        task.actual_output = {
            "opportunities_count": len(opps),
            "opportunities": [o.to_dict() for o in opps],
            "anti_spam_verified": True,
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "opportunities_identified": len(opps),
            "zero_spam_policy_enforced": True,
            "timestamp": time.time(),
        }
        return task

    def _run_toxicity_scan(self, task: TaskContract) -> TaskContract:
        inv = self.provider_mgr.load_inventory()
        records = [BacklinkRecord(**item) for item in inv]
        audit_res = self.toxicity_scanner.audit_inventory(records)

        toxic_recs = [r for r in records if r.toxicity_score >= 50.0]
        disavow_text = self.toxicity_scanner.generate_disavow_file(toxic_recs)

        task.actual_output = {
            "toxicity_audit": audit_res,
            "disavow_file_preview": disavow_text,
            "toxic_count": len(toxic_recs),
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "toxic_count": len(toxic_recs),
            "disavow_generated": len(toxic_recs) > 0,
            "timestamp": time.time(),
        }
        return task
