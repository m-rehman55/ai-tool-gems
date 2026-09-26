"""
SEO Growth Agent — daily optimization engine for aitoolgems.tech.

Daily tasks:
1. Indexing audit — all sitemap URLs, reachability + meta health
2. GSC performance — impressions, clicks, CTR, position trends
3. Keyword opportunity detection — high impressions + low CTR = optimize
4. Competitor presence check — who ranks for target keywords
5. Top pages analysis — which pages drive traffic, which need work
6. Action items generation — what to do today
7. Learning notes — track what improves
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dataclasses import dataclass, field
from typing import Any
from html.parser import HTMLParser
from xml.etree import ElementTree

from .config import Settings
from .search_apis import GSCClient, BingClient
from .telegram import TelegramClient

# ── Target keywords (Pakistan + Japan) ────────────────────────────────────────

TARGET_KEYWORDS_PK = [
    "ai tools pakistan",
    "ai tools price in pakistan",
    "chatgpt plus price pakistan",
    "canva pro price pakistan",
    "netflix premium price pakistan",
    "adobe creative cloud price pakistan",
    "ai tools marketplace pakistan",
    "buy ai tools pakistan",
    "premium ai tools pakistan",
    "ai subscriptions pakistan",
    "ai tool gems",
    "ai tool gems pakistan",
]

TARGET_KEYWORDS_JP = [
    "aiツール 日本",
    "aiツール 価格 日本",
    "chatgpt plus 日本価格",
    "canva pro 日本価格",
    "netflix premium 日本価格",
    "aiマーケットプレイス 日本",
    "aiツール 購入 日本",
    "ai tool gems japan",
    "aitoolgems",
]

# Competitor domains to watch
COMPETITOR_DOMAINS = [
    "aitools.com",
    "futurepedia.io",
    "theresanaiforthat.com",
    "topai.tools",
    "ai-tool-lab.com",
    "there's an ai for that",
]

# ── HTML Parser (reuse from seo_monitor) ──────────────────────────────────────

class PageSignals(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.h1_count = 0
        self.schemas: list[str] = []
        self._in_title = False
        self._in_schema = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta" and values.get("name", "").lower() == "description":
            self.description = values.get("content") or ""
        elif tag == "link" and values.get("rel", "").lower() == "canonical":
            self.canonical = values.get("href") or ""
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._in_schema = True
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._in_schema:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_schema:
            self.schemas.append("".join(self._buffer))
            self._in_schema = False


def _fetch(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": "AI-Tool-Gems-SEO-Agent/1.0"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def _sitemap_urls(sitemap_xml: str) -> list[str]:
    root = ElementTree.fromstring(sitemap_xml)
    return [node.text.strip() for node in root.findall("{*}url/{*}loc") if node.text and node.text.strip()]


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class SEOInsight:
    category: str
    page: str | None
    severity: str
    description: str
    action: str
    impact: str


@dataclass
class DailySEOReport:
    date: str
    site_health_score: int
    indexing_status: dict[str, Any]
    gsc_performance: dict[str, Any]
    keyword_opportunities: list[dict[str, Any]]
    competitor_snapshot: dict[str, Any]
    top_pages: list[dict[str, Any]]
    pages_needing_work: list[dict[str, Any]]
    action_items: list[dict[str, Any]]
    learning_notes: list[str]
    insights: list[SEOInsight]


# ── SEO Optimizer ─────────────────────────────────────────────────────────────

class SEOOptimizer:
    """Daily SEO growth agent."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.site_url = settings.site_url.rstrip("/")
        gsc_id = os.getenv("GSC_CLIENT_ID", "").strip()
        gsc_secret = os.getenv("GSC_CLIENT_SECRET", "").strip()
        bing_key = os.getenv("BING_API_KEY", "").strip()
        self.gsc = GSCClient(gsc_id, gsc_secret, self.site_url) if gsc_id and gsc_secret else None
        self.bing = BingClient(bing_key, self.site_url) if bing_key else None

    # ── Indexing Audit ─────────────────────────────────────────────────────────

    def audit_indexing(self) -> dict[str, Any]:
        issues: list[dict[str, Any]] = []
        checked: dict[str, int] = {}
        healthy: dict[str, bool] = {}

        try:
            sitemap_main = _fetch(f"{self.site_url}/sitemap.xml")
            urls_main = _sitemap_urls(sitemap_main)
            sitemap_jp = _fetch(f"{self.site_url}/sitemap-jp.xml")
            urls_jp = _sitemap_urls(sitemap_jp)
            all_urls = urls_main + urls_jp
        except Exception as exc:
            return {
                "error": str(exc),
                "total_urls": 0,
                "reachable": 0,
                "healthy_meta": 0,
                "indexing_score": 0,
                "issues": [{"page": None, "issue": f"Sitemap fetch failed: {exc}"}],
            }

        for url in all_urls:
            try:
                html = _fetch(url, timeout=10)
                checked[url] = 200
                parser = PageSignals()
                parser.feed(html)
                page_issues: list[str] = []
                if not parser.title.strip():
                    page_issues.append("Missing title")
                if not parser.description.strip():
                    page_issues.append("Missing meta description")
                if not parser.canonical.strip():
                    page_issues.append("Missing canonical")
                elif parser.canonical.rstrip("/") != url.rstrip("/"):
                    page_issues.append(f"Canonical → {parser.canonical}")
                healthy[url] = len(page_issues) == 0
                if page_issues:
                    issues.append({"page": url, "issues": page_issues})
            except Exception as exc:
                checked[url] = 0
                healthy[url] = False
                issues.append({"page": url, "issue": f"Unreachable: {exc}"})

        reachable = sum(1 for s in checked.values() if s == 200)
        healthy_count = sum(1 for v in healthy.values() if v)
        total = len(all_urls)

        return {
            "total_urls": total,
            "reachable": reachable,
            "healthy_meta": healthy_count,
            "unhealthy_pages": len(issues),
            "indexing_score": round((healthy_count / total) * 100) if total else 0,
            "issues": issues[:20],
        }

    # ── GSC Performance ────────────────────────────────────────────────────────

    def analyze_gsc(self, days: int = 7) -> dict[str, Any]:
        if not self.gsc:
            return {"error": "GSC not configured"}

        today = date.today()
        start = (today - timedelta(days=days)).isoformat()
        end = today.isoformat()

        try:
            rows = self.gsc.query_analytics(start, end, ("query", "page"), 50)
        except Exception as exc:
            return {"error": str(exc)}

        query_data: dict[str, dict[str, Any]] = {}
        for row in rows:
            keys = row.get("keys", [])
            q = keys[0] if keys else "unknown"
            p = keys[1] if len(keys) > 1 else None
            if q not in query_data:
                query_data[q] = {"query": q, "pages": [], "impressions": 0, "clicks": 0, "ctr": 0.0, "position": 0.0}
            e = query_data[q]
            e["impressions"] += int(row.get("impressions", 0))
            e["clicks"] += int(row.get("clicks", 0))
            if row.get("ctr"):
                e["ctr"] = float(row.get("ctr"))
            if row.get("position"):
                e["position"] = float(row.get("position"))
            if p and p not in e["pages"]:
                e["pages"].append(p)

        sorted_q = sorted(query_data.values(), key=lambda x: x["impressions"], reverse=True)
        total_imp = sum(q["impressions"] for q in sorted_q)
        total_clk = sum(q["clicks"] for q in sorted_q)
        ctr = (total_clk / total_imp * 100) if total_imp else 0
        avg_pos = sum(q["position"] for q in sorted_q) / len(sorted_q) if sorted_q else 0

        opportunities = []
        zero_click = []
        for q in sorted_q:
            c = (q["clicks"] / q["impressions"] * 100) if q["impressions"] else 0
            if q["impressions"] >= 5 and c < 2.0:
                opportunities.append({
                    "query": q["query"],
                    "impressions": q["impressions"],
                    "clicks": q["clicks"],
                    "ctr": round(c, 2),
                    "position": round(q["position"], 1),
                    "action": f"Optimize title & meta description for '{q['query']}'",
                    "impact": "high",
                })
            if q["clicks"] == 0 and q["impressions"] >= 3:
                zero_click.append({
                    "query": q["query"],
                    "impressions": q["impressions"],
                    "position": round(q["position"], 1),
                    "action": f"Improve ranking for '{q['query']}' — currently position {q['position']}",
                    "impact": "medium",
                })

        return {
            "period": f"{start} → {end}",
            "total_impressions": total_imp,
            "total_clicks": total_clk,
            "overall_ctr": round(ctr, 2),
            "avg_position": round(avg_pos, 2),
            "queries_tracked": len(sorted_q),
            "top_queries": sorted_q[:10],
            "opportunities": opportunities,
            "zero_click_queries": zero_click,
        }

    # ── Competitor Check ───────────────────────────────────────────────────────

    def check_competitors(self) -> dict[str, Any]:
        """Check where we and competitors rank for target keywords.
        Uses web_search to simulate Google results.
        """
        all_keywords = TARGET_KEYWORDS_PK + TARGET_KEYWORDS_JP
        results: dict[str, Any] = {}

        for kw in all_keywords:
            try:
                from hermes_tools import web_search
                search_result = web_search(kw, limit=10)
                web_data = search_result.get("data", {}).get("web", [])
                our_rank = None
                comps: list[dict[str, Any]] = []
                top_domains: list[dict[str, Any]] = []

                for i, item in enumerate(web_data[:10]):
                    url = item.get("url", "")
                    domain = url.split("/")[2] if "://" in url and len(url.split("/")) > 2 else ""
                    top_domains.append({"position": i + 1, "domain": domain, "title": (item.get("title") or "")[:80]})
                    if domain == "aitoolgems.tech":
                        our_rank = i + 1
                    if any(c in domain for c in COMPETITOR_DOMAINS):
                        comps.append({"position": i + 1, "domain": domain})

                results[kw] = {
                    "our_rank": our_rank,
                    "competitors": comps,
                    "top_10": top_domains,
                    "status": "ranked" if our_rank and our_rank <= 10 else "not_ranked" if our_rank is None else f"ranked#{our_rank}",
                }
            except Exception as exc:
                results[kw] = {"error": str(exc), "status": "error"}

        return results

    # ── Top Pages ──────────────────────────────────────────────────────────────

    def analyze_top_pages(self, days: int = 7) -> dict[str, Any]:
        if not self.gsc:
            return {"error": "GSC not configured"}

        today = date.today()
        start = (today - timedelta(days=days)).isoformat()
        end = today.isoformat()

        try:
            rows = self.gsc.query_analytics(start, end, ("page",), 50)
        except Exception as exc:
            return {"error": str(exc)}

        pages: dict[str, dict[str, Any]] = {}
        for row in rows:
            p = row.get("keys", [None])[0]
            if not p:
                continue
            if p not in pages:
                pages[p] = {"page": p, "impressions": 0, "clicks": 0, "ctr": 0.0, "position": 0.0}
            e = pages[p]
            e["impressions"] += int(row.get("impressions", 0))
            e["clicks"] += int(row.get("clicks", 0))
            if row.get("ctr"):
                e["ctr"] = float(row.get("ctr"))
            if row.get("position"):
                e["position"] = float(row.get("position"))

        sorted_by_clicks = sorted(pages.values(), key=lambda x: x["clicks"], reverse=True)
        sorted_by_imp = sorted(pages.values(), key=lambda x: x["impressions"], reverse=True)
        no_clicks = [p for p in sorted_by_imp if p["clicks"] == 0 and p["impressions"] >= 5]

        return {
            "top_by_clicks": sorted_by_clicks[:10],
            "top_by_impressions": sorted_by_imp[:10],
            "no_click_pages": no_clicks,
        }

    # ── Action Items ───────────────────────────────────────────────────────────

    def generate_actions(self, report: DailySEOReport) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []

        for issue in report.indexing_status.get("issues", []):
            items.append({
                "priority": "high",
                "type": "technical",
                "task": f"Fix {', '.join(issue['issues'])} → {issue['page']}",
                "impact": "improves indexing",
            })

        for opp in report.gsc_performance.get("opportunities", []):
            items.append({
                "priority": "high",
                "type": "content",
                "task": f"Optimize '{opp['query'][:50]}' — {opp['impressions']} imp, {opp['ctr']}% CTR",
                "impact": opp.get("impact", "high"),
            })

        for qc in report.gsc_performance.get("zero_click_queries", []):
            items.append({
                "priority": "medium",
                "type": "ranking",
                "task": f"Improve rank for '{qc['query'][:50]}' — pos {qc['position']}, {qc['impressions']} imp",
                "impact": qc.get("impact", "medium"),
            })

        for page in report.gsc_performance.get("no_click_pages", [])[:5]:
            items.append({
                "priority": "medium",
                "type": "content",
                "task": f"Convert impressions to clicks: {page['page']} ({page['impressions']} imp, 0 clicks)",
                "impact": "medium",
            })

        return items[:15]

    # ── Main Run ───────────────────────────────────────────────────────────────

    def run_daily(self) -> DailySEOReport:
        print(f"🔍 SEO Growth Agent running for {self.site_url}...")

        print("  📋 Indexing audit...")
        indexing = self.audit_indexing()

        print("  📊 GSC performance...")
        gsc = self.analyze_gsc()

        print("  🕵️ Competitor check...")
        competitors = self.check_competitors()

        print("  📈 Top pages...")
        top_pages = self.analyze_top_pages()

        report = DailySEOReport(
            date=date.today().isoformat(),
            site_health_score=indexing.get("indexing_score", 0),
            indexing_status=indexing,
            gsc_performance=gsc,
            keyword_opportunities=gsc.get("opportunities", []),
            competitor_snapshot=competitors,
            top_pages=top_pages.get("top_by_clicks", []),
            pages_needing_work=top_pages.get("no_click_pages", [])[:5],
            action_items=[],
            learning_notes=[],
            insights=[],
        )

        report.action_items = self.generate_actions(report)

        notes = []
        if gsc.get("total_impressions", 0) > 0:
            notes.append(f"Impressions: {gsc['total_impressions']}, Clicks: {gsc['total_clicks']}, CTR: {gsc['overall_ctr']}%, Avg pos: {gsc['avg_position']}")
        if len(report.keyword_opportunities) > 0:
            notes.append(f"Found {len(report.keyword_opportunities)} CTR optimization opportunities")
        if len(report.pages_needing_work) > 0:
            notes.append(f"{len(report.pages_needing_work)} pages have impressions but 0 clicks")
        if competitors:
            our_ranked = sum(1 for v in competitors.values() if isinstance(v, dict) and v.get("our_rank") and v["our_rank"] <= 10)
            notes.append(f"Ranked for {our_ranked}/{len(competitors)} target keywords")
        report.learning_notes = notes

        return report


# ── Report Formatting ──────────────────────────────────────────────────────────

def format_report(report: DailySEOReport) -> str:
    lines: list[str] = []
    lines.append("📊 AI Tool Gems — Daily SEO Growth Report")
    lines.append("")
    lines.append(f"📅 {report.date}")
    lines.append(f"🏥 Site Health: {report.site_health_score}/100")
    lines.append("")

    idx = report.indexing_status
    if "error" not in idx:
        lines.append("📋 Indexing:")
        lines.append(f"  URLs: {idx.get('total_urls', 0)} | Reachable: {idx.get('reachable', 0)} | Healthy: {idx.get('healthy_meta', 0)}")
        lines.append(f"  Score: {idx.get('indexing_score', 0)}/100")
        if idx.get("unhealthy_pages", 0) > 0:
            lines.append(f"  ⚠️ {idx['unhealthy_pages']} pages need fixing")
            for issue in idx.get("issues", [])[:5]:
                if issue.get("page"):
                    lines.append(f"    🔧 {issue['page']} — {', '.join(issue['issues'])}")
                else:
                    lines.append(f"    🔧 {issue['issue']}")
        lines.append("")

    gsc = report.gsc_performance
    if "error" not in gsc:
        lines.append("📊 GSC Performance:")
        lines.append(f"  Period: {gsc.get('period', '?')}")
        lines.append(f"  Impressions: {gsc.get('total_impressions', 0):,} | Clicks: {gsc.get('total_clicks', 0):,} | CTR: {gsc.get('overall_ctr', 0)}% | Avg Pos: {gsc.get('avg_position', 0)}")
        lines.append(f"  Queries: {gsc.get('queries_tracked', 0)}")
        lines.append("")

        if gsc.get("top_queries"):
            lines.append("🏆 Top Queries:")
            for q in gsc["top_queries"][:5]:
                lines.append(f"  • {q['query'][:55]}")
                lines.append(f"    {q['impressions']} imp | {q['clicks']} clicks | CTR {q['ctr']}% | Pos {q['position']}")
            lines.append("")

        if gsc.get("opportunities"):
            lines.append("⚡ CTR Opportunities (optimize title/meta):")
            for opp in gsc["opportunities"][:5]:
                lines.append(f"  • '{opp['query'][:45]}' — {opp['impressions']} imp, {opp['ctr']}% CTR")
            lines.append("")

        if gsc.get("zero_click_queries"):
            lines.append("⚠️ Zero-Click Queries (improve ranking):")
            for qc in gsc["zero_click_queries"][:5]:
                lines.append(f"  • '{qc['query'][:45]}' — {qc['impressions']} imp, 0 clicks, pos {qc['position']}")
            lines.append("")

    comp = report.competitor_snapshot
    if comp:
        lines.append("🕵️ Competitor Presence:")
        our_ranked = 0
        for kw, data in comp.items():
            if isinstance(data, dict) and data.get("our_rank"):
                our_ranked += 1
                lines.append(f"  ✓ '{kw[:35]}' — We: #{data['our_rank']}")
            elif isinstance(data, dict) and data.get("status") == "not_ranked":
                lines.append(f"  ✗ '{kw[:35]}' — Not in top 10 yet")
        if our_ranked == 0 and len(comp) > 0:
            lines.append("  No target keywords ranked in top 10 — building authority")
        lines.append("")

    if report.action_items:
        lines.append("✅ Today's Actions:")
        for i, item in enumerate(report.action_items[:10], 1):
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(item["priority"], "⚪")
            lines.append(f"  {icon} {i}. [{item['priority'].upper()}] {item['task']}")
        lines.append("")

    if report.learning_notes:
        lines.append("📝 Learning Notes:")
        for n in report.learning_notes:
            lines.append(f"  • {n}")
        lines.append("")

    lines.append("— AI Tool Gems SEO Growth Agent")

    return "\n".join(lines)


def run_daily(send: bool = False) -> str:
    settings = Settings(
        database_path=__import__("pathlib").Path("marketing_agent/data/marketing.db"),
        site_url=os.getenv("ATG_SITE_URL", "https://aitoolgems.tech"),
        whatsapp_number="923236715731",
        timezone=__import__("zoneinfo").ZoneInfo("Asia/Karachi"),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_channel_id=os.getenv("TELEGRAM_CHANNEL_ID", "").strip(),
        telegram_owner_chat_id=os.getenv("TELEGRAM_OWNER_CHAT_ID", "").strip(),
        buffer_api_key=os.getenv("BUFFER_API_KEY", "").strip(),
        posts_per_day=3,
        auto_approve=False,
        gsc_client_id=os.getenv("GSC_CLIENT_ID", "").strip(),
        gsc_client_secret=os.getenv("GSC_CLIENT_SECRET", "").strip(),
        bing_api_key=os.getenv("BING_API_KEY", "").strip(),
    )

    optimizer = SEOOptimizer(settings)
    report = optimizer.run_daily()
    message = format_report(report)

    if send and settings.telegram_owner_chat_id and settings.telegram_bot_token:
        TelegramClient(settings.telegram_bot_token).send_with_retry(
            settings.telegram_owner_chat_id, message, settings.site_url + "/"
        )
        print("→ Telegram report sent.")

    return message
