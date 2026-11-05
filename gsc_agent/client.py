"""
Google Search Console Client for HERMES GSC Intelligence Agent.
Handles OAuth2 token refreshing, auto-retry, rate-limit backoff,
complete pagination, multi-property discovery, and raw response archiving.
"""

from __future__ import annotations
import json
import os
import time
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GSC_API_ROOT = "https://searchconsole.googleapis.com"
GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"


@dataclass
class GSCAuthCredentials:
    client_id: str
    client_secret: str
    refresh_token: str
    access_token: Optional[str] = None
    token_expiry: Optional[datetime] = None


class GSCClient:
    """Enterprise-grade Google Search Console API client."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        site_url: str = "https://aitoolgems.tech/",
        base_dir: Optional[Path | str] = None,
    ):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self._load_env_if_needed()

        self.client_id = client_id or os.environ.get("GSC_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("GSC_CLIENT_SECRET", "")
        self.refresh_token = refresh_token or os.environ.get("GSC_REFRESH_TOKEN", "")
        self.site_url = site_url

        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self.archive_dir = self.base_dir / "data" / "gsc_history" / "raw_responses"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def _load_env_if_needed(self) -> None:
        env_file = self.base_dir / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    def refresh_access_token(self) -> str:
        """Refreshes Google OAuth access token if expired or about to expire within 5 minutes."""
        if not self.is_configured():
            raise RuntimeError("GSC credentials incomplete: GSC_CLIENT_ID, GSC_CLIENT_SECRET, and GSC_REFRESH_TOKEN are required.")

        now_utc = datetime.now(timezone.utc)
        if self._access_token and self._token_expiry and (now_utc < self._token_expiry - timedelta(minutes=5)):
            return self._access_token

        body = urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }).encode("utf-8")

        req = Request(GOOGLE_TOKEN_URL, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        for attempt in range(1, 4):
            try:
                with urlopen(req, timeout=25) as resp:
                    token_data = json.load(resp)
                    self._access_token = token_data["access_token"]
                    expires_in = int(token_data.get("expires_in", 3600))
                    self._token_expiry = now_utc + timedelta(seconds=expires_in)
                    return self._access_token
            except HTTPError as e:
                err_content = e.read().decode("utf-8", errors="replace")
                if attempt == 3 or e.code in (400, 401):
                    raise RuntimeError(f"GSC OAuth refresh failed (HTTP {e.code}): {err_content}")
                time.sleep(2 ** attempt + random.uniform(0.1, 0.5))
            except Exception as e:
                if attempt == 3:
                    raise RuntimeError(f"GSC OAuth network error: {e}")
                time.sleep(2 ** attempt)

        raise RuntimeError("GSC OAuth token refresh exhausted retries.")

    def _headers(self) -> Dict[str, str]:
        token = self.refresh_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "HERMES-GSC-Agent/2.0 (+https://aitoolgems.tech/)"
        }

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
        max_retries: int = 4
    ) -> Dict[str, Any]:
        """Executes authorized request with exponential backoff and jitter."""
        data_bytes = json.dumps(payload).encode("utf-8") if payload else None

        for attempt in range(1, max_retries + 1):
            req = Request(url, data=data_bytes, headers=self._headers(), method=method)
            try:
                with urlopen(req, timeout=40) as resp:
                    res_body = json.load(resp)
                    return res_body
            except HTTPError as e:
                err_text = e.read().decode("utf-8", errors="replace")
                # Handle 429 Too Many Requests or 5xx Server Errors
                if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    retry_after = e.headers.get("Retry-After")
                    wait_time = float(retry_after) if retry_after else (2 ** attempt + random.uniform(0.5, 1.5))
                    time.sleep(wait_time)
                    continue
                raise RuntimeError(f"GSC API error (HTTP {e.code}) on {url}: {err_text}")
            except Exception as e:
                if attempt < max_retries:
                    time.sleep(2 ** attempt + random.uniform(0.2, 0.8))
                    continue
                raise RuntimeError(f"GSC Network request failed on {url}: {e}")

        raise RuntimeError(f"GSC request exhausted retries for {url}")

    def list_accessible_sites(self) -> List[Dict[str, Any]]:
        """Lists all Search Console properties accessible to the authenticated credentials."""
        url = f"{GSC_API_ROOT}/webmasters/v3/sites"
        res = self._make_request(url, method="GET")
        return res.get("siteEntry", [])

    def query_search_analytics_paginated(
        self,
        start_date: str,
        end_date: str,
        dimensions: List[str],
        property_url: Optional[str] = None,
        dimension_filters: Optional[List[Dict[str, Any]]] = None,
        search_type: str = "web",
        aggregation_type: str = "auto",
        max_total_rows: int = 50000,
        page_size: int = 5000,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes Search Analytics query with full pagination loop.
        Guarantees retrieval beyond the single 25,000 row API limit.
        Stores raw responses for empirical audit trails.
        """
        target_property = property_url or self.site_url
        clean_prop = quote(target_property, safe="")
        endpoint = f"{GSC_API_ROOT}/webmasters/v3/sites/{clean_prop}/searchAnalytics/query"

        all_rows: List[Dict[str, Any]] = []
        start_row = 0

        query_metadata = {
            "property": target_property,
            "start_date": start_date,
            "end_date": end_date,
            "dimensions": dimensions,
            "filters": dimension_filters or [],
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        while start_row < max_total_rows:
            current_page_size = min(page_size, 25000)
            payload: Dict[str, Any] = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": dimensions,
                "searchType": search_type,
                "aggregationType": aggregation_type,
                "rowLimit": current_page_size,
                "startRow": start_row,
            }
            if dimension_filters:
                payload["dimensionFilterGroups"] = [{
                    "filters": dimension_filters
                }]

            res = self._make_request(endpoint, method="POST", payload=payload)
            rows = res.get("rows", [])
            if not rows:
                break

            all_rows.extend(rows)
            start_row += len(rows)

            # If we received fewer rows than requested, pagination is exhausted
            if len(rows) < current_page_size:
                break

        query_metadata["total_rows_retrieved"] = len(all_rows)

        # Archive raw response
        safe_date = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dims_slug = "_".join(dimensions)
        archive_file = self.archive_dir / f"gsc_{dims_slug}_{safe_date}.json"
        try:
            archive_file.write_text(
                json.dumps({"metadata": query_metadata, "rows": all_rows}, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

        return all_rows, query_metadata

    def inspect_url(
        self,
        inspection_url: str,
        site_url: Optional[str] = None,
        language_code: str = "en-US"
    ) -> Dict[str, Any]:
        """Calls Google Search Console URL Inspection API for genuine indexing state."""
        endpoint = f"{GSC_API_ROOT}/v1/urlInspection/index:inspect"
        payload = {
            "inspectionUrl": inspection_url,
            "siteUrl": site_url or self.site_url,
            "languageCode": language_code
        }
        res = self._make_request(endpoint, method="POST", payload=payload)
        return res.get("inspectionResult", {})
