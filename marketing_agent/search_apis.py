"""Dependency-free Google Search Console + Bing Webmaster API clients."""

from __future__ import annotations

import json
import os
import webbrowser
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dataclasses import dataclass, field
from typing import Any

# ── Google OAuth2 helpers ──────────────────────────────────────────────────────

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GSC_API_ROOT = "https://searchconsole.googleapis.com"

# Scopes — Read-only is enough for monitoring
GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"

# Path where the refresh token is stored (inside the package, gitignored)
_TOKEN_CACHE = os.path.join(os.path.dirname(__file__), "data", "gsc_token.json")


@dataclass
class GSCClient:
    """Talks to Google Search Console API using OAuth2 desktop flow.

    First run opens a browser for consent. Subsequent runs refresh the token
    silently using the cached refresh token.
    """

    client_id: str
    client_secret: str
    site_url: str  # e.g. "https://aitoolgems.tech"

    _access_token: str | None = field(default=None, init=False)
    _token_expiry: datetime | None = field(default=None, init=False)

    # ── token lifecycle ────────────────────────────────────────────────────────

    def _save_token(self, data: dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(_TOKEN_CACHE), exist_ok=True)
        with open(_TOKEN_CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _load_token(self) -> dict[str, Any] | None:
        try:
            with open(_TOKEN_CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _refresh_access_token(self) -> None:
        cached = self._load_token()
        if not cached:
            raise RuntimeError("No cached token — run authorize() first")
        if self._access_token and self._token_expiry and (
            datetime.now(timezone.utc) < self._token_expiry - timedelta(minutes=5)
        ):
            return  # still valid

        body = urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": cached["refresh_token"],
            "grant_type": "refresh_token",
        }).encode()
        req = Request(GOOGLE_TOKEN_URL, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urlopen(req, timeout=20) as resp:
            token_data = json.load(resp)
        self._access_token = token_data["access_token"]
        # Google returns expiry in seconds; clamp to 1h for safety
        self._token_expiry = datetime.now(timezone.utc) + timedelta(
            seconds=min(token_data.get("expires_in", 3600), 3600)
        )

    # ── public API ──────────────────────────────────────────────────────────────

    def authorize(self, test_mode: bool = True) -> None:
        """Open browser for first-time consent. Cache refresh token after."""
        auth_params = urlencode({
            "client_id": self.client_id,
            "redirect_uri": "http://localhost:8080/",
            "response_type": "code",
            "scope": GSC_SCOPE,
            "access_type": "offline",
            "prompt": "consent" if test_mode else "none",
        })
        url = f"{GOOGLE_AUTH_URL}?{auth_params}"
        webbrowser.open(url)
        print(
            "→ Browser opened for Google consent. "
            "Allow access, then paste the verification code from the URL bar: "
            "(the URL will be like http://localhost:8080/?code=4/0AXe...)\n"
            "→ Paste the code here and press Enter:"
        )
        code = input().strip()
        if not code:
            raise RuntimeError("No authorization code provided")

        body = urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:8080/",
        }).encode()
        req = Request(GOOGLE_TOKEN_URL, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urlopen(req, timeout=20) as resp:
            token_data = json.load(resp)
        self._save_token(token_data)
        self._access_token = token_data["access_token"]
        self._token_expiry = datetime.now(timezone.utc) + timedelta(
            seconds=min(token_data.get("expires_in", 3600), 3600)
        )
        print("✓ Token saved — future runs refresh silently.")

    def _headers(self) -> dict[str, str]:
        self._refresh_access_token()
        assert self._access_token
        return {"Authorization": f"Bearer {self._access_token}", "Accept": "application/json"}

    # ── GSC queries ────────────────────────────────────────────────────────────

    def _gsc_get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call GSC API — path is like 'webmasters/v3/sites'."""
        url = f"{GSC_API_ROOT}/{path}"
        if params:
            url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
        req = Request(url, headers=self._headers())
        with urlopen(req, timeout=30) as resp:
            return json.load(resp)

    def list_sites(self) -> list[dict[str, Any]]:
        """Return all Search Console properties for this account."""
        return self._gsc_get("webmasters/v3/sites").get("siteEntry", [])

    def get_site_status(self) -> dict[str, Any]:
        """Site info for the primary site."""
        site_url = self.site_url.rstrip("/")
        return self._gsc_get(f"webmasters/v3/sites/{quote(site_url, safe='')}")

    def query_analytics(
        self,
        start_date: str,
        end_date: str,
        dimensions: tuple[str, ...] = ("query", "page"),
        row_limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Impressions, clicks, CTR, position for date range.

        Returns top rows by impressions.
        """
        site_url = self.site_url.rstrip("/")
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": list(dimensions),
            "rowLimit": row_limit,
            "startRow": 0,
        }
        req = Request(
            f"{GSC_API_ROOT}/webmasters/v3/sites/{quote(site_url, safe='')}/searchAnalytics/query",
            data=json.dumps(body).encode(),
            headers=self._headers(),
            method="POST",
        )
        req.add_header("Content-Type", "application/json")
        with urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        return data.get("rows", [])

    def get_coverage_issues(self) -> list[dict[str, Any]]:
        """Return recent indexing coverage errors (not available via read-only)."""
        return []


# ── Bing Webmaster helpers ──────────────────────────────────────────────────────

BING_API_BASE = "https://ssl.bing.com/webmaster/api.svc/json"


@dataclass
class BingClient:
    """Talks to Bing Webmaster API with a simple API key."""

    api_key: str
    site_url: str

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{BING_API_BASE}/{endpoint}"
        all_params = {"apikey": self.api_key}
        if params:
            all_params.update(params)
        url += "?" + urlencode(all_params)
        req = Request(url, headers={"Accept": "application/json"}, method="GET")
        try:
            with urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except HTTPError as exc:
            return {"error": exc.code, "body": exc.read().decode("utf-8", errors="replace")}

    def site_info(self) -> dict[str, Any]:
        """Get site ownership + crawl stats."""
        return self._get("GetSite", {"siteUrl": self.site_url})

    def submit_sitemap(self, sitemap_url: str) -> dict[str, Any]:
        """Ask Bing to re-crawl a sitemap."""
        return self._get("SubmitSiteMap", {"siteUrl": self.site_url, "sitemapUrl": sitemap_url})

    def crawl_stats(self) -> dict[str, Any]:
        """Last crawl date, pages crawled, etc."""
        return self._get("GetCrawlStats", {"siteUrl": self.site_url})


# ── integrated report builder ───────────────────────────────────────────────────

def build_search_report(
    gsc: GSCClient,
    bing: BingClient,
    days: int = 7,
) -> dict[str, Any]:
    """Pull data from both APIs and build a Telegram-ready report dict.

    Returns a plain dict — the caller formats it however they like.
    """
    today = datetime.now().date()
    start = (today - timedelta(days=days)).isoformat()
    end = today.isoformat()

    # GSC data
    try:
        rows = gsc.query_analytics(start, end, dimensions=("query", "page"), row_limit=10)
        total_impressions = sum(int(r.get("impressions", 0)) for r in rows)
        total_clicks = sum(int(r.get("clicks", 0)) for r in rows)
        top_queries = sorted(rows, key=lambda r: int(r.get("impressions", 0)), reverse=True)[:5]
        # GSC total from response metadata if available
        gsc_metadata = {"total_impressions": total_impressions, "total_clicks": total_clicks}
    except Exception as exc:
        top_queries = []
        gsc_metadata = {"error": str(exc)}

    # Bing data
    try:
        site_info = bing.site_info()
        bing_status = site_info.get("siteInfo", {})
        bing_crawl = bing.crawl_stats()
        bing_crawl_data = bing_crawl.get("crawlStats", {})
    except Exception as exc:
        bing_status = {"error": str(exc)}
        bing_crawl_data = {}

    # GSC site status
    try:
        site_status = gsc.get_site_status()
    except Exception as exc:
        site_status = {"error": str(exc)}

    return {
        "period": f"{start} → {end}",
        "gsc": {
            "metadata": gsc_metadata,
            "top_queries": top_queries,
            "site_status": site_status,
        },
        "bing": {
            "site_info": bing_status,
            "crawl_stats": bing_crawl_data,
        },
    }
