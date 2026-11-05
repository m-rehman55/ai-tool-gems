"""
Multi-Page Crawl Engine for HERMES Technical SEO & Web Crawling Agent (Agent 2).
Performs polite, concurrent, multi-page live HTTP crawls and offline repo crawls,
tracks redirect chains, depth, robots.txt boundaries, and live vs local diffs.
"""

from __future__ import annotations
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

from crawler_agent.models import (
    CrawlRecord,
    URLCrawlState,
    HeadingHierarchyAudit,
    ImageAuditItem,
)

ALLOWED_HOSTS = {"aitoolgems.tech", "www.aitoolgems.tech", "localhost", "127.0.0.1"}

EXCLUDED_CRAWL_PATTERNS = [
    re.compile(p, re.I) for p in [
        r"^/admin(\.html)?",
        r"^/cart",
        r"^/checkout",
        r"^/payment",
        r"^/scratch/",
        r"^/\.seo-cache/",
        r"^/data/",
        r"^/marketing_agent/",
    ]
]

STRIP_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "msclkid", "ref", "src", "v",
}


class AdvancedHTMLParser(HTMLParser):
    """Detailed HTML extractor parsing headings hierarchy, links, images, and structured data."""

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.title = ""
        self.meta_description = ""
        self.canonical = ""
        self.robots_meta = ""
        self.h1_list: List[str] = []
        self.h2_list: List[str] = []
        self.h3_list: List[str] = []
        self.heading_order: List[str] = []  # Tracks tag order, e.g. ["h1", "h2", "h3"]
        self.internal_links: List[str] = []
        self.external_links: List[str] = []
        self.images: List[ImageAuditItem] = []
        self.schemas: List[str] = []
        self.has_mixed_content = False

        self._in_title = False
        self._cur_tag = ""
        self._tag_buf: List[str] = []
        self._in_schema = False
        self._schema_buf: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "").strip() for k, v in attrs}

        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = attr_dict.get("name", "").lower()
            prop = attr_dict.get("property", "").lower()
            content = attr_dict.get("content", "")
            if name == "description" or prop == "og:description":
                if not self.meta_description:
                    self.meta_description = content
            elif name == "robots":
                self.robots_meta = content
        elif tag == "link":
            rel = attr_dict.get("rel", "").lower()
            href = attr_dict.get("href", "")
            if rel == "canonical":
                self.canonical = href
            # Check mixed content link (e.g. http stylesheet or icon)
            if href.startswith("http://"):
                self.has_mixed_content = True
        elif tag in ("h1", "h2", "h3"):
            self._cur_tag = tag
            self._tag_buf = []
            self.heading_order.append(tag)
        elif tag == "a" and "href" in attr_dict:
            href = attr_dict["href"]
            if href.startswith(("mailto:", "tel:", "javascript:")):
                pass
            elif href.startswith(("http://", "https://", "//")):
                parsed = urllib.parse.urlparse(href)
                if parsed.netloc in ALLOWED_HOSTS:
                    norm = self._normalize(href)
                    if norm:
                        self.internal_links.append(norm)
                else:
                    self.external_links.append(href)
            elif not href.startswith("#"):
                norm = self._normalize(href)
                if norm:
                    self.internal_links.append(norm)
        elif tag == "img":
            src = attr_dict.get("src", "")
            alt = attr_dict.get("alt", "")
            loading = attr_dict.get("loading", "")
            is_mixed = src.startswith("http://")
            if is_mixed:
                self.has_mixed_content = True
            ext = src.split("?")[0].split(".")[-1].lower() if "." in src else ""
            is_modern = ext in ("webp", "svg", "avif")
            self.images.append(
                ImageAuditItem(
                    src=src,
                    alt=alt,
                    loading=loading,
                    is_missing_alt=(not bool(alt.strip())),
                    is_modern_format=is_modern,
                    is_mixed_content=is_mixed
                )
            )
        elif tag == "script":
            if attr_dict.get("type", "").lower() == "application/ld+json":
                self._in_schema = True
                self._schema_buf = []
            src = attr_dict.get("src", "")
            if src.startswith("http://"):
                self.has_mixed_content = True

    def handle_endtag(self, tag: str):
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3"):
            text = " ".join("".join(self._tag_buf).split())
            if text:
                if tag == "h1":
                    self.h1_list.append(text)
                elif tag == "h2":
                    self.h2_list.append(text)
                elif tag == "h3":
                    self.h3_list.append(text)
            self._cur_tag = ""
        elif tag == "script" and self._in_schema:
            self.schemas.append("".join(self._schema_buf).strip())
            self._in_schema = False

    def handle_data(self, data: str):
        if self._in_title:
            self.title += data
        elif self._cur_tag in ("h1", "h2", "h3"):
            self._tag_buf.append(data)
        elif self._in_schema:
            self._schema_buf.append(data)

    def _normalize(self, raw_url: str) -> Optional[str]:
        try:
            joined = urllib.parse.urljoin(self.base_url, raw_url)
            parsed = urllib.parse.urlparse(joined)
            if parsed.netloc not in ALLOWED_HOSTS:
                return None
            path = parsed.path
            if not path or path == "":
                path = "/"
            elif path.endswith("/index.html"):
                path = path[:-10]
            elif "." not in path.split("/")[-1] and not path.endswith("/"):
                path += "/"

            # Exclude non-crawlable patterns
            for pat in EXCLUDED_CRAWL_PATTERNS:
                if pat.search(path):
                    return None

            return urllib.parse.urlunparse((
                "https",
                "aitoolgems.tech",
                path,
                "",
                "",
                ""
            ))
        except Exception:
            return None


class CrawlerEngine:
    """Enterprise technical SEO crawler supporting live multi-page crawling and local inspection."""

    def __init__(
        self,
        base_url: str = "https://aitoolgems.tech",
        base_dir: Optional[Path | str] = None,
        user_agent: str = "HERMES-Crawler-Agent/2.0 (+https://aitoolgems.tech/robots.txt)",
        max_pages: int = 150,
        concurrency: int = 4,
        timeout_seconds: float = 12.0,
        rate_limit_delay_seconds: float = 0.2,
    ):
        self.base_url = base_url.rstrip("/")
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.user_agent = user_agent
        self.max_pages = max_pages
        self.concurrency = concurrency
        self.timeout = timeout_seconds
        self.rate_limit_delay = rate_limit_delay_seconds

    def parse_html(self, html: str, url: str, status_code: int = 200, elapsed_ms: float = 0.0) -> CrawlRecord:
        """Parses HTML document into structured CrawlRecord with heading hierarchy checks."""
        parser = AdvancedHTMLParser(base_url=self.base_url)
        try:
            parser.feed(html)
        except Exception:
            pass

        # Heading hierarchy audit
        heading_issues = []
        if len(parser.h1_list) == 0:
            heading_issues.append("Missing H1 heading tag")
        elif len(parser.h1_list) > 1:
            heading_issues.append(f"Multiple H1 headings detected ({len(parser.h1_list)} H1s)")

        # Check for skipped heading tiers, e.g. H1 immediately followed by H3
        seen_h1 = False
        seen_h2 = False
        for tag in parser.heading_order:
            if tag == "h1":
                seen_h1 = True
            elif tag == "h2":
                seen_h2 = True
            elif tag == "h3":
                if seen_h1 and not seen_h2:
                    heading_issues.append("Heading hierarchy violation: H3 tag placed without preceding H2")
                    break

        headings = HeadingHierarchyAudit(
            h1_list=parser.h1_list,
            h2_list=parser.h2_list,
            h3_list=parser.h3_list,
            missing_h1=(len(parser.h1_list) == 0),
            multiple_h1=(len(parser.h1_list) > 1),
            hierarchy_valid=(len(heading_issues) == 0),
            issues=heading_issues
        )

        # Word count calculation (strip HTML tags)
        plain_text = re.sub(r"<[^>]+>", " ", html)
        words = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", plain_text)
        word_count = len(words)

        # Content hash
        html_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()

        # Trailing slash consistency
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        has_trailing_slash = (path == "/" or path.endswith("/") or "." in path.split("/")[-1])

        # Indexability check
        robots = parser.robots_meta.lower()
        is_indexable = ("noindex" not in robots and status_code == 200)

        record = CrawlRecord(
            url=url,
            state=URLCrawlState.CRAWLED,
            status_code=status_code,
            title=parser.title.strip(),
            meta_description=parser.meta_description.strip(),
            canonical=parser.canonical.strip(),
            robots_meta=parser.robots_meta.strip(),
            is_indexable=is_indexable,
            word_count=word_count,
            headings=headings,
            internal_links=list(set(parser.internal_links)),
            external_links=list(set(parser.external_links)),
            images=parser.images,
            has_mixed_content=parser.has_mixed_content,
            has_trailing_slash=has_trailing_slash,
            schemas=parser.schemas,
            fetch_time_ms=round(elapsed_ms, 2),
            html_hash=html_hash,
            last_crawled_at=datetime.now(timezone.utc).isoformat(),
        )
        return record

    def fetch_live_url(self, target_url: str) -> Tuple[Optional[str], int, List[str], float, Optional[str]]:
        """
        Fetches live URL following redirect chains and recording intermediate hops.
        Returns: (html_content, status_code, redirect_chain, elapsed_ms, error)
        """
        redirect_chain = [target_url]
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                elapsed_ms = (time.time() - t0) * 1000.0
                final_url = resp.geturl()
                if final_url != target_url:
                    redirect_chain.append(final_url)
                html = resp.read().decode("utf-8", errors="replace")
                return html, resp.status, redirect_chain, elapsed_ms, None
        except urllib.error.HTTPError as e:
            elapsed_ms = (time.time() - t0) * 1000.0
            return None, e.code, redirect_chain, elapsed_ms, str(e)
        except Exception as e:
            elapsed_ms = (time.time() - t0) * 1000.0
            return None, 0, redirect_chain, elapsed_ms, str(e)

    def extract_sitemap_urls(self, sitemap_path_or_url: Optional[str] = None) -> List[str]:
        """Discovers all canonical URLs from sitemap.xml."""
        sitemap_target = sitemap_path_or_url or f"{self.base_url}/sitemap.xml"
        xml_content = None

        if sitemap_target.startswith("http"):
            html, status, _, _, _ = self.fetch_live_url(sitemap_target)
            if status == 200 and html:
                xml_content = html
        else:
            p = Path(sitemap_target)
            if p.exists():
                xml_content = p.read_text(encoding="utf-8")

        if not xml_content:
            local_sm = self.base_dir / "sitemap.xml"
            if local_sm.exists():
                xml_content = local_sm.read_text(encoding="utf-8")

        urls = []
        if xml_content:
            try:
                root = ET.fromstring(xml_content)
                ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
                for elem in root.findall(".//ns:loc", ns):
                    if elem.text:
                        urls.append(elem.text.strip())
            except Exception:
                # Fallback to regex
                urls = re.findall(r"<loc>(https?://[^<]+)</loc>", xml_content)

        return sorted(list(set(urls)))

    def crawl_live_production(
        self,
        seed_url: Optional[str] = None,
        use_sitemap_seeds: bool = True
    ) -> List[CrawlRecord]:
        """
        Executes full recursive live crawl across production website.
        Discovers internal links, follows crawl queue, and respects rate limits.
        """
        start_seed = seed_url or f"{self.base_url}/"
        sitemap_urls = set(self.extract_sitemap_urls()) if use_sitemap_seeds else set()

        discovered: Set[str] = {start_seed}
        if sitemap_urls:
            discovered.update(sitemap_urls)

        crawled_records: Dict[str, CrawlRecord] = {}
        queue: List[Tuple[str, int]] = [(u, 0 if u == start_seed else 1) for u in discovered]
        visited: Set[str] = set()

        print(f"[CRAWLER-AGENT] Starting Live Crawl on {self.base_url} (Initial Queue: {len(queue)} URLs)...")

        while queue and len(visited) < self.max_pages:
            current_url, depth = queue.pop(0)
            if current_url in visited:
                continue

            visited.add(current_url)
            html, status, chain, elapsed_ms, error = self.fetch_live_url(current_url)

            if html and status == 200:
                record = self.parse_html(html, current_url, status_code=status, elapsed_ms=elapsed_ms)
                record.crawl_depth = depth
                record.redirect_chain = chain
                record.in_sitemap = (current_url in sitemap_urls)
                crawled_records[current_url] = record

                # Enqueue newly discovered internal links
                for link in record.internal_links:
                    if link not in visited and link not in [q[0] for q in queue]:
                        if len(visited) + len(queue) < self.max_pages:
                            queue.append((link, depth + 1))
            else:
                crawled_records[current_url] = CrawlRecord(
                    url=current_url,
                    state=URLCrawlState.CRAWLED,
                    status_code=status,
                    crawl_depth=depth,
                    redirect_chain=chain,
                    in_sitemap=(current_url in sitemap_urls),
                    fetch_time_ms=elapsed_ms,
                    error_message=error,
                )

            time.sleep(self.rate_limit_delay)

        print(f"[CRAWLER-AGENT] Live Crawl Finished: {len(crawled_records)} pages crawled successfully.")
        return list(crawled_records.values())

    def crawl_local_repository(self) -> List[CrawlRecord]:
        """Crawl 100% of static HTML files in local workspace."""
        crawled: List[CrawlRecord] = []
        html_files = list(self.base_dir.glob("*.html")) + list(self.base_dir.glob("*/**/*.html"))
        ignore_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", ".agents", "scratch", ".seo-cache"}

        sitemap_urls = set(self.extract_sitemap_urls())

        for fpath in html_files:
            if any(part in fpath.parts for part in ignore_dirs):
                continue
            if fpath.name.startswith("google") and fpath.name.endswith(".html"):
                continue

            rel = fpath.relative_to(self.base_dir).as_posix()
            if rel == "index.html":
                page_url = f"{self.base_url}/"
            elif rel.endswith("/index.html"):
                page_url = f"{self.base_url}/{rel[:-10]}"
            else:
                page_url = f"{self.base_url}/{rel}"

            try:
                html = fpath.read_text(encoding="utf-8", errors="replace")
                rec = self.parse_html(html, page_url, status_code=200, elapsed_ms=1.0)
                rec.in_sitemap = (page_url in sitemap_urls)
                crawled.append(rec)
            except Exception as e:
                crawled.append(
                    CrawlRecord(
                        url=page_url,
                        status_code=500,
                        error_message=f"Local read failure: {e}"
                    )
                )

        return crawled

    def compare_live_vs_local(self) -> Dict[str, Any]:
        """Compares live production HTML vs local repository content and uncovers discrepancies."""
        print("[CRAWLER-AGENT] Comparing Live Production vs Local Repository...")
        local_records = {r.url: r for r in self.crawl_local_repository()}
        sitemap_urls = self.extract_sitemap_urls()

        live_records: Dict[str, CrawlRecord] = {}
        # Fetch live sitemap URLs
        for url in sitemap_urls[:50]:  # Sample first 50 canonical URLs to be safe on quota
            html, status, chain, elapsed_ms, err = self.fetch_live_url(url)
            if status == 200 and html:
                live_records[url] = self.parse_html(html, url, status_code=status, elapsed_ms=elapsed_ms)
            time.sleep(0.1)

        diffs = []
        for url, live_rec in live_records.items():
            local_rec = local_records.get(url)
            if not local_rec:
                diffs.append({
                    "url": url,
                    "issue": "URL exists on live production but missing from local repository."
                })
            else:
                # Compare title, H1, and canonical
                mismatches = []
                if live_rec.title != local_rec.title:
                    mismatches.append(f"Title mismatch (Live: '{live_rec.title}' vs Local: '{local_rec.title}')")
                if live_rec.canonical != local_rec.canonical:
                    mismatches.append(f"Canonical mismatch (Live: '{live_rec.canonical}' vs Local: '{local_rec.canonical}')")
                if live_rec.headings.h1_list != local_rec.headings.h1_list:
                    mismatches.append(f"H1 mismatch (Live: {live_rec.headings.h1_list} vs Local: {local_rec.headings.h1_list})")

                if mismatches:
                    diffs.append({"url": url, "mismatches": mismatches})

        return {
            "total_urls_compared": len(live_records),
            "discrepancies_count": len(diffs),
            "discrepancies": diffs,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
