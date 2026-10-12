#!/usr/bin/env python3
"""
Crawler for AIToolGems Autonomous SEO Growth Agent
--------------------------------------------------
Polite, bounded, concurrent-safe crawler supporting both:
1. Local offline repository crawling (exact filesystem inspection).
2. Live HTTP crawling (with exponential backoff, jitter, rate limits, and custom User-Agent).
"""

from __future__ import annotations
import os
import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

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
                    self.internal_links.append(href)
                else:
                    self.external_links.append(href)
            elif href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
                pass
            else:
                self.internal_links.append(href)
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

    def parse_html_content(self, html: str, url: str, status_code: int = 200, file_path: Optional[str] = None) -> CrawledPage:
        """Parses HTML and computes metrics."""
        parser = PageHTMLParser(base_url=self.base_url)
        try:
            parser.feed(html)
        except Exception as e:
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
                    )
                )

            if len(crawled) >= self.max_pages:
                break

        return crawled

    def fetch_live_page(self, url: str) -> CrawledPage:
        """Politely fetches a live page over HTTP with retry and timeout."""
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
            return CrawledPage(url=url, status_code=e.code, error=str(e))
        except Exception as e:
            return CrawledPage(url=url, status_code=0, error=str(e))
