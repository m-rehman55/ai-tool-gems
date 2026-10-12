#!/usr/bin/env python3
"""
Daily Reporting Engine for AIToolGems Growth Agent
--------------------------------------------------
Generates comprehensive, evidence-backed daily Markdown and JSON reports:
- Executive summary & health status.
- Technical & schema audit results.
- Scope guard & zero-JP confirmation.
- Google Search Console performance trends.
- Prioritized opportunities with ICE-R scores.
- Safety & rollback disclosures.
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from agent.technical_audit import TechnicalAuditReport
from agent.decision_engine import SEOOpportunity, ActionTier
from agent.monitoring import PerformanceMetrics
from agent.scope_guard import ScopeResult
from agent.safety_firewall import SafetyFirewall

class ReportGenerator:
    """Produces clean, executive and technical daily audit reports."""

    def __init__(self, output_dir: Path | str = "seo-agent/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.firewall = SafetyFirewall()

    def generate_markdown_report(
        self,
        mode: str,
        tech_report: TechnicalAuditReport,
        scope_res: ScopeResult,
        opportunities: List[SEOOpportunity],
        metrics: PerformanceMetrics,
        pr_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # P0/P1/P2 counts
        p0 = tech_report.issues_by_severity.get("P0_CRITICAL", 0)
        p1 = tech_report.issues_by_severity.get("P1_HIGH", 0)
        p2 = tech_report.issues_by_severity.get("P2_MEDIUM", 0)
        
        # Format top queries table
        queries_md = ""
        if metrics.top_queries:
            q_rows = "\n".join(
                f"| `{q.query}` | {q.impressions} | {q.clicks} | {q.ctr}% | {q.position} |"
                for q in metrics.top_queries[:8]
            )
            queries_md = f"""
| Query | Impressions | Clicks | CTR | Position |
|-------|-------------|--------|-----|----------|
{q_rows}
"""
        else:
            queries_md = f"_{metrics.status_message}_\n"

        # Format opportunities table
        opps_md = ""
        if opportunities:
            opp_rows = "\n".join(
                f"| `{o.id}` | {o.tier.value} | {o.score} | {o.title} | {o.risk} |"
                for o in opportunities[:10]
            )
            opps_md = f"""
| ID | Action Tier | Score | Opportunity | Risk |
|----|-------------|-------|-------------|------|
{opp_rows}
"""
        else:
            opps_md = "_No urgent opportunities flagged during this run._\n"

        # Scope status
        scope_status = "✅ PASS (100% Pakistan Exclusive, Zero Foreign/JP Contamination)" if scope_res.passed else f"❌ VIOLATION ({len(scope_res.violations)} issues)"

        report = f"""# 📈 AIToolGems Autonomous SEO Growth Report

**Run Timestamp:** `{date_str}`  
**Operational Mode:** `{mode.upper()}`  
**Scope Guard:** {scope_status}  
**Technical SEO Score:** `{tech_report.score}/100`  

---

## 1. Executive Summary & Health Check

- **Pages Audited:** `{tech_report.total_pages_audited}`
- **Clean Pages:** `{tech_report.clean_pages_count}`
- **Technical Issues:** `{len(tech_report.issues)}` (P0: `{p0}`, P1: `{p1}`, P2: `{p2}`)
- **Search Console Status:** `{metrics.status_message}`
  - **Live Impressions (28d):** `{metrics.total_impressions}`
  - **Live Clicks (28d):** `{metrics.total_clicks}`
  - **Average CTR:** `{metrics.average_ctr}%`
  - **Average Position:** `{metrics.average_position}`

---

## 2. Search Console Performance & Queries
{queries_md}

---

## 3. Prioritized Growth Opportunities (ICE-R Ranked)
{opps_md}

---

## 4. Technical Audit Defects (Top Issues)
"""
        if tech_report.issues:
            for idx, issue in enumerate(tech_report.issues[:8], start=1):
                report += f"- **[{issue.severity}]** `{issue.check_type}` on `{issue.url}`: {issue.message}\n"
        else:
            report += "- ✅ Zero technical defects found across all audited pages.\n"

        report += f"""
---

## 5. Scope & Safety Disclosures
- **Production Firewall:** Active. Direct writes to `main` are blocked.
- **Price Policy Freeze:** Active. Product prices require explicit human approval.
- **Rollback Guidance:** Any proposed branch can be abandoned or reverted with `git checkout main && git reset --hard origin/main`.

---
*Report generated autonomously by AIToolGems HERMES SEO Growth Agent.*
"""
        return self.firewall.redact_secrets(report)

    def save_report(self, markdown_content: str, filename_prefix: str = "daily-report") -> Path:
        date_stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filepath = self.output_dir / f"{filename_prefix}-{date_stamp}.md"
        filepath.write_text(markdown_content, encoding="utf-8")
        return filepath
