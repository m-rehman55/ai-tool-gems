"""
gsc_agent.hermes_integration - Connects Search Console Agent to HERMES Central Orchestrator.
"""

from pathlib import Path
from typing import Dict, Any

from hermes_core.contracts import TaskContract, TaskStatus, RiskClassification, ApprovalRequirement
from gsc_agent.client import GSCClient
from gsc_agent.performance import GSCPerformanceEngine
from gsc_agent.opportunities import GSCOpportunityEngine


class GSCHermesAgent:
    """
    AGENT-01-GSC:
    Google Search Console Intelligence, Search Analytics & CTR Opportunity Engine.
    """

    AGENT_ID = "AGENT-01-GSC"

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.client = GSCClient(repo_root=self.repo_root)
        self.perf = GSCPerformanceEngine(self.client)
        self.opportunities = GSCOpportunityEngine(self.client)

    def execute_task(self, task: TaskContract) -> TaskContract:
        task.responsible_agent = self.AGENT_ID
        try:
            if not self.client.is_configured:
                task.status = TaskStatus.BLOCKED_PENDING_CREDENTIALS
                task.verification_evidence = {
                    "status": "BLOCKED_PENDING_CREDENTIALS",
                    "reason": "GSC OAuth credentials or refresh token pending in environment/vault.",
                    "required_scopes": ["https://www.googleapis.com/auth/webmasters.readonly"]
                }
                task.expected_output = "GSC Agent blocked pending authorized OAuth credentials"
                return task

            # When configured, retrieve performance summary
            perf_summary = self.perf.get_search_performance(days=28, country="PAK")
            task.status = TaskStatus.VERIFIED
            task.verification_evidence = {
                "total_clicks": perf_summary.get("total_clicks", 0),
                "total_impressions": perf_summary.get("total_impressions", 0),
                "average_ctr": perf_summary.get("average_ctr", 0.0),
                "country_filtered": "PAK"
            }
            return task
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence = {"error": f"GSC execution error: {str(e)}"}
            return task

