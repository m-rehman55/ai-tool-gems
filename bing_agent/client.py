"""
client.py - Official Bing Webmaster Tools JSON API Client.

Directly communicates with https://ssl.bing.com/webmaster/api.svc/json/
using authorized BING_API_KEY / BING_WEBMASTER_API_KEY.

Provides full access to:
- GetUserSites: Verified properties
- GetUrlSubmissionQuota: Daily and monthly limits
- GetCrawlStats: Daily crawl status and in-index count
- GetQueryStats: Empirical Bing search queries, impressions, clicks, positions
- GetPageStats: Page-level performance
- GetCrawlErrors: Specific 4xx, 5xx, or robot-blocked URLs
- GetFeedbacks: Bing SEO recommendations
- SubmitUrlBatch: Official batch URL submission
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bing_agent.models import (
    BingCrawlStat,
    BingPageStat,
    BingQueryStat,
    BingQuota,
    BingSite,
    parse_bing_date,
)

logger = logging.getLogger("bing_agent.client")


def _load_env_file() -> None:
    """Loads root .env file if BING_API_KEY is not already in environment."""
    if os.getenv("BING_API_KEY") or os.getenv("BING_WEBMASTER_API_KEY"):
        return
    proj_dir = Path(__file__).resolve().parent.parent
    env_file = proj_dir / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class BingWebmasterClient:
    """Official Bing Webmaster Tools REST/JSON API Client."""

    BASE_URL = "https://ssl.bing.com/webmaster/api.svc/json"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_site_url: str = "https://aitoolgems.tech/",
        timeout: int = 15,
    ):
        _load_env_file()
        self.api_key = (
            api_key
            or os.getenv("BING_API_KEY", "").strip()
            or os.getenv("BING_WEBMASTER_API_KEY", "").strip()
        )
        self.default_site_url = default_site_url if default_site_url.endswith("/") else default_site_url + "/"
        self.timeout = timeout

    @property
    def is_authorized(self) -> bool:
        """Returns True if a non-empty API key is present."""
        return bool(self.api_key)

    def _call(self, endpoint: str, params: Optional[Dict[str, Any]] = None, post_data: Optional[Dict[str, Any]] = None) -> Any:
        """Executes an authenticated JSON request to Bing Webmaster Tools API."""
        if not self.is_authorized:
            raise PermissionError("Bing Webmaster API Key is missing. Set BING_API_KEY or BING_WEBMASTER_API_KEY in .env.")

        query_params = {"apikey": self.api_key}
        if params:
            query_params.update(params)

        qs = urllib.parse.urlencode(query_params)
        full_url = f"{self.BASE_URL}/{endpoint}?{qs}"

        headers = {
            "Accept": "application/json",
            "User-Agent": "AIToolGems-BingAgent/1.0",
        }

        data_bytes = None
        if post_data is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
            data_bytes = json.dumps(post_data).encode("utf-8")

        req = urllib.request.Request(full_url, data=data_bytes, headers=headers, method="POST" if post_data else "GET")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                parsed = json.loads(raw)
                return parsed.get("d", parsed)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            logger.error(f"Bing Webmaster API HTTP Error {e.code} on {endpoint}: {err_body}")
            if "invalid" in err_body.lower() or "key" in err_body.lower() or e.code in (400, 401, 403):
                raise PermissionError(f"Bing API {endpoint} BLOCKED (HTTP {e.code}): InvalidApiKey - {err_body}")
            raise RuntimeError(f"Bing API {endpoint} failed (HTTP {e.code}): {e.reason} - {err_body}")
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Bing Webmaster API Connection Error on {endpoint}: {e}")
            raise

    # ── Official API Operations ───────────────────────────────────────────────

    def get_user_sites(self) -> List[BingSite]:
        """Retrieves list of verified website properties registered to this API key."""
        res = self._call("GetUserSites")
        if not isinstance(res, list):
            return []
        sites = []
        for s in res:
            sites.append(BingSite(
                url=s.get("Url", ""),
                is_verified=bool(s.get("IsVerified", False)),
                auth_code=s.get("AuthenticationCode", ""),
                dns_verification_code=s.get("DnsVerificationCode", ""),
            ))
        return sites

    def get_submission_quota(self, site_url: Optional[str] = None) -> BingQuota:
        """Retrieves daily and monthly URL submission quota remaining."""
        target_site = site_url or self.default_site_url
        res = self._call("GetUrlSubmissionQuota", {"siteUrl": target_site})
        if not isinstance(res, dict):
            return BingQuota(daily_quota=0, monthly_quota=0)
        return BingQuota(
            daily_quota=int(res.get("DailyQuota", 0)),
            monthly_quota=int(res.get("MonthlyQuota", 0)),
            daily_remaining=int(res.get("DailyQuota", 0)),
            monthly_remaining=int(res.get("MonthlyQuota", 0)),
        )

    def get_crawl_stats(self, site_url: Optional[str] = None) -> List[BingCrawlStat]:
        """Retrieves historical crawl statistics and in-index counts."""
        target_site = site_url or self.default_site_url
        res = self._call("GetCrawlStats", {"siteUrl": target_site})
        if not isinstance(res, list):
            return []
        stats = []
        for r in res:
            stats.append(BingCrawlStat(
                date=parse_bing_date(r.get("Date", "")),
                crawled_pages=int(r.get("CrawledPages", 0)),
                in_index=int(r.get("InIndex", 0)),
                crawl_errors=int(r.get("CrawlErrors", 0)),
                code_2xx=int(r.get("Code2xx", 0)),
                code_4xx=int(r.get("Code4xx", 0)),
                code_5xx=int(r.get("Code5xx", 0)),
                blocked_by_robots=int(r.get("BlockedByRobotsTxt", 0)),
                connection_timeouts=int(r.get("ConnectionTimeout", 0)),
                dns_failures=int(r.get("DnsFailures", 0)),
            ))
        return stats

    def get_query_stats(self, site_url: Optional[str] = None) -> List[BingQueryStat]:
        """Retrieves empirical search query impressions, clicks, and rankings on Bing."""
        target_site = site_url or self.default_site_url
        res = self._call("GetQueryStats", {"siteUrl": target_site})
        if not isinstance(res, list):
            return []
        queries = []
        for r in res:
            queries.append(BingQueryStat(
                query=r.get("Query", ""),
                date=parse_bing_date(r.get("Date", "")),
                clicks=int(r.get("Clicks", 0)),
                impressions=int(r.get("Impressions", 0)),
                avg_click_position=float(r.get("AvgClickPosition", -1)),
                avg_impression_position=float(r.get("AvgImpressionPosition", -1)),
            ))
        return queries

    def get_page_stats(self, site_url: Optional[str] = None) -> List[BingPageStat]:
        """Retrieves page-level search performance on Bing."""
        target_site = site_url or self.default_site_url
        res = self._call("GetPageStats", {"siteUrl": target_site})
        if not isinstance(res, list):
            return []
        pages = []
        for r in res:
            pages.append(BingPageStat(
                page=r.get("Query", r.get("Page", "")),
                date=parse_bing_date(r.get("Date", "")),
                clicks=int(r.get("Clicks", 0)),
                impressions=int(r.get("Impressions", 0)),
                avg_click_position=float(r.get("AvgClickPosition", -1)),
                avg_impression_position=float(r.get("AvgImpressionPosition", -1)),
            ))
        return pages

    def get_crawl_errors(self, site_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves detailed crawl error records."""
        target_site = site_url or self.default_site_url
        try:
            res = self._call("GetCrawlErrors", {"siteUrl": target_site})
            return res if isinstance(res, list) else []
        except Exception:
            return []

    def get_feedbacks(self, site_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves Bing SEO recommendations and site scan feedback."""
        target_site = site_url or self.default_site_url
        try:
            res = self._call("GetFeedbacks", {"siteUrl": target_site})
            return res if isinstance(res, list) else []
        except Exception:
            return []

    def submit_url_batch(self, urls: List[str], site_url: Optional[str] = None) -> Dict[str, Any]:
        """Submits a batch of URLs directly to Bing Webmaster Tools API."""
        target_site = site_url or self.default_site_url
        clean_urls = sorted(list(set(u.strip() for u in urls if u and u.strip())))
        if not clean_urls:
            return {"status": "error", "message": "No URLs provided."}

        payload = {
            "siteUrl": target_site,
            "urlList": clean_urls,
        }
        res = self._call("SubmitUrlBatch", post_data=payload)
        return {
            "status": "success",
            "submitted_count": len(clean_urls),
            "response": res,
        }
