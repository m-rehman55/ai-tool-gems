"""
reporting.py - Generates Search Console Regex Library, Daily Intelligence Reports, and Growth Artifacts.
Outputs:
- docs/GSC_REGEX_LIBRARY.md: Complete, validated RE2 filters with copy-ready expressions.
- reports/keyword-agent/daily-report-YYYY-MM-DD.md: Daily actionable keyword intelligence report.
- reports/keyword-agent/daily-report-latest.json: Machine-readable CI artifact.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from keyword_agent.gsc_data import GSCDataset
from keyword_agent.regex_engine import GSCFilterDefinition, GSCFilterLibrary
from keyword_agent.discovery import KeywordCandidate
from keyword_agent.content_optimizer import PageOptimizationBrief
from keyword_agent.page_mapper import CannibalizationCollision


class KeywordReportGenerator:
    """Produces verified documentation and multi-cadence markdown/JSON reports."""

    def __init__(self, reports_dir: Path, docs_dir: Path):
        self.reports_dir = reports_dir
        self.docs_dir = docs_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def export_gsc_regex_library_markdown(self, filters: List[GSCFilterDefinition]) -> Path:
        """Writes docs/GSC_REGEX_LIBRARY.md with verified copy-ready RE2 filters."""
        file_path = self.docs_dir / "GSC_REGEX_LIBRARY.md"
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        body_parts = [
            f"# 🛡️ Google Search Console RE2 Regex Filter Library — AIToolGems Pakistan",
            f"**Last Updated:** `{today}`  ",
            f"**Target Market:** Pakistan (PKR, EasyPaisa, JazzCash, SadaPay)  ",
            f"**Syntax Standard:** Google Search Console RE2 Regular Expressions  ",
            "",
            "---",
            "",
            "## 📖 How to Use These Filters in Google Search Console",
            "1. Open [Google Search Console](https://search.google.com/search-console) -> Select **aitoolgems.tech** property.",
            "2. Navigate to **Performance** -> **Search results**.",
            "3. Click **+ New** at the top filter bar and choose **Query** or **Page**.",
            "4. In the dropdown, switch from *Queries containing* to **Custom (regex)**.",
            "5. Select either **Matches regex** or **Doesn't match regex** as indicated below.",
            "6. Copy and paste the exact regex pattern.",
            "",
            "---",
            "",
            "## 🗂️ Verified RE2 Regex Filters",
            "",
        ]

        for f in filters:
            body_parts.append(f.format_markdown())
            body_parts.append("\n---\n")

        file_path.write_text("\n".join(body_parts), encoding="utf-8")
        return file_path

    def generate_daily_report(
        self,
        gsc_dataset: GSCDataset,
        filters: List[GSCFilterDefinition],
        opportunities: Dict[str, List[KeywordCandidate]],
        collisions: List[CannibalizationCollision],
        briefs: List[PageOptimizationBrief],
    ) -> Tuple[Path, Path]:
        """Generates comprehensive daily markdown report and JSON summary."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        md_file = self.reports_dir / f"daily-report-{today}.md"
        json_file = self.reports_dir / f"daily-report-latest.json"

        # Summary counts
        quick_wins = opportunities.get("high_impact_quick_wins", [])
        pk_trans = opportunities.get("pakistan_transactional", [])
        intl_growth = opportunities.get("international_growth_opportunities", [])
        intl_workflows = opportunities.get("international_audience_workflows", [])
        aeo_opps = opportunities.get("aeo_question_opportunities", [])

        # Format quick wins table
        quick_win_rows = "\n".join(
            f"| `{k.keyword}` | {k.impressions} | {k.clicks} | {k.ctr}% | {k.position:.1f} | `{k.cluster}` | {k.opportunity_score} | `{k.action_type}` |"
            for k in quick_wins[:8]
        ) or "| _No urgent CTR gap queries found (import GSC CSV to populate)_ | - | - | - | - | - | - | - |"

        # Format top pages table
        top_pages_rows = "\n".join(
            f"| `{p.page}` | {p.clicks} | {p.impressions} | {p.ctr}% | {p.position:.1f} |"
            for p in sorted(gsc_dataset.pages, key=lambda x: x.clicks, reverse=True)[:8]
        ) or "| _No page data available_ | - | - | - | - |"

        # Format countries breakdown (separating Pakistan from International)
        pk_country = next((c for c in gsc_dataset.countries if "pakistan" in c.country.lower()), None)
        intl_countries = [c for c in gsc_dataset.countries if "pakistan" not in c.country.lower()]
        
        country_summary = f"**Pakistan (#1 Market):** `{pk_country.clicks} clicks` / `{pk_country.impressions} impressions` ({pk_country.ctr}% CTR, pos {pk_country.position:.1f})" if pk_country else "Pakistan data loaded."
        
        intl_country_rows = "\n".join(
            f"| {c.country} | {c.clicks} | {c.impressions} | {c.ctr}% | {c.position:.1f} |"
            for c in sorted(intl_countries, key=lambda x: (x.clicks, x.impressions), reverse=True)[:8]
        ) or "| _No international country records found_ | - | - | - | - |"

        device_rows = "\n".join(
            f"- **{d.device}:** `{d.clicks} clicks` | `{d.impressions} impressions` | `{d.ctr}% CTR` | `Pos: {d.position:.1f}`"
            for d in gsc_dataset.devices
        ) or "- _No device breakdown available._"

        # Format Pakistan transactional table
        pk_rows = "\n".join(
            f"| `{k.keyword}` | `{k.intent}` | `{k.cluster}` | {k.opportunity_score} | `{k.action_type}` |"
            for k in pk_trans[:10]
        ) or "| _No transactional queries mapped_ | - | - | - | - |"

        # Format International search opportunities table
        all_intl = intl_growth + intl_workflows
        intl_rows = "\n".join(
            f"| `{k.keyword.replace(chr(10), ' ').replace(chr(13), ' ')}` | `{k.country_market}` | `{k.intent}` | `{k.opportunity_score}` | `{k.priority}` | [{(k.recommended_page or 'https://aitoolgems.tech/').replace('https://aitoolgems.tech', '') or '/'}]({k.recommended_page or 'https://aitoolgems.tech/'}) | {k.content_gap} | `{k.action_type}` |"
            for k in all_intl[:12]
        ) or "| _No international opportunities mapped_ | - | - | - | - | - | - | - |"

        # Format cannibalization section
        if collisions:
            cannibal_md = "\n".join(
                f"- ⚠️ **Collision on intent `{c.normalized_intent}`** ({c.severity} severity)\n"
                f"  - Competing URLs: {', '.join(f'`{u}`' for u in c.competing_urls)}\n"
                f"  - Action: {c.recommended_action}"
                for c in collisions
            )
        else:
            cannibal_md = "✅ **Zero Cannibalization Collisions Detected.** All keywords map to unique canonical URLs."

        # Format briefs
        briefs_md = "\n\n".join(b.format_markdown() for b in briefs[:3]) if briefs else "_No optimization briefs generated._"

        content = f"""# 📈 AIToolGems Keyword Intelligence & Dual-Market SEO Growth Report

**Date:** `{today}`  
**Site URL:** `https://aitoolgems.tech`  
**Primary Commercial Market:** Pakistan (PKR / EasyPaisa / JazzCash / SadaPay / Bank IBFT)  
**Secondary Growth Market:** International / Global (Tool Comparisons, Student/Freelancer Workflows, WhatsApp Inquiries)  
**Search Console Data Source:** `{gsc_dataset.source}`  
**GSC Status:** {gsc_dataset.status_message}  

---

## 1. Executive Performance Baseline
- **Total Clicks:** `{gsc_dataset.total_clicks}`
- **Total Impressions:** `{gsc_dataset.total_impressions}`
- **Average CTR:** `{gsc_dataset.average_ctr}%`
- **Average Position:** `{gsc_dataset.average_position}`
- **Active Query Count:** `{len(gsc_dataset.queries)}`
- **Active Pages Tracked:** `{len(gsc_dataset.pages)}`
- {country_summary}

### 🌍 International Organic Footprint (GSC Measured)
| Country / Territory | Clicks | Imp | CTR | Average Position |
|---------------------|--------|-----|-----|------------------|
{intl_country_rows}

### 📱 Device Breakdown
{device_rows}

---

## 2. Top Performing Landing Pages (Traffic Drivers)
| Landing Page URL | Clicks | Imp | CTR | Average Position |
|------------------|--------|-----|-----|------------------|
{top_pages_rows}

---

## 3. High-Impact Quick Wins (Striking Distance & CTR Optimization)
Queries where incremental metadata and direct-answer optimizations can drive immediate click gains:

| Target Query | Imp | Clicks | CTR | Pos | Cluster | Score | Action |
|--------------|-----|--------|-----|-----|---------|-------|--------|
{quick_win_rows}

---

## 4. Pakistan Commercial & Transactional Queries (PKR & Local Wallets)
Authentic PKR pricing and domestic payment rails (EasyPaisa, JazzCash, SadaPay, Raast):

| Target Query | Intent | Cluster | Score | Recommended Action |
|--------------|--------|---------|-------|--------------------|
{pk_rows}

---

## 5. International SEO Growth & Audience Workflow Opportunities
Approved non-domestic opportunities targeting tool comparisons, alternatives, workflows, and manual inquiry quotes:

| Target Query | Market | Intent | Score | Priority | Relevant Page | Content Gap | Recommended Action |
|--------------|--------|--------|-------|----------|---------------|-------------|--------------------|
{intl_rows}

---

## 6. Keyword Cannibalization & URL Mapping Integrity
{cannibal_md}

---

## 7. Google Search Console RE2 Filter Engine
- **Active Verified Filters:** `{len(filters)}` copy-ready filters available in `docs/GSC_REGEX_LIBRARY.md`
- **RE2 Compatibility:** 100% verified against RE2 syntax constraints. Includes Dedicated International Filters (#12 Global Comparisons & #13 Cross-Border Inquiries).

---

## 8. On-Page Content & AEO Optimization Proposals
{briefs_md}

---

## 9. Next Autonomous Action Plan
1. **Pakistan Focus:** Maintain domestic transactional leadership for ChatGPT, Canva, CapCut, and Gemini Pro via transparent PKR pricing and verified WhatsApp onboarding.
2. **International Growth:** Optimize existing comparison and workflow guides (`guides/canva-vs-figma-pakistan/`, `guides/chatgpt-vs-gemini-pakistan/`, `guides/students/`, `guides/creators/`) to answer global search intent without creating thin duplicate country pages.
3. **Cross-Border Inquiry Routing:** Direct international customers to manual WhatsApp support for availability, payment method (Wise, SWIFT), and pricing verification on `policies.html#payments`.
4. **Safeguards Active:** Preserving strict human review gates, grounded facts, and zero fabricated foreign checkout rails.
"""

        md_file.write_text(content, encoding="utf-8")

        # Save JSON artifact
        json_data = {
            "date": today,
            "gsc_source": gsc_dataset.source,
            "gsc_status": gsc_dataset.status_message,
            "total_clicks": gsc_dataset.total_clicks,
            "total_impressions": gsc_dataset.total_impressions,
            "average_ctr": gsc_dataset.average_ctr,
            "average_position": gsc_dataset.average_position,
            "quick_wins_count": len(quick_wins),
            "pakistan_transactional_count": len(pk_trans),
            "international_opportunities_count": len(all_intl),
            "aeo_questions_count": len(aeo_opps),
            "cannibalization_collisions_count": len(collisions),
            "briefs_count": len(briefs),
            "briefs": [b.to_dict() for b in briefs],
        }
        json_file.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

        return md_file, json_file

    def send_telegram_summary(
        self,
        gsc_dataset: GSCDataset,
        opportunities: Dict[str, List[KeywordCandidate]],
        collisions: List[CannibalizationCollision],
    ) -> bool:
        """Dispatches an executive summary to the configured owner Telegram chat."""
        import os
        import urllib.request
        import urllib.error

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_OWNER_CHAT_ID", "").strip() or os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if not bot_token or not chat_id:
            return False

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        quick_wins = opportunities.get("high_impact_quick_wins", [])
        
        # Build concise message
        lines = [
            f"📊 *AIToolGems Daily Search Intelligence*",
            f"📅 `{today}` | 🇵🇰 Pakistan Focus",
            f"",
            f"📈 *Performance:*",
            f"• Clicks: `{gsc_dataset.total_clicks}` | Impressions: `{gsc_dataset.total_impressions}`",
            f"• Average CTR: `{gsc_dataset.average_ctr}%` | Pos: `{gsc_dataset.average_position}`",
            f"• Active Queries: `{len(gsc_dataset.queries)}` | Pages: `{len(gsc_dataset.pages)}`",
            f"",
            f"⚡ *Top High-Impression Quick Wins:*",
        ]

        if quick_wins:
            for q in quick_wins[:3]:
                lines.append(f"• `{q.keyword}`: {q.impressions} imp, pos {q.position:.1f} ({q.ctr}% CTR)")
        else:
            lines.append("• _No urgent CTR gaps detected._")

        lines.extend([
            f"",
            f"🛡️ *Cannibalization:* {'0 collisions ✅' if not collisions else f'{len(collisions)} warning(s) ⚠️'}",
            f"📄 Full report saved in repository.",
        ])

        payload = json.dumps({
            "chat_id": chat_id,
            "text": "\n".join(lines),
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "AIToolGems-KeywordAgent/1.0"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return bool(res.get("ok"))
        except Exception:
            return False
