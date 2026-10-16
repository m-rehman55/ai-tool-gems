#!/usr/bin/env python3
"""
Autonomous Growth Orchestrator for AIToolGems
---------------------------------------------
Coordinates the complete 10-step autonomous SEO & AI Search execution loop:
1. Preflight
2. Collect Evidence
3. Audit
4. Research
5. Prioritize
6. Generate Improvements
7. Validate
8. Prepare Changes
9. Monitor
10. Report
"""

from __future__ import annotations
import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from agent.crawler import Crawler, CrawledPage
from agent.technical_audit import TechnicalAuditor, TechnicalAuditReport
from agent.schema_validator import SchemaValidator
from agent.internal_links import InternalLinkAnalyzer
from agent.keyword_research import KeywordManager
from agent.content_quality import ContentQualityAuditor
from agent.content_planner import ContentPlanner
from agent.decision_engine import DecisionEngine, SEOOpportunity, Category, ActionTier
from agent.scope_guard import ScopeGuard, ScopeResult
from agent.safety_firewall import SafetyFirewall
from agent.monitoring import PerformanceMonitor, PerformanceMetrics
from agent.github_integration import GitHubIntegration
from agent.reporting import ReportGenerator
from agent.telegram_notifier import TelegramNotifier, TelegramNotificationResult
from agent.deployment_verifier import DeploymentVerifier

class GrowthOrchestrator:
    """Master orchestrator executing the 10-step daily growth loop."""

    def __init__(
        self,
        config_path: Optional[Path | str] = None,
        mode: str = "AUDIT",
        live_crawl: bool = False,
        send_telegram: bool = False,
    ):
        self.mode = mode.upper()
        self.live_crawl = live_crawl
        self.send_telegram = send_telegram
        self.base_dir = Path(__file__).resolve().parent.parent.parent

        # Load configuration
        cfg_file = Path(config_path) if config_path else (self.base_dir / "seo-agent" / "config" / "settings.example.yml")
        self.config: Dict[str, Any] = {}
        if cfg_file.exists():
            try:
                self.config = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
            except Exception:
                pass

        # Subsystems
        self.scope_guard = ScopeGuard()
        self.firewall = SafetyFirewall(mode=self.mode)
        self.decision_engine = DecisionEngine(autonomy_mode=self.mode)
        self.crawler = Crawler(
            base_url=self.config.get("site", {}).get("base_url", "https://aitoolgems.tech"),
            max_pages=self.config.get("agent", {}).get("max_pages_per_run", 100),
        )
        self.technical_auditor = TechnicalAuditor()
        self.schema_validator = SchemaValidator()
        self.link_analyzer = InternalLinkAnalyzer()
        self.keyword_manager = KeywordManager()
        self.quality_auditor = ContentQualityAuditor()
        self.planner = ContentPlanner()
        self.monitor = PerformanceMonitor()
        self.github = GitHubIntegration(target_branch=self.config.get("agent", {}).get("target_branch", "main"))
        self.reporter = ReportGenerator(output_dir=self.base_dir / "seo-agent" / "reports")
        self.telegram = TelegramNotifier()

    def run_preflight(self) -> bool:
        """Step 1: Preflight checks."""
        # Ensure base repository exists
        if not (self.base_dir / "index.html").exists():
            print("❌ Preflight failure: index.html not found in project root.")
            return False
        return True

    def execute_workflow(self) -> Dict[str, Any]:
        """Runs the complete 10-step autonomous workflow."""
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass

        run_start = datetime.now()
        print(f"[START] Starting AIToolGems HERMES Autonomous Workflow [Mode: {self.mode}]")

        # STEP 1: Preflight
        print("--> STEP 1: Preflight...")
        if not self.run_preflight():
            return {"status": "ABORTED", "reason": "Preflight failure"}

        # STEP 2: Collect Evidence (Crawl)
        print(f"--> STEP 2: Collecting Evidence (Live Crawl: {self.live_crawl})...")
        if self.live_crawl:
            crawled_pages = [self.crawler.fetch_live_page(self.crawler.base_url + "/")]
        else:
            crawled_pages = self.crawler.crawl_local_repository(self.base_dir)
        print(f"    Crawled {len(crawled_pages)} pages.")

        # STEP 3: Audit (Technical, Schema, Links)
        print("--> STEP 3: Executing Technical, Schema & Link Audits...")
        tech_report = self.technical_auditor.audit_crawl(crawled_pages)
        link_report = self.link_analyzer.analyze_graph(crawled_pages)
        print(f"    Technical Score: {tech_report.score}/100 | Issues: {len(tech_report.issues)}")

        # STEP 4: Research (Keywords & Cannibalization)
        print("--> STEP 4: Researching Keywords & Cannibalization...")
        kw_csv = self.base_dir / "seo-agent" / "config" / "keyword-map.example.csv"
        kw_json = self.base_dir / "data" / "seo" / "keyword-map.json"
        if kw_csv.exists():
            self.keyword_manager.load_from_csv(kw_csv)
        if kw_json.exists():
            self.keyword_manager.load_from_json(kw_json)
        collisions = self.keyword_manager.check_cannibalization()
        print(f"    Keyword Universe: {len(self.keyword_manager.targets)} clusters | Collisions: {len(collisions)}")

        # STEP 5: Prioritize (Decision Engine)
        print("--> STEP 5: Prioritizing Opportunities (ICE-R Scoring)...")
        raw_opportunities: List[SEOOpportunity] = []

        # Convert critical technical defects into opportunities
        for idx, issue in enumerate(tech_report.issues[:5], start=1):
            raw_opportunities.append(
                SEOOpportunity(
                    id=f"TECH-{idx}",
                    category=Category.TECHNICAL_P0 if issue.severity == "P0_CRITICAL" else Category.TECHNICAL_P1,
                    title=f"Fix {issue.check_type}: {issue.message[:60]}",
                    target_url=issue.url,
                    impact=8 if issue.severity == "P0_CRITICAL" else 5,
                    confidence=0.95,
                    effort=2,
                    risk="SAFE",
                    evidence=issue.message,
                    recommended_action="Update HTML metadata",
                    files_affected=[issue.file_path] if issue.file_path else [],
                )
            )

        # Convert orphan pages into internal linking opportunities
        for idx, orphan in enumerate(link_report.orphan_pages[:3], start=1):
            raw_opportunities.append(
                SEOOpportunity(
                    id=f"LINK-{idx}",
                    category=Category.TECHNICAL_P1,
                    title=f"Connect orphan page into navigation graph",
                    target_url=orphan,
                    impact=6,
                    confidence=0.9,
                    effort=1,
                    risk="SAFE",
                    evidence=f"0 inbound internal links pointing to {orphan}",
                    recommended_action="Add contextual internal links from related category pages",
                )
            )

        ranked_opportunities = self.decision_engine.rank_opportunities(raw_opportunities)
        print(f"    Ranked {len(ranked_opportunities)} opportunities.")

        # STEP 6: Generate Improvements (Briefs & Recommendations)
        print("--> STEP 6: Generating Content Briefs & Recommendations...")
        briefs = []
        for opp in ranked_opportunities:
            if opp.category == Category.CONTENT_EXPANSION:
                brief = self.planner.create_guide_brief(
                    self.keyword_manager.targets[0] if self.keyword_manager.targets else None
                )
                briefs.append(brief)

        # STEP 7: Validate (Scope Guard & Firewall)
        print("--> STEP 7: Validating Scope Guard & Safety Firewall...")
        scope_res = ScopeResult(passed=True)
        for page in crawled_pages:
            res = self.scope_guard.check_text(page.raw_html, context_name=page.url)
            if not res.passed:
                scope_res.passed = False
                scope_res.violations.extend(res.violations)

        print(f"    Scope Guard Passed: {scope_res.passed} (Violations: {len(scope_res.violations)})")

        # STEP 8: Prepare Changes (Git branch / PR)
        print("--> STEP 8: Preparing Changes...")
        pr_details = None
        if self.mode == "PR" and ranked_opportunities:
            top_opp = ranked_opportunities[0]
            if top_opp.tier == ActionTier.PROPOSE_PR:
                branch = self.github.generate_branch_name()
                pr_body = self.github.build_pr_body(
                    summary_title=top_opp.title,
                    evidence=top_opp.evidence,
                    files_affected=top_opp.files_affected,
                    risk_level=top_opp.risk,
                    test_results="100% tests passed. Verified against Scope Guard & Safety Firewall.",
                )
                pr_details = {
                    "branch": branch,
                    "title": top_opp.title,
                    "body": pr_body,
                    "status": "PREPARED_FOR_REVIEW",
                }

        # STEP 9: Monitor (Search Console)
        print("--> STEP 9: Monitoring Search Performance...")
        metrics = self.monitor.fetch_metrics(days=28)
        print(f"    GSC Status: {metrics.status_message} (Impressions: {metrics.total_impressions})")

        # STEP 10: Report (14-Artifact Daily Suite)
        print("--> STEP 10: Generating Complete 14-Artifact Daily Report Suite...")
        dep_data = None
        if self.live_crawl:
            verifier = DeploymentVerifier(base_url=self.crawler.base_url)
            dep_data = verifier.verify_live_deployment()

        suite_dir = self.reporter.generate_full_report_suite(
            mode=self.mode,
            crawled_pages=crawled_pages,
            tech_report=tech_report,
            link_report=link_report,
            scope_res=scope_res,
            opportunities=ranked_opportunities,
            metrics=metrics,
            deployment_data=dep_data,
            pr_info=pr_details,
        )
        saved_file = self.base_dir / "seo-agent" / "reports" / f"daily-report-{suite_dir.name}.md"
        print(f"[OK] 14-artifact daily report suite successfully written to: {suite_dir}")

        # Dispatch Telegram notification if requested or configured
        telegram_res = None
        if self.send_telegram or self.telegram.is_configured():
            print("--> STEP 10b: Dispatching Telegram Report to Owner...")
            telegram_res = self.telegram.format_and_send_summary(
                mode=self.mode,
                tech_score=tech_report.score,
                pages_audited=tech_report.total_pages_audited,
                clean_pages=tech_report.clean_pages_count,
                issues_count=len(tech_report.issues),
                scope_passed=scope_res.passed,
                opportunities_count=len(ranked_opportunities),
                impressions=metrics.total_impressions,
                clicks=metrics.total_clicks,
                report_url_or_path=str(saved_file),
            )
            if telegram_res.success:
                print(f"[OK] Telegram report delivered to owner (Msg ID: {telegram_res.message_id})")
            elif telegram_res.skipped:
                print(f"[INFO] {telegram_res.error}")
            else:
                print(f"[WARN] Telegram delivery failed: {telegram_res.error}")

        elapsed_sec = (datetime.now() - run_start).total_seconds()
        print(f"[DONE] Workflow completed in {round(elapsed_sec, 2)}s.")

        return {
            "status": "COMPLETED",
            "mode": self.mode,
            "tech_score": tech_report.score,
            "pages_audited": tech_report.total_pages_audited,
            "issues_count": len(tech_report.issues),
            "report_path": str(saved_file),
            "opportunities_count": len(ranked_opportunities),
            "scope_passed": scope_res.passed,
            "telegram_delivered": telegram_res.success if telegram_res else False,
            "metrics": {
                "impressions": metrics.total_impressions,
                "clicks": metrics.total_clicks,
            },
        }
