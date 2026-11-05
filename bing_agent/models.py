"""
models.py - Data Models for Bing Webmaster Tools & IndexNow Intelligence.

Represents official Bing Webmaster Tools API objects:
- BingSite: Verified site registration
- BingQueryStat: Search performance query rows (impressions, clicks, CTR, position)
- BingPageStat: Page-level performance
- BingCrawlStat: Daily crawl metrics, status codes, and in-index count
- BingCrawlError: Detailed crawl errors (HTTP 4xx, 5xx, timeouts, blocked)
- BingQuota: IndexNow & URL submission limits
- IndexNowQueueItem: Durable submission queue entry
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def parse_bing_date(date_str: str) -> str:
    """Converts Bing's '/Date(1790294400000)/' epoch millisecond strings to ISO-8601 YYYY-MM-DD."""
    if not date_str:
        return ""
    s = str(date_str).strip()
    if s.startswith("/Date(") and s.endswith(")/"):
        m = re.search(r"-?\d+", s)
        if m:
            try:
                ms = int(m.group(0))
                return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
            except Exception:
                pass
    return s


@dataclass
class BingSite:
    url: str
    is_verified: bool
    auth_code: str = ""
    dns_verification_code: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BingQueryStat:
    query: str
    date: str
    clicks: int
    impressions: int
    avg_click_position: float
    avg_impression_position: float

    @property
    def ctr(self) -> float:
        return round((self.clicks / self.impressions * 100.0), 2) if self.impressions > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["ctr"] = self.ctr
        return d


@dataclass
class BingPageStat:
    page: str
    date: str
    clicks: int
    impressions: int
    avg_click_position: float
    avg_impression_position: float

    @property
    def ctr(self) -> float:
        return round((self.clicks / self.impressions * 100.0), 2) if self.impressions > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["ctr"] = self.ctr
        return d


@dataclass
class BingCrawlStat:
    date: str
    crawled_pages: int
    in_index: int
    crawl_errors: int
    code_2xx: int
    code_4xx: int
    code_5xx: int
    blocked_by_robots: int
    connection_timeouts: int
    dns_failures: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BingQuota:
    daily_quota: int
    monthly_quota: int
    daily_remaining: int = 0
    monthly_remaining: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IndexNowSubmissionRecord:
    submission_id: str
    timestamp: str
    urls_count: int
    urls: List[str]
    endpoint: str
    http_status: int
    is_accepted: bool  # HTTP 200 or 202
    response_message: str
    duration_ms: float = 0.0

    # NON-FABRICATION CONTRACT:
    # Submission acceptance means the IndexNow endpoint accepted the notification for queuing.
    # It does NOT mean the URL is crawled or indexed.
    # Google does NOT participate in IndexNow.
    engine_scope: str = "Bing, Yandex, Seznam, Naver (Google excluded from IndexNow protocol)"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IndexNowQueueItem:
    url: str
    reason: str  # "NEW_URL", "CONTENT_UPDATED", "DELETED"
    discovered_at: str
    content_hash: str
    submission_attempts: int = 0
    status: str = "QUEUED"  # "QUEUED", "SUBMITTED", "FAILED"
    last_submitted: Optional[str] = None
    last_http_status: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
