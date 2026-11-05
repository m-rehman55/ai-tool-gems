"""
Data Models and State Machine for HERMES Technical SEO Crawler (Agent 2).
Tracks each URL along the state machine:
DISCOVERED -> CRAWLED -> ANALYZED -> FIX_REQUIRED -> APPROVED -> DEPLOYED -> VERIFIED.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional, Set


class URLCrawlState(str, Enum):
    DISCOVERED = "DISCOVERED"
    CRAWLED = "CRAWLED"
    ANALYZED = "ANALYZED"
    FIX_REQUIRED = "FIX_REQUIRED"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    VERIFIED = "VERIFIED"


@dataclass
class ImageAuditItem:
    src: str
    alt: str
    loading: str = ""
    is_missing_alt: bool = False
    is_modern_format: bool = True  # webp, svg, avif
    is_mixed_content: bool = False


@dataclass
class HeadingHierarchyAudit:
    h1_list: List[str] = field(default_factory=list)
    h2_list: List[str] = field(default_factory=list)
    h3_list: List[str] = field(default_factory=list)
    missing_h1: bool = False
    multiple_h1: bool = False
    hierarchy_valid: bool = True
    issues: List[str] = field(default_factory=list)


@dataclass
class CrawlRecord:
    url: str
    state: URLCrawlState = URLCrawlState.DISCOVERED
    status_code: int = 0
    redirect_chain: List[str] = field(default_factory=list)
    crawl_depth: int = 0
    title: str = ""
    meta_description: str = ""
    canonical: str = ""
    robots_meta: str = ""
    is_indexable: bool = True
    word_count: int = 0
    headings: HeadingHierarchyAudit = field(default_factory=HeadingHierarchyAudit)
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    images: List[ImageAuditItem] = field(default_factory=list)
    has_mixed_content: bool = False
    has_trailing_slash: bool = True
    schemas: List[str] = field(default_factory=list)
    in_sitemap: bool = False
    fetch_time_ms: float = 0.0
    html_hash: str = ""
    error_message: Optional[str] = None
    issues_detected: List[str] = field(default_factory=list)
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_crawled_at: Optional[str] = None
    last_analyzed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CrawlRecord:
        d = dict(data)
        d["state"] = URLCrawlState(d.get("state", "DISCOVERED"))
        if "headings" in d and isinstance(d["headings"], dict):
            d["headings"] = HeadingHierarchyAudit(**d["headings"])
        if "images" in d and isinstance(d["images"], list):
            d["images"] = [ImageAuditItem(**img) if isinstance(img, dict) else img for img in d["images"]]
        return cls(**d)

    def transition_to(self, new_state: URLCrawlState) -> None:
        self.state = new_state


@dataclass
class TechnicalAuditSummary:
    total_urls_scanned: int = 0
    crawl_mode: str = "LIVE_PRODUCTION"  # or LOCAL_REPO
    broken_links_count: int = 0
    orphan_pages_count: int = 0
    duplicate_titles_count: int = 0
    duplicate_metas_count: int = 0
    missing_h1_count: int = 0
    heading_hierarchy_violations: int = 0
    images_missing_alt_count: int = 0
    mixed_content_violations: int = 0
    trailing_slash_inconsistencies: int = 0
    thin_content_pages_count: int = 0
    canonical_issues_count: int = 0
    sitemap_mismatches_count: int = 0
    crawl_budget_waste_count: int = 0
    average_fetch_time_ms: float = 0.0
    technical_health_score: float = 100.0  # 0 to 100
    critical_issues: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
