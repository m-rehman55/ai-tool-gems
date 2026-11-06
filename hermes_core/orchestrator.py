"""
HERMES-CEO — Central Executive Orchestrator
-------------------------------------------
Highest-level coordination agent governing the entire HERMES multi-agent ecosystem.
Coordinates 15 specialist agents, resolves conflicts, enforces task contracts,
validates evidence independently, executes end-to-end growth cycles,
and maintains the global task dependency graph.
"""

from __future__ import annotations
import json
import os
import sys

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
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
        self._agents: Dict[str, Any] = {}

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Lazy loads and caches specialist agent instances."""
        if agent_id in self._agents:
            return self._agents[agent_id]

        instance = None
        try:
            if agent_id in ("AGENT-01-GSC", "gsc"):
                from gsc_agent.hermes_integration import GSCHermesAgent
                instance = GSCHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-02-CRAWLER", "crawler"):
                from crawler_agent.hermes_integration import CrawlerHermesAgent
                instance = CrawlerHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-03-KEYWORD", "keyword"):
                from keyword_agent.hermes_integration import KeywordHermesAgent
                instance = KeywordHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-04-BING", "bing"):
                from bing_agent.hermes_integration import BingHermesAgent
                instance = BingHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-05-GA4", "ga4"):
                from ga4_agent.hermes_integration import GA4HermesAgent
                instance = GA4HermesAgent(self.base_dir)
            elif agent_id in ("AGENT-06-POSTHOG", "posthog"):
                from posthog_agent.hermes_integration import PostHogHermesAgent
                instance = PostHogHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-07-PAGESPEED", "pagespeed"):
                from pagespeed_agent.hermes_integration import PageSpeedHermesAgent
                instance = PageSpeedHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-08-GEO-AEO", "aio"):
                from aio_agent.hermes_integration import AIOHermesAgent
                instance = AIOHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-09-CONTENT", "content"):
                from content_agent.hermes_integration import ContentHermesAgent
                instance = ContentHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-10-BACKLINKS", "backlinks"):
                from backlink_agent.hermes_integration import BacklinkHermesAgent
                instance = BacklinkHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-11-COMPETITORS", "competitor"):
                from competitor_agent.hermes_integration import CompetitorHermesAgent
                instance = CompetitorHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-12-MARKETING", "marketing"):
                from marketing_agent.hermes_integration import MarketingHermesAgent
                instance = MarketingHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-13-MERCHANT", "merchant"):
                from merchant_agent.hermes_integration import MerchantHermesAgent
                instance = MerchantHermesAgent(self.base_dir)
            elif agent_id in ("AGENT-14-CONVERSION", "conversion"):
                from conversion_agent.hermes_integration import HermesConversionAgent
                instance = HermesConversionAgent(self.base_dir)
            elif agent_id in ("AGENT-15-SECURITY", "security"):
                from security_agent.hermes_integration import HermesSecurityAgent
                instance = HermesSecurityAgent(self.base_dir)
        except Exception as e:
            print(f"[HERMES-CEO] Error instantiating agent {agent_id}: {e}")

        if instance:
            self._agents[agent_id] = instance
        return instance

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

    def execute_task_contract(self, task: TaskContract) -> TaskContract:
        """Executes a dispatched contract using the appropriate specialist agent and validates evidence."""
        agent = self.get_agent(task.responsible_agent)
        if not agent:
            task.status = TaskStatus.FAILED
            task.verification_evidence = {"error": f"Agent {task.responsible_agent} not found or failed to load."}
            self.registry.update_task_status(task.task_id, TaskStatus.FAILED, task.verification_evidence)
            return task

        task.status = TaskStatus.IN_PROGRESS
        self.registry.update_task_status(task.task_id, TaskStatus.IN_PROGRESS)

        completed_task = agent.execute_task(task)

        # Validate evidence independently
        valid, msg = self.validate_task_evidence(completed_task.task_id)
        if not valid and completed_task.status == TaskStatus.VERIFIED:
            print(f"[HERMES-CEO] Evidence validation rejected for {completed_task.task_id}: {msg}")
            completed_task.status = TaskStatus.FAILED

        self.registry.update_task_status(
            completed_task.task_id,
            completed_task.status,
            completed_task.verification_evidence
        )
        return completed_task

    def validate_task_evidence(self, task_id: str) -> tuple[bool, str]:
        """Independently evaluates whether a task's reported results are backed by empirical evidence."""
        task = self.registry.get_task(task_id)
        if not task:
            return False, f"Task {task_id} not found."

        ev = task.verification_evidence
        if not ev:
            return False, "Zero verification evidence supplied."

        # Risk-specific independent validation checks
        if task.risk_classification in (RiskClassification.HIGH_COMMERCIAL, RiskClassification.MEDIUM_CODE):
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

        risk_rank = {
            RiskClassification.READ_ONLY: 1,
            RiskClassification.LOW_REVERSIBLE: 2,
            RiskClassification.MEDIUM_CODE: 3,
            RiskClassification.HIGH_COMMERCIAL: 4,
            RiskClassification.CRITICAL_DEPLOY: 5,
        }
        return task_a if risk_rank.get(task_a.risk_classification, 3) <= risk_rank.get(task_b.risk_classification, 3) else task_b

    def run_master_audit_cycle(self) -> Dict[str, Any]:
        """
        Executes a complete, coordinated multi-agent audit cycle across specialist agents:
        Security (15) -> Crawler (2) -> PageSpeed (7) -> Merchant (13) -> Conversion (14) -> AIO/GEO (8) -> Competitor (11)
        """
        print("\n=================================================================")
        print("[HERMES-CEO] MASTER MULTI-AGENT EXECUTION LOOP START")
        print("=================================================================")

        cycle_results = {}

        # 1. Security & Firewall Gate (Agent 15)
        task_sec = self.delegate_task(
            responsible_agent="AGENT-15-SECURITY",
            objective="Perform complete security and safety audit",
            scope="repository",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["Valid security audit report"]
        )
        res_sec = self.execute_task_contract(task_sec)
        cycle_results["security"] = res_sec.verification_evidence

        # 2. Technical Crawler (Agent 2)
        task_crawl = self.delegate_task(
            responsible_agent="AGENT-02-CRAWLER",
            objective="Crawl local repository and discover link graph health",
            scope="repository",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["Crawl graph discovered"]
        )
        res_crawl = self.execute_task_contract(task_crawl)
        cycle_results["crawler"] = res_crawl.verification_evidence

        # 3. PageSpeed & Core Web Vitals (Agent 7)
        task_perf = self.delegate_task(
            responsible_agent="AGENT-07-PAGESPEED",
            objective="Audit representative URLs for Core Web Vitals health",
            scope="templates",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["PageSpeed evaluation"]
        )
        res_perf = self.execute_task_contract(task_perf)
        cycle_results["pagespeed"] = res_perf.verification_evidence

        # 4. Merchant Center & Schema Parity (Agent 13)
        task_merch = self.delegate_task(
            responsible_agent="AGENT-13-MERCHANT",
            objective="Generate Google Merchant Center feeds and audit schema parity",
            scope="catalog",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["Merchant feed generation"]
        )
        res_merch = self.execute_task_contract(task_merch)
        cycle_results["merchant"] = res_merch.verification_evidence

        # 5. Conversion Journey & Trust Architecture (Agent 14)
        task_conv = self.delegate_task(
            responsible_agent="AGENT-14-CONVERSION",
            objective="Run conversion journey and trust audit across catalog",
            scope="site-wide",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["Catalog conversion analysis"]
        )
        res_conv = self.execute_task_contract(task_conv)
        cycle_results["conversion"] = res_conv.verification_evidence

        # 6. GEO & AI Search Visibility (Agent 8)
        task_aio = self.delegate_task(
            responsible_agent="AGENT-08-GEO-AEO",
            objective="Audit AI answer readiness and search platform visibility",
            scope="index.html",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["AI visibility evaluation"]
        )
        res_aio = self.execute_task_contract(task_aio)
        cycle_results["aio"] = res_aio.verification_evidence

        # 7. Competitor Intelligence & Radar (Agent 11)
        task_comp = self.delegate_task(
            responsible_agent="AGENT-11-COMPETITORS",
            objective="Audit competitor price leaders and SERP overlap",
            scope="pakistan-serp",
            risk=RiskClassification.READ_ONLY,
            approval=ApprovalRequirement.AUTONOMOUS_APPROVED,
            criteria=["Competitor audit report"]
        )
        res_comp = self.execute_task_contract(task_comp)
        cycle_results["competitors"] = res_comp.verification_evidence

        # Executive Daily Synthesis
        report = self.generate_executive_daily_report()
        report["cycle_results"] = cycle_results

        print("=================================================================")
        print("[HERMES-CEO] MASTER MULTI-AGENT EXECUTION LOOP COMPLETE")
        print("=================================================================\n")
        return report

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


if __name__ == "__main__":
    ceo = HermesCEO()
    res = ceo.run_master_audit_cycle()
    print("\n[HERMES-CEO] Master audit cycle completed successfully!")
