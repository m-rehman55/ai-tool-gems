"""Offline repository and online production SEO audits for Hermes."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .hermes_models import ActionDecision, SEOAction


class _HTMLSignals(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.h1_count = 0
        self.hreflang: list[dict[str, str]] = []
        self.links: list[str] = []
        self.images: list[dict[str, str]] = []
        self.schemas: list[dict] = []
        self.noindex = False
        self._title = False
        self._jsonld = False
        self._jsonld_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag == "title":
            self._title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            name = values.get("name", "").lower()
            if name == "description":
                self.description = values.get("content", "")
            if name == "robots" and "noindex" in values.get("content", "").lower():
                self.noindex = True
        elif tag == "link":
            rel = values.get("rel", "").lower()
            if rel == "canonical":
                self.canonical = values.get("href", "")
            if rel == "alternate" and values.get("hreflang") and values.get("href"):
                self.hreflang.append({"hreflang": values["hreflang"], "href": values["href"]})
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"])
        elif tag == "img":
            self.images.append({"src": values.get("src", ""), "alt": values.get("alt", "")})
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._jsonld = True
            self._jsonld_buffer = []

    def handle_data(self, data: str) -> None:
        if self._title:
            self.title += data
        if self._jsonld:
            self._jsonld_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._title = False
        elif tag == "script" and self._jsonld:
            try:
                parsed = json.loads("".join(self._jsonld_buffer))
                self.schemas.append(parsed)
            except json.JSONDecodeError:
                self.schemas.append({"_invalid_jsonld": True})
            self._jsonld = False


@dataclass
class OfflineAudit:
    pages: list[dict] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)
    sitemaps: dict[str, dict] = field(default_factory=dict)
    robots: dict = field(default_factory=dict)
    links: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)
    actions: list[SEOAction] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "pages": self.pages,
            "issues": self.issues,
            "sitemaps": self.sitemaps,
            "robots": self.robots,
            "links": self.links,
            "summary": self.summary,
            "actions": [action.to_dict() for action in self.actions],
        }


def _market_for(path: Path, root: Path) -> tuple[str, str, str]:
    return "PK", "PK", "en"


def _url_for(path: Path, root: Path, site_url: str) -> str:
    relative = path.relative_to(root).as_posix()
    if relative.endswith("/index.html"):
        relative = relative[:-10]
    elif relative == "index.html":
        relative = ""
    return site_url.rstrip("/") + "/" + relative.lstrip("/")


def _schema_types(schemas: list[dict]) -> list[str]:
    types: list[str] = []
    for schema in schemas:
        entries = schema.get("@graph", []) if isinstance(schema, dict) else []
        if not entries and isinstance(schema, dict):
            entries = [schema]
        for entry in entries:
            value = entry.get("@type") if isinstance(entry, dict) else None
            if isinstance(value, list):
                types.extend(str(item) for item in value)
            elif value:
                types.append(str(value))
    return sorted(set(types))




def _issue(code: str, severity: str, url: str, message: str) -> dict:
    return {"code": code, "severity": severity, "url": url, "message": message}


def _sitemap_locations(path: Path) -> list[str]:
    try:
        root = ElementTree.fromstring(path.read_text(encoding="utf-8"))
    except (OSError, ElementTree.ParseError):
        return []
    return [node.text.strip() for node in root.findall("{*}url/{*}loc") if node.text and node.text.strip()]


def audit_repository(root: Path, site_url: str) -> OfflineAudit:
    result = OfflineAudit()
    html_files = sorted(path for path in root.rglob("*.html") if ".git" not in path.parts and not any(part.startswith(".") for part in path.relative_to(root).parts))
    known_urls: set[str] = set()
    for path in html_files:
        url = _url_for(path, root, site_url)
        known_urls.add(url.rstrip("/") or site_url)
        market, country, language = _market_for(path, root)
        signals = _HTMLSignals()
        try:
            signals.feed(path.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            result.issues.append(_issue("READ_ERROR", "P0", url, str(exc)))
            continue
        page = {
            "path": path.relative_to(root).as_posix(),
            "url": url,
            "market": market,
            "country": country,
            "language": language,
            "title": signals.title.strip(),
            "description": signals.description.strip(),
            "canonical": signals.canonical,
            "h1_count": signals.h1_count,
            "hreflang": signals.hreflang,
            "schema_types": _schema_types(signals.schemas),
            "image_count": len(signals.images),
            "missing_alt_count": sum(1 for image in signals.images if not image["alt"]),
            "internal_link_count": 0,
            "noindex": signals.noindex,
        }
        for href in signals.links:
            target = urljoin(url.rstrip("/") + "/", href)
            if urlparse(target).netloc == urlparse(site_url).netloc:
                page["internal_link_count"] += 1
        result.pages.append(page)
        indexable = not signals.noindex and not path.name.startswith("google")
        if indexable and not signals.title.strip():
            result.issues.append(_issue("MISSING_TITLE", "P1", url, "Page has no title."))
        if indexable and not signals.description.strip():
            result.issues.append(_issue("MISSING_DESCRIPTION", "P1", url, "Page has no meta description."))
        if indexable and not signals.canonical:
            result.issues.append(_issue("MISSING_CANONICAL", "P1", url, "Page has no canonical link."))
        if indexable and signals.h1_count != 1:
            result.issues.append(_issue("H1_COUNT", "P1", url, f"Expected one H1, found {signals.h1_count}."))
        if indexable and any(schema.get("_invalid_jsonld") for schema in signals.schemas):
            result.issues.append(_issue("INVALID_JSONLD", "P1", url, "A JSON-LD block is invalid."))
        if indexable and page["missing_alt_count"]:
            result.issues.append(_issue("MISSING_ALT", "P2", url, f"{page['missing_alt_count']} image(s) lack alt text."))

    for sitemap_name in ("sitemap.xml",):
        sitemap_path = root / sitemap_name
        locations = _sitemap_locations(sitemap_path) if sitemap_path.exists() else []
        missing = sorted(set(loc.rstrip("/") for loc in locations) - {url.rstrip("/") for url in known_urls})
        result.sitemaps[sitemap_name] = {"exists": sitemap_path.exists(), "url_count": len(locations), "missing_local_pages": missing}
        if not sitemap_path.exists():
            result.issues.append(_issue("MISSING_SITEMAP", "P0", site_url, f"{sitemap_name} is missing."))
        elif not locations:
            result.issues.append(_issue("EMPTY_SITEMAP", "P1", site_url, f"{sitemap_name} has no URL entries."))

    robots_path = root / "robots.txt"
    robots_text = robots_path.read_text(encoding="utf-8", errors="replace") if robots_path.exists() else ""
    result.robots = {"exists": robots_path.exists(), "sitemaps": [line.split(":", 1)[1].strip() for line in robots_text.splitlines() if line.lower().startswith("sitemap:")], "has_disallow_all": bool(re.search(r"(?im)^\s*disallow:\s*/\s*$", robots_text))}
    if not robots_path.exists():
        result.issues.append(_issue("MISSING_ROBOTS", "P0", site_url, "robots.txt is missing."))
    if result.robots["has_disallow_all"]:
        result.issues.append(_issue("ROBOTS_BLOCK_ALL", "P0", site_url, "robots.txt disallows the whole site."))

    result.summary = {
        "pages": len(result.pages),
        "pk_pages": sum(page["market"] == "PK" for page in result.pages),
        "issues": len(result.issues),
        "p0": sum(issue["severity"] == "P0" for issue in result.issues),
        "p1": sum(issue["severity"] == "P1" for issue in result.issues),
        "p2": sum(issue["severity"] == "P2" for issue in result.issues),
    }
    for issue in result.issues:
        decision = ActionDecision.HUMAN_REVIEW if issue["severity"] == "P0" else ActionDecision.AUTO_SAFE if issue["code"] in {"MISSING_ALT"} else ActionDecision.PR_REQUIRED
        result.actions.append(SEOAction(issue["code"], decision, issue["message"], {"url": issue["url"], "severity": issue["severity"]}))
    return result


def fetch_production(url: str, timeout: int = 20) -> dict:
    request = Request(url, headers={"User-Agent": "AI-Tool-Gems-Hermes/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            return {"status": "VERIFIED", "url": url, "http_status": response.status, "bytes": len(body), "content_type": response.headers.get("content-type", "")}
    except Exception as exc:
        return {"status": "ERROR", "url": url, "error": str(exc)}
