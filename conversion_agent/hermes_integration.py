"""
conversion_agent.hermes_integration - Connects Conversion Journey Agent to HERMES Central Orchestrator.
"""

from pathlib import Path
from typing import Dict, Any

from hermes_core.contracts import TaskContract, TaskStatus, RiskClassification, ApprovalRequirement
from conversion_agent.journey_analyzer import CustomerJourneyAnalyzer


class HermesConversionAgent:
    """
    AGENT-14-CONVERSION:
    Evaluates website conversion funnel, trust architecture, and purchase friction.
    """

    AGENT_ID = "AGENT-14-CONVERSION"

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.analyzer = CustomerJourneyAnalyzer(self.repo_root)

    def execute_task(self, task: TaskContract) -> TaskContract:
        """
        Executes a TaskContract delegated to AGENT-14-CONVERSION.
        """
        task.responsible_agent = self.AGENT_ID
        objective_lower = task.objective.lower()

        try:
            if "audit" in objective_lower or "funnel" in objective_lower or "journey" in objective_lower:
                return self._handle_catalog_audit(task)
            elif "page" in objective_lower or "friction" in objective_lower:
                return self._handle_page_audit(task)
            elif "trust" in objective_lower:
                return self._handle_trust_audit(task)
            else:
                return self._handle_catalog_audit(task)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence = {"error": f"Conversion agent execution error: {str(e)}"}
            return task

    def _handle_catalog_audit(self, task: TaskContract) -> TaskContract:
        audit_res = self.analyzer.audit_catalog()

        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "total_pages_audited": audit_res["total_pages_audited"],
            "average_journey_score": audit_res["average_journey_score"],
            "high_friction_pages_count": len(audit_res["high_friction_pages"]),
            "high_friction_pages": audit_res["high_friction_pages"]
        }
        task.expected_output = (
            f"Catalog Conversion Journey Audit Complete: {audit_res['average_journey_score']}/100 score"
        )
        return task

    def _handle_page_audit(self, task: TaskContract) -> TaskContract:
        target_path_str = task.scope or "index.html"
        target_path = Path(target_path_str)
        if not target_path.is_absolute():
            target_path = self.repo_root / target_path_str

        if not target_path.exists():
            task.status = TaskStatus.FAILED
            task.verification_evidence = {"error": f"Target file does not exist: {target_path_str}"}
            return task

        report = self.analyzer.analyze_file(target_path)
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "target": target_path_str,
            "overall_score": report.overall_readiness_score,
            "trust_score": report.trust_audit.trust_score,
            "friction_score": report.friction_audit.friction_score,
            "issues_count": len(report.friction_audit.issues)
        }
        return task

    def _handle_trust_audit(self, task: TaskContract) -> TaskContract:
        target_path = self.repo_root / "index.html"
        report = self.analyzer.analyze_file(target_path)

        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "trust_score": report.trust_audit.trust_score,
            "passed_checks": report.trust_audit.passed_checks,
            "failed_checks": report.trust_audit.failed_checks
        }
        return task
