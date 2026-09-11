"""Dependency-free daily SEO/GEO integrity monitor for the public website."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .config import Settings
from .telegram import TelegramClient


AI_CRAWLERS = ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot")
REQUIRED_SCHEMA = {"Organization", "WebSite", "ItemList"}


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: int
    content_type: str
    body: str


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


def _fetch(url: str, timeout: int = 20) -> FetchResult:
    request = Request(url, headers={"User-Agent": "AI-Tool-Gems-SEO-Monitor/1.0"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return FetchResult(
            url=response.geturl(), status=int(response.status),
            content_type=response.headers.get("Content-Type", ""),
            body=response.read().decode(charset, errors="replace"),
        )


def inspect_homepage(html: str, canonical_url: str) -> list[str]:
    issues: list[str] = []
    parser = PageSignals()
    parser.feed(html)
    if not 20 <= len(parser.title.strip()) <= 65:
        issues.append("Homepage title length is outside 20–65 characters")
    if not 70 <= len(parser.description.strip()) <= 170:
        issues.append("Homepage meta description length is outside 70–170 characters")
    if parser.canonical.rstrip("/") != canonical_url.rstrip("/"):
        issues.append("Homepage canonical is missing or incorrect")
    if parser.h1_count != 1:
        issues.append(f"Homepage must contain exactly one H1; found {parser.h1_count}")
    schema_types: set[str] = set()
    for raw in parser.schemas:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            issues.append("Homepage contains invalid JSON-LD")
            continue
        nodes = data.get("@graph", []) if isinstance(data, dict) and "@graph" in data else [data]
        for node in nodes:
            if isinstance(node, dict):
                value = node.get("@type")
                schema_types.update(value if isinstance(value, list) else [value] if value else [])
    missing = sorted(REQUIRED_SCHEMA - schema_types)
    if missing:
        issues.append("Homepage missing schema types: " + ", ".join(missing))
    return issues


def _sitemap_urls(xml: str) -> list[str]:
    root = ElementTree.fromstring(xml)
    return [node.text.strip() for node in root.findall("{*}url/{*}loc") if node.text and node.text.strip()]


def audit_site(settings: Settings, fetch: Callable[[str], FetchResult] = _fetch) -> dict:
    site = settings.site_url.rstrip("/")
    issues: list[str] = []
    checked: dict[str, int] = {}

    try:
        sitemap = fetch(f"{site}/sitemap.xml")
        urls = _sitemap_urls(sitemap.body)
    except Exception as exc:
        return {"ok": False, "score": 0, "urls_total": 0, "urls_ok": 0,
                "issues": [f"Sitemap fetch/parse failed: {type(exc).__name__}"]}
    if not urls:
        issues.append("Sitemap contains no URLs")
    if len(urls) != len(set(urls)):
        issues.append("Sitemap contains duplicate URLs")
    if any(not url.startswith(site + "/") for url in urls):
        issues.append("Sitemap contains an off-domain or non-canonical URL")

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                result = future.result()
                checked[url] = result.status
                if result.status != 200:
                    issues.append(f"Non-200 sitemap URL: {url} ({result.status})")
            except Exception as exc:
                checked[url] = 0
                issues.append(f"Unreachable sitemap URL: {url} ({type(exc).__name__})")

    try:
        homepage = fetch(site + "/")
        issues.extend(inspect_homepage(homepage.body, site + "/"))
    except Exception as exc:
        issues.append(f"Homepage SEO inspection failed: {type(exc).__name__}")

    try:
        robots = fetch(f"{site}/robots.txt").body
        for crawler in AI_CRAWLERS:
            if crawler.lower() not in robots.lower():
                issues.append(f"robots.txt does not explicitly mention {crawler}")
        if f"Sitemap: {site}/sitemap.xml" not in robots:
            issues.append("robots.txt sitemap declaration is missing")
    except Exception as exc:
        issues.append(f"robots.txt inspection failed: {type(exc).__name__}")

    try:
        llms = fetch(f"{site}/llms.txt").body
        for required in (site + "/", site + "/deals/", site + "/guides/"):
            if required not in llms:
                issues.append(f"llms.txt missing core URL: {required}")
    except Exception as exc:
        issues.append(f"llms.txt inspection failed: {type(exc).__name__}")

    urls_ok = sum(status == 200 for status in checked.values())
    score = max(0, round(100 - (len(issues) * 7)))
    return {
        "ok": not issues, "score": score, "urls_total": len(urls), "urls_ok": urls_ok,
        "ai_crawlers_checked": list(AI_CRAWLERS), "issues": issues,
    }


def format_report(result: dict) -> str:
    icon = "✅" if result["ok"] else "⚠️"
    issue_lines = "\n".join(f"• {item}" for item in result["issues"][:8]) or "• No SEO/GEO integrity problems detected."
    return (
        f"{icon} AI Tool Gems daily SEO/GEO monitor\n\n"
        f"Integrity score: {result['score']}/100\n"
        f"Sitemap pages reachable: {result['urls_ok']}/{result['urls_total']}\n"
        f"AI crawler policies checked: {len(result.get('ai_crawlers_checked', []))}\n\n"
        f"{issue_lines}\n\n"
        "This checks technical integrity; rankings are measured separately in Google Search Console."
    )


def run_monitor(settings: Settings, send: bool = False) -> dict:
    result = audit_site(settings)
    if send:
        if not settings.owner_reports_ready:
            raise RuntimeError("Owner Telegram credentials are missing")
        TelegramClient(settings.telegram_bot_token).send_with_retry(
            settings.telegram_owner_chat_id, format_report(result), settings.site_url + "/"
        )
    return result
