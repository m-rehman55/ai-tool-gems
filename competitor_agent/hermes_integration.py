"""HERMES-CEO Orchestrator Integration for Competitor Intelligence Agent (AGENT-11)."""

from __future__ import annotations

import time
from typing import Any, Dict

from competitor_agent.competitors import get_top_10_competitors
from competitor_agent.pricing_radar import get_pricing_radar_report
from competitor_agent.serp_radar import compute_share_of_voice, get_serp_radar_snapshots
from competitor_agent.snapshots import CompetitorSnapshotManager
from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus


class CompetitorHermesAgent:
    """Agent 11 implementation for HERMES Omniscient."""

    AGENT_ID = "AGENT-11-COMPETITORS"

    def __init__(self, snapshot_mgr: CompetitorSnapshotManager = None):
        self.snapshot_mgr = snapshot_mgr or CompetitorSnapshotManager()

    def execute_task(self, task: TaskContract) -> TaskContract:
        task.status = TaskStatus.IN_PROGRESS
        obj_lower = task.objective.lower()

        try:
            if "audit" in obj_lower or "gap" in obj_lower:
                return self._run_competitor_gap_audit(task)
            elif "pricing" in obj_lower or "parity" in obj_lower:
                return self._run_pricing_radar(task)
            elif "serp" in obj_lower or "overlap" in obj_lower or "voice" in obj_lower:
                return self._run_serp_radar(task)
            else:
                return self._run_competitor_gap_audit(task)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence["error"] = str(e)
            return task

    def _run_competitor_gap_audit(self, task: TaskContract) -> TaskContract:
        competitors = get_top_10_competitors()
        sov = compute_share_of_voice()
        pricing = get_pricing_radar_report()

        # Build and save snapshot
        snapshot_data = {
            "timestamp": time.time(),
            "competitors_count": len(competitors),
            "share_of_voice": sov,
            "pricing": {p.tool_id: p.competitor_prices for p in pricing},
        }
        self.snapshot_mgr.save_snapshot(snapshot_data)

        task.actual_output = {
            "monitored_competitors_count": len(competitors),
            "top_10_competitors": [c.to_dict() for c in competitors],
            "share_of_voice": sov,
            "pricing_benchmarks": [p.to_dict() for p in pricing],
            "data_policy": "Public SERP observation & empirical market pricing (zero private scraping)",
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "competitors_monitored": len(competitors),
            "market_leader": sov.get("market_leader"),
            "tracked_queries": sov.get("tracked_queries_count"),
            "timestamp": time.time(),
        }
        return task

    def _run_pricing_radar(self, task: TaskContract) -> TaskContract:
        pricing = get_pricing_radar_report()
        price_leader_count = sum(1 for p in pricing if p.price_position == "PRICE_LEADER")

        task.actual_output = {
            "pricing_comparisons": [p.to_dict() for p in pricing],
            "price_leader_count": price_leader_count,
            "total_benchmarked_tools": len(pricing),
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "price_leader_tools": price_leader_count,
            "benchmarked_tools": len(pricing),
            "timestamp": time.time(),
        }
        return task

    def _run_serp_radar(self, task: TaskContract) -> TaskContract:
        radar = get_serp_radar_snapshots()
        sov = compute_share_of_voice()

        task.actual_output = {
            "serp_snapshots": [s.to_dict() for s in radar],
            "share_of_voice": sov,
        }
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "tracked_queries": len(radar),
            "market_leader": sov.get("market_leader"),
            "timestamp": time.time(),
        }
        return task
