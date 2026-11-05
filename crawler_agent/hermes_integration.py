"""
crawler_agent.hermes_integration - Connects Technical Crawler Agent to HERMES Central Orchestrator.
"""

from pathlib import Path
from typing import Dict, Any

from hermes_core.contracts import TaskContract, TaskStatus, RiskClassification, ApprovalRequirement
from crawler_agent.engine import CrawlerEngine
from crawler_agent.analyzer import TechnicalSEOAnalyzer


class CrawlerHermesAgent:
    """
    AGENT-02-CRAWLER:
    Production & Repository Technical Crawler & Link Graph Analyzer.
    """

    AGENT_ID = "AGENT-02-CRAWLER"

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.crawler = CrawlerEngine(base_dir=self.repo_root)
        self.analyzer = TechnicalSEOAnalyzer()

    def execute_task(self, task: TaskContract) -> TaskContract:
        task.responsible_agent = self.AGENT_ID
        try:
            # Execute local repository crawl to evaluate technical health
            records = self.crawler.crawl_local_repository()
            summary = self.analyzer.audit_crawl_dataset(records, crawl_mode="LOCAL_REPOSITORY")

            task.status = TaskStatus.VERIFIED
            task.verification_evidence = {
                "total_pages_crawled": len(records),
                "technical_health_score": summary.technical_health_score,
                "broken_links_count": len(summary.broken_links),
                "orphan_pages_count": len(summary.orphan_pages),
                "duplicate_titles_count": len(summary.duplicate_titles)
            }
            task.expected_output = (
                f"Technical SEO Crawl Complete: {len(records)} pages, "
                f"Health Score: {summary.technical_health_score}/100"
            )
            return task
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence = {"error": f"Crawler execution error: {str(e)}"}
            return task
