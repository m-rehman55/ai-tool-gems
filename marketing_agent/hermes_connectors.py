"""Free-first online connectors with explicit source-health states."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .hermes_models import ConnectorResult, DataStatus, MetricRecord, Provenance


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GSC_ROOT = "https://searchconsole.googleapis.com"
GA4_ROOT = "https://analyticsdata.googleapis.com/v1beta"
BING_ROOT = "https://ssl.bing.com/webmaster/api.svc/json"


def _json_request(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=body, headers=headers or {}, method=method)
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _google_access_token(prefix: str) -> tuple[str | None, str | None]:
    access_token = os.getenv(f"{prefix}_ACCESS_TOKEN", "").strip()
    if access_token:
        return access_token, None
    client_id = os.getenv("GSC_CLIENT_ID", "").strip()
    client_secret = os.getenv("GSC_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv(f"{prefix}_REFRESH_TOKEN", "").strip()
    if not refresh_token and prefix == "GSC":
        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN", "").strip()
    if not refresh_token:
        cache_file = os.path.join(os.path.dirname(__file__), "data", "gsc_token.json")
        if os.path.isfile(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                refresh_token = cached_data.get("refresh_token", "").strip()
            except Exception:
                pass
    if not all((client_id, client_secret, refresh_token)):
        return None, "OAuth credentials are not configured."
    body = urlencode({"client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token, "grant_type": "refresh_token"}).encode()
    request = Request(GOOGLE_TOKEN_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        token = data.get("access_token")
        return token, None if token else "Google did not return an access token."
    except Exception as exc:
        return None, str(exc)


def _google_result(name: str, status: DataStatus, source: str, error: str | None = None, details: dict[str, Any] | None = None, records: list[MetricRecord] | None = None) -> ConnectorResult:
    return ConnectorResult(name, status, source, records or [], details or {}, error)


def collect_gsc(site_url: str, days: tuple[int, ...] = (7, 28, 90, 180)) -> ConnectorResult:
    token, token_error = _google_access_token("GSC")
    if not token:
        return _google_result("GSC", DataStatus.ACCESS_REQUIRED, "Google Search Console API", token_error, {"required": ["GSC_CLIENT_ID", "GSC_CLIENT_SECRET", "GSC_REFRESH_TOKEN or GSC_ACCESS_TOKEN"]})
    property_url = site_url.rstrip("/") + "/"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    records: list[MetricRecord] = []
    details: dict[str, Any] = {"property": property_url, "windows": {}}
    try:
        encoded = quote(property_url, safe="")
        for window in days:
            end = date.today() - timedelta(days=2)
            start = end - timedelta(days=window - 1)
            payload = {"startDate": start.isoformat(), "endDate": end.isoformat(), "dimensions": ["query", "page", "country", "device"], "rowLimit": 25000, "startRow": 0}
            data = _json_request(f"{GSC_ROOT}/webmasters/v3/sites/{encoded}/searchAnalytics/query", method="POST", payload=payload, headers=headers)
            rows = data.get("rows", [])
            details["windows"][str(window)] = len(rows)
            for row in rows:
                keys = row.get("keys", [])
                values = {"clicks": row.get("clicks"), "impressions": row.get("impressions"), "ctr": row.get("ctr"), "position": row.get("position"), "query": keys[0] if len(keys) > 0 else None, "page": keys[1] if len(keys) > 1 else None, "country": keys[2] if len(keys) > 2 else None, "device": keys[3] if len(keys) > 3 else None}
                records.append(MetricRecord("gsc_search_analytics", values, Provenance("google_search_console", property_url, datetime.now(timezone.utc).isoformat(timespec="seconds"), country=values["country"], device=values["device"], date_range=f"{start.isoformat()}..{end.isoformat()}", confidence="high", status=DataStatus.VERIFIED)))
        status = DataStatus.VERIFIED if records else DataStatus.NO_DATA
        return _google_result("GSC", status, "Google Search Console API", details=details, records=records)
    except HTTPError as exc:
        return _google_result("GSC", DataStatus.ERROR, "Google Search Console API", f"HTTP {exc.code}", details)
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return _google_result("GSC", DataStatus.ERROR, "Google Search Console API", str(exc), details)


def collect_ga4(site_url: str) -> ConnectorResult:
    property_id = os.getenv("GA4_PROPERTY_ID", "").strip()
    token, token_error = _google_access_token("GA4")
    if not property_id or not token:
        missing = []
        if not property_id:
            missing.append("GA4_PROPERTY_ID")
        if not token:
            missing.append("GA4_ACCESS_TOKEN or GA4_REFRESH_TOKEN plus GSC OAuth client credentials")
        return _google_result("GA4", DataStatus.ACCESS_REQUIRED, "Google Analytics Data API", token_error, {"required": missing})
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=27)
    payload = {"dateRanges": [{"startDate": start.isoformat(), "endDate": end.isoformat()}], "dimensions": [{"name": "date"}, {"name": "country"}, {"name": "sessionDefaultChannelGroup"}], "metrics": [{"name": "activeUsers"}, {"name": "sessions"}, {"name": "engagedSessions"}, {"name": "engagementRate"}, {"name": "eventCount"}]}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    try:
        data = _json_request(f"{GA4_ROOT}/properties/{quote(property_id, safe='')}:runReport", method="POST", payload=payload, headers=headers)
        rows = data.get("rows", [])
        records: list[MetricRecord] = []
        for row in rows:
            dimensions = [item.get("value") for item in row.get("dimensionValues", [])]
            metrics = [item.get("value") for item in row.get("metricValues", [])]
            values = {"date": dimensions[0] if len(dimensions) > 0 else None, "country": dimensions[1] if len(dimensions) > 1 else None, "channel": dimensions[2] if len(dimensions) > 2 else None, "activeUsers": metrics[0] if len(metrics) > 0 else None, "sessions": metrics[1] if len(metrics) > 1 else None, "engagedSessions": metrics[2] if len(metrics) > 2 else None, "engagementRate": metrics[3] if len(metrics) > 3 else None, "eventCount": metrics[4] if len(metrics) > 4 else None}
            records.append(MetricRecord("ga4_daily", values, Provenance("google_analytics_data_api", f"properties/{property_id}", datetime.now(timezone.utc).isoformat(timespec="seconds"), country=values["country"], date_range=f"{start.isoformat()}..{end.isoformat()}", confidence="high", status=DataStatus.VERIFIED)))
        return _google_result("GA4", DataStatus.VERIFIED if records else DataStatus.NO_DATA, "Google Analytics Data API", details={"property_id": property_id, "rows": len(rows)}, records=records)
    except HTTPError as exc:
        return _google_result("GA4", DataStatus.ERROR, "Google Analytics Data API", f"HTTP {exc.code}", {"property_id": property_id})
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return _google_result("GA4", DataStatus.ERROR, "Google Analytics Data API", str(exc), {"property_id": property_id})


def collect_bing(site_url: str) -> ConnectorResult:
    api_key = os.getenv("BING_API_KEY", "").strip()
    if not api_key:
        return ConnectorResult("Bing", DataStatus.ACCESS_REQUIRED, "Bing Webmaster API", details={"required": ["BING_API_KEY"]})
    details: dict[str, Any] = {"site_url": site_url}
    try:
        normalized_url = site_url if site_url.endswith("/") else (site_url + "/")
        sites_data = _json_request(f"{BING_ROOT}/GetUserSites?apikey={api_key}")
        crawl_params = urlencode({"apikey": api_key, "siteUrl": normalized_url})
        crawl_data = _json_request(f"{BING_ROOT}/GetCrawlStats?{crawl_params}")
        details.update({
            "verified_sites": len(sites_data.get("d", [])),
            "crawl_records": len(crawl_data.get("d", []))
        })
        return ConnectorResult("Bing", DataStatus.VERIFIED, "Bing Webmaster API", details=details)
    except HTTPError as exc:
        return ConnectorResult("Bing", DataStatus.ERROR, "Bing Webmaster API", details=details, error=f"HTTP {exc.code}")
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return ConnectorResult("Bing", DataStatus.ERROR, "Bing Webmaster API", details=details, error=str(exc))


def unavailable_connectors() -> list[ConnectorResult]:
    return [
        ConnectorResult("SERP", DataStatus.NOT_AVAILABLE, "No free official SERP API configured", details={"reason": "Restricted search-result scraping and paid providers are not used."}),
        ConnectorResult("Backlinks", DataStatus.ACCESS_REQUIRED, "Authorized backlink provider", details={"required": ["An authorized free provider export or API"]}),
        ConnectorResult("Trends", DataStatus.NOT_SUPPORTED, "Google Trends", details={"reason": "No supported official Google Trends API is available in this dependency-free agent."}),
    ]


def collect_online(site_url: str) -> list[ConnectorResult]:
    gsc = collect_gsc(site_url)
    ga4 = collect_ga4(site_url)
    bing = collect_bing(site_url)
    kw_status = DataStatus.VERIFIED if gsc.status in {DataStatus.VERIFIED, DataStatus.NO_DATA} else DataStatus.NOT_AVAILABLE
    kw_details = {"source": "GSC Search Console Query Stream", "records": len(gsc.records)}
    keywords = ConnectorResult("Keywords", kw_status, "Google Search Console Query Stream", details=kw_details)
    return [gsc, ga4, bing, keywords, *unavailable_connectors()]
