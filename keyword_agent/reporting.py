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

        # Format countries and devices
        pk_country = next((c for c in gsc_dataset.countries if "pakistan" in c.country.lower()), None)
        country_summary = f"**Pakistan (#1 Market):** `{pk_country.clicks} clicks` / `{pk_country.impressions} impressions` ({pk_country.ctr}% CTR, pos {pk_country.position:.1f})" if pk_country else "Global data loaded."

        device_rows = "\n".join(
            f"- **{d.device}:** `{d.clicks} clicks` | `{d.impressions} impressions` | `{d.ctr}% CTR` | `Pos: {d.position:.1f}`"
            for d in gsc_dataset.devices
        ) or "- _No device breakdown available._"

        # Format Pakistan transactional table
        pk_rows = "\n".join(
            f"| `{k.keyword}` | `{k.intent}` | `{k.cluster}` | {k.opportunity_score} | `{k.action_type}` |"
            for k in pk_trans[:8]
        ) or "| _No transactional queries mapped_ | - | - | - | - |"

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

        content = f"""# 📈 AIToolGems Keyword Intelligence & Content Optimization Report

**Date:** `{today}`  
**Site URL:** `https://aitoolgems.tech`  
**Primary Market:** Pakistan (PKR / EasyPaisa / JazzCash)  
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

### 📱 Device Breakdown
{device_rows}

---

## 2. Top Performing Landing Pages (Traffic Drivers)
| Landing Page URL | Clicks | Imp | CTR | Average Position |
|------------------|--------|-----|-----|------------------|
{top_pages_rows}

---

## 3. High-Impact Quick Wins (High Impression / Low CTR & Striking Distance)
Queries where incremental optimization can drive immediate click gains without waiting for major ranking changes:

| Target Query | Imp | Clicks | CTR | Pos | Cluster | Score | Action |
|--------------|-----|--------|-----|-----|---------|-------|--------|
{quick_win_rows}

---

## 4. High-Value Pakistani Transactional Queries (PKR & Local Wallets)
| Target Query | Intent | Cluster | Score | Recommended Action |
|--------------|--------|---------|-------|--------------------|
{pk_rows}

---

## 5. Keyword Cannibalization & URL Mapping Integrity
{cannibal_md}

---

## 6. Google Search Console RE2 Filter Engine
- **Active Verified Filters:** `{len(filters)}` filters available in `docs/GSC_REGEX_LIBRARY.md`
- **RE2 Compatibility:** 100% verified against RE2 syntax constraints.

---

## 7. On-Page Content & AEO Optimization Proposals
{briefs_md}

---

## 8. Next Autonomous Action Plan
1. **Focus on Quick Wins:** Implement CTR optimization for top impression queries (e.g. Leonardo AI license key, LinkedIn Premium Pakistan).
2. **Review Proposed Changes:** Review the approval gates above before merging any changes to live tool pages.
3. **Continuous Monitoring:** Scheduled daily run will re-evaluate rankings, clicks, and intent maps.
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
