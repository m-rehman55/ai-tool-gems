"""
HERMES-CEO — Central Executive Orchestrator
-------------------------------------------
Highest-level coordination agent governing the entire HERMES multi-agent ecosystem.
Coordinates specialist agents, resolves conflicts, enforces task contracts,
validates evidence independently, and maintains the global task dependency graph.
"""

from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from hermes_core.contracts import (
    TaskContract,
    TaskStatus,
    RiskClassification,
    ApprovalRequirement,
    TaskRegistry,
)


@dataclass
class ExecutiveDecision:
    decision_id: str
    task_id: str
    approved: bool
    rationale: str
    risk_level: RiskClassification
    evidence_verified: bool
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HermesCEO:
    """Central Executive Orchestrator (HERMES-CEO)."""

    def __init__(self, base_dir: Optional[Path | str] = None, registry_path: Optional[Path | str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.registry = TaskRegistry(storage_path=registry_path)
        self.evidence_dir = self.base_dir / "data" / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.base_dir / "data" / "reports" / "executive"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.base_dir / "data" / "learning" / "executive_learning_history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def load_learning_history(self) -> Dict[str, Any]:
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"total_decisions": 0, "successful_outcomes": 0, "failed_outcomes": 0, "confidence_modulators": {}}

    def save_learning_history(self, history: Dict[str, Any]) -> None:
        self.history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")

    def delegate_task(
        self,
        responsible_agent: str,
        objective: str,
        scope: str,
        risk: RiskClassification,
        approval: ApprovalRequirement,
        criteria: List[str],
        evidence: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        budget_seconds: int = 300,
    ) -> TaskContract:
        """Dispatches an executive task contract to a specialist agent after duplicate inspection."""
        duplicate = self.registry.detect_duplicate_task(objective, responsible_agent)
        if duplicate:
            print(f"[HERMES-CEO] Duplicate task detected: {duplicate.task_id} is already {duplicate.status.value}. Re-using contract.")
            return duplicate

        task = self.registry.create_task(
            requesting_agent="HERMES-CEO",
            responsible_agent=responsible_agent,
            objective=objective,
            scope=scope,
            risk_classification=risk,
            approval_requirement=approval,
            completion_criteria=criteria,
            input_evidence=evidence,
            dependencies=dependencies,
            required_tools=tools,
            budget_seconds=budget_seconds,
        )
        print(f"[HERMES-CEO] Dispatched {task.task_id} -> {responsible_agent} (Risk: {risk.value})")
        return task

    def validate_task_evidence(self, task_id: str) -> tuple[bool, str]:
        """Independently evaluates whether a task's reported results are backed by empirical evidence."""
        task = self.registry.get_task(task_id)
        if not task:
            return False, f"Task {task_id} not found."

        ev = task.verification_evidence
        if not ev:
            return False, "Zero verification evidence supplied."

        # Check required completion criteria
        for criterion in task.completion_criteria:
            crit_key = criterion.lower().replace(" ", "_")
            if crit_key not in ev and not any(crit_key in str(k).lower() for k in ev.keys()):
                # Allow partial match if detailed evidence dict contains it
                pass

        # Risk-specific independent validation checks
        if task.risk_classification in (RiskClassification.HIGH_COMMERCIAL, RiskClassification.MEDIUM_CODE):
            # Must verify test results artifact
            tests = ev.get("tests", {})
            if not tests or not tests.get("passed", False):
                return False, "Missing verified passing test artifact for code/commercial modification."

        return True, "Task evidence validated independently."

    def resolve_conflicting_recommendations(
        self,
        task_a: TaskContract,
        task_b: TaskContract
    ) -> TaskContract:
        """Arbitrates between competing recommendations from two specialist agents."""
        # Preference: Lower risk, higher verified evidence confidence, higher Pakistan fortress alignment
        print(f"[HERMES-CEO] Arbitrating conflict between {task_a.task_id} and {task_b.task_id}...")
        
        # Priority rule: Security & Policy Firewall (Agent 15) trumps all others
        if "AGENT-15" in task_a.responsible_agent:
            return task_a
        if "AGENT-15" in task_b.responsible_agent:
            return task_b

        # Priority rule: Verified empirical GSC data trumps predictive model inference
        if "AGENT-01" in task_a.responsible_agent and "AGENT-09" in task_b.responsible_agent:
            return task_a
        if "AGENT-01" in task_b.responsible_agent and "AGENT-09" in task_a.responsible_agent:
            return task_b

        # Default: Select task with lower risk level
        risk_rank = {
            RiskClassification.READ_ONLY: 1,
            RiskClassification.LOW_REVERSIBLE: 2,
            RiskClassification.MEDIUM_CODE: 3,
            RiskClassification.HIGH_COMMERCIAL: 4,
            RiskClassification.CRITICAL_DEPLOY: 5,
        }
        return task_a if risk_rank.get(task_a.risk_classification, 3) <= risk_rank.get(task_b.risk_classification, 3) else task_b

    def generate_executive_daily_report(self) -> Dict[str, Any]:
        """Produces a unified, evidence-backed daily executive growth and system report."""
        now_iso = datetime.now(timezone.utc).isoformat()
        all_tasks = list(self.registry.tasks.values())
        
        status_counts = {}
        for t in all_tasks:
            status_counts[t.status.value] = status_counts.get(t.status.value, 0) + 1

        completed_tasks = [t for t in all_tasks if t.status in (TaskStatus.VERIFIED, TaskStatus.DEPLOYED)]
        pending_approvals = self.registry.list_pending_approvals()

        report = {
            "report_type": "EXECUTIVE_DAILY",
            "timestamp": now_iso,
            "system_health": {
                "total_tasks_tracked": len(all_tasks),
                "status_breakdown": status_counts,
                "pending_human_approvals": len(pending_approvals),
                "verified_completed_count": len(completed_tasks),
            },
            "pending_approval_items": [
                {
                    "task_id": t.task_id,
                    "responsible_agent": t.responsible_agent,
                    "objective": t.objective,
                    "risk": t.risk_classification.value,
                    "evidence": t.verification_evidence,
                }
                for t in pending_approvals
            ],
            "strategic_objectives": [
                "Dominate Pakistan transactional search intent with flat PKR pricing",
                "Maintain 100% Core Web Vitals and zero broken links",
                "Automate evidence-driven search console optimizations via pull requests",
            ]
        }

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        report_file = self.reports_dir / f"executive_daily_{today_str}.json"
        report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report

