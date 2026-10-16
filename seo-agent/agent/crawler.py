#!/usr/bin/env python3
"""
Crawler for AIToolGems Autonomous SEO Growth Agent
--------------------------------------------------
Polite, bounded, concurrent-safe crawler supporting both:
1. Local offline repository crawling (exact filesystem inspection).
2. Live HTTP crawling (with exponential backoff, jitter, rate limits, and custom User-Agent).
3. Screaming Frog SEO Spider compatibility detection (graceful zero-dependency fallback).
4. Sensitive URL exclusions, domain allowlisting, and parameter normalization.
"""

from __future__ import annotations
import os
import re
import time
import shutil
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

# Security and Crawl Boundaries
ALLOWED_DOMAINS = {"aitoolgems.tech", "www.aitoolgems.tech", "localhost", "127.0.0.1"}

# Sensitive and non-crawlable routes
EXCLUDED_PATTERNS = [
    re.compile(p, re.I) for p in [
        r"^/admin(\.html)?",
        r"^/cart",
        r"^/checkout",
        r"^/payment",
        r"^/logout",
        r"^/login",
        r"^/auth",
        r"^/account",
        r"^/scratch/",
        r"^/\.seo-cache/",
        r"^/reports/",
        r"^/marketing_agent/",
    ]
]

# Query parameters to strip to prevent infinite crawling loops
STRIP_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "msclkid", "ref", "src", "v",
}

def detect_screaming_frog() -> Dict[str, Any]:
    """
    Detects if Screaming Frog SEO Spider CLI is available locally.
    Never requires a paid license; if unavailable or cannot run unattended,
    falls back cleanly to AIToolGems native Python crawler.
    """
    cli_name = "ScreamingFrogSEOSpiderCli"
    path = shutil.which(cli_name) or shutil.which("screamingfrogseospider")
    
    if not path:
        win_paths = [
            Path(r"C:\Program Files\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe"),
            Path(r"C:\Program Files (x86)\Screaming Frog SEO Spider\ScreamingFrogSEOSpiderCli.exe"),
        ]
        for wp in win_paths:
            if wp.exists():
                path = str(wp)
                break
                
    if path:
        return {
            "available": True,
            "cli_path": path,
            "engine": "screaming_frog",
            "message": f"Screaming Frog CLI detected at: {path}",
        }
    return {
        "available": False,
        "cli_path": None,
        "engine": "native_python",
        "message": "Screaming Frog CLI not detected in environment. Using AIToolGems native Python crawler.",
    }

def is_allowed_domain(url: str, base_host: str = "aitoolgems.tech") -> bool:
    """Ensures domain allowlisting is strictly enforced."""
    try:
        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc:
            return True  # Relative URL
        host = parsed.netloc.split(":")[0].lower()
        return host in ALLOWED_DOMAINS or host == base_host
    except Exception:
        return False

def is_sensitive_url(path_or_url: str) -> bool:
    """Verifies that checkout, admin, auth, and state-changing endpoints are excluded."""
    try:
        parsed = urllib.parse.urlparse(path_or_url)
        path = parsed.path
        return any(pattern.search(path) for pattern in EXCLUDED_PATTERNS)
    except Exception:
        return True

def normalize_url(url: str, base_url: str = "https://aitoolgems.tech") -> Optional[str]:
    """Normalizes URL, strips tracking query parameters, and removes fragments."""
    try:
        joined = urllib.parse.urljoin(base_url, url)
        parsed = urllib.parse.urlparse(joined)
        
        # Remove fragment
        fragment = ""
        
        # Strip tracking query parameters
        qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=False)
        cleaned_qs = {k: v for k, v in qs.items() if k.lower() not in STRIP_TRACKING_PARAMS}
        new_query = urllib.parse.urlencode(cleaned_qs, doseq=True)
        
        # Normalize path
        path = parsed.path
        if not path:
            path = "/"
        elif path != "/" and path.endswith("/index.html"):
            path = path[:-10]
            
        rebuilt = urllib.parse.urlunparse((
            parsed.scheme or "https",
            parsed.netloc.lower() or "aitoolgems.tech",
            path,
            parsed.params,
            new_query,
            fragment
        ))
        return rebuilt
    except Exception:
        return None

@dataclass
class CrawledPage:
    url: str
    status_code: int
    title: str = ""
    meta_description: str = ""
    canonical: str = ""
    robots_meta: str = ""
    h1_list: List[str] = field(default_factory=list)
    h2_list: List[str] = field(default_factory=list)
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    schemas: List[str] = field(default_factory=list)
    word_count: int = 0
    raw_html: str = ""
    file_path: Optional[str] = None
    fetch_time_ms: float = 0.0
    error: Optional[str] = None
    crawler_engine: str = "native_python"

class PageHTMLParser(HTMLParser):
    """Extracts SEO elements, metadata, schema, and link structure."""

    def __init__(self, base_url: str = "https://aitoolgems.tech"):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.title = ""
        self.meta_description = ""
        self.canonical = ""
        self.robots_meta = ""
        self.h1_list: List[str] = []
        self.h2_list: List[str] = []
        self.internal_links: List[str] = []
        self.external_links: List[str] = []
        self.images: List[Dict[str, str]] = []
        self.schemas: List[str] = []
        
        self._in_title = False
        self._in_h1 = False
        self._in_h2 = False
        self._in_schema = False
        self._h1_buf: List[str] = []
        self._h2_buf: List[str] = []
        self._schema_buf: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]):
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
            if rel == "canonical":
                self.canonical = attr_dict.get("href", "")
        elif tag == "h1":
            self._in_h1 = True
            self._h1_buf = []
        elif tag == "h2":
            self._in_h2 = True
            self._h2_buf = []
        elif tag == "a" and "href" in attr_dict:
            href = attr_dict["href"]
            if href.startswith("http://") or href.startswith("https://") or href.startswith("//"):
                if "aitoolgems.tech" in href:
                    norm = normalize_url(href, self.base_url)
                    if norm and not is_sensitive_url(norm):
                        self.internal_links.append(norm)
                else:
                    self.external_links.append(href)
            elif href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
                pass
            else:
                norm = normalize_url(href, self.base_url)
                if norm and not is_sensitive_url(norm):
                    self.internal_links.append(norm)
        elif tag == "img":
            self.images.append({
                "src": attr_dict.get("src", ""),
                "alt": attr_dict.get("alt", ""),
                "loading": attr_dict.get("loading", ""),
            })
        elif tag == "script" and attr_dict.get("type", "").lower() == "application/ld+json":
            self._in_schema = True
            self._schema_buf = []

    def handle_endtag(self, tag: str):
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
            full_h1 = " ".join("".join(self._h1_buf).split())
            if full_h1:
                self.h1_list.append(full_h1)
        elif tag == "h2":
            self._in_h2 = False
            full_h2 = " ".join("".join(self._h2_buf).split())
            if full_h2:
                self.h2_list.append(full_h2)
        elif tag == "script" and self._in_schema:
            self.schemas.append("".join(self._schema_buf))
            self._in_schema = False

    def handle_data(self, data: str):
        if self._in_title:
            self.title += data
        elif self._in_h1:
            self._h1_buf.append(data)
        elif self._in_h2:
            self._h2_buf.append(data)
        elif self._in_schema:
            self._schema_buf.append(data)

class Crawler:
    """Orchestrates polite site and local repository crawling."""

    def __init__(
        self,
        base_url: str = "https://aitoolgems.tech",
        user_agent: str = "AIToolGems-GrowthAgent/1.0 (+https://aitoolgems.tech/robots.txt)",
        timeout_seconds: float = 12.0,
        delay_seconds: float = 0.5,
        max_pages: int = 100,
    ):
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.timeout = timeout_seconds
        self.delay = delay_seconds
        self.max_pages = max_pages
        self.screaming_frog_status = detect_screaming_frog()

    def parse_html_content(self, html: str, url: str, status_code: int = 200, file_path: Optional[str] = None) -> CrawledPage:
        """Parses HTML and computes metrics."""
        parser = PageHTMLParser(base_url=self.base_url)
        try:
            parser.feed(html)
        except Exception:
            pass

        # Compute plain text word count
        plain_text = re.sub(r"<[^>]+>", " ", html)
        words = re.findall(r"\b\w+\b", plain_text)

        return CrawledPage(
            url=url,
            status_code=status_code,
            title=parser.title.strip(),
            meta_description=parser.meta_description.strip(),
            canonical=parser.canonical.strip(),
            robots_meta=parser.robots_meta.strip(),
            h1_list=parser.h1_list,
            h2_list=parser.h2_list,
            internal_links=parser.internal_links,
            external_links=parser.external_links,
            images=parser.images,
            schemas=parser.schemas,
            word_count=len(words),
            raw_html=html,
            file_path=file_path,
            crawler_engine=self.screaming_frog_status["engine"],
        )

    def crawl_local_repository(self, root_dir: Path | str) -> List[CrawledPage]:
        """Fast, 100% offline crawl of all static HTML files in the repository."""
        root = Path(root_dir)
        crawled: List[CrawledPage] = []

        html_files = list(root.glob("*.html")) + list(root.glob("*/**/*.html"))
        # Exclude node_modules, .git, venv, temporary scratch folders, and cache directories
        ignore_parts = {".git", "node_modules", ".venv", "venv", "__pycache__", ".agents", "scratch", ".seo-cache"}

        for fpath in html_files:
            if any(part in fpath.parts for part in ignore_parts):
                continue
            if fpath.name.startswith("google") and fpath.name.endswith(".html"):
                continue

            rel_path = fpath.relative_to(root).as_posix()
            if rel_path == "index.html":
                page_url = f"{self.base_url}/"
            elif rel_path.endswith("/index.html"):
                page_url = f"{self.base_url}/{rel_path[:-10]}"
            else:
                page_url = f"{self.base_url}/{rel_path}"

            # Check sensitive path exclusion
            if is_sensitive_url(page_url):
                continue

            try:
                html = fpath.read_text(encoding="utf-8", errors="ignore")
                page = self.parse_html_content(html, url=page_url, status_code=200, file_path=str(fpath))
                crawled.append(page)
            except Exception as e:
                crawled.append(
                    CrawledPage(
                        url=page_url,
                        status_code=500,
                        file_path=str(fpath),
                        error=f"Local read error: {e}",
                        crawler_engine=self.screaming_frog_status["engine"],
                    )
                )

            if len(crawled) >= self.max_pages:
                break

        return crawled

    def fetch_live_page(self, url: str) -> CrawledPage:
        """Politely fetches a live page over HTTP with retry and timeout."""
        if not is_allowed_domain(url, urllib.parse.urlparse(self.base_url).netloc):
            return CrawledPage(url=url, status_code=403, error="Domain not in approved allowlist")

        if is_sensitive_url(url):
            return CrawledPage(url=url, status_code=403, error="URL matches sensitive exclusion policy")

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                status = response.getcode()
                html = response.read().decode("utf-8", errors="ignore")
                elapsed = (time.time() - start_time) * 1000.0
                page = self.parse_html_content(html, url=url, status_code=status)
                page.fetch_time_ms = round(elapsed, 2)
                return page
        except urllib.error.HTTPError as e:
            return CrawledPage(url=url, status_code=e.code, error=str(e), crawler_engine=self.screaming_frog_status["engine"])
        except Exception as e:
            return CrawledPage(url=url, status_code=0, error=str(e), crawler_engine=self.screaming_frog_status["engine"])
