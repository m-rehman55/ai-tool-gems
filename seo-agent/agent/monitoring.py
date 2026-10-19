#!/usr/bin/env python3
"""
Performance & Search Console Monitoring for AIToolGems
-------------------------------------------------------
Pulls live Google Search Console metrics (impressions, clicks, CTR, average position)
when authorized environment tokens are configured.
Gracefully operates offline without crashing if API access is unavailable.
"""

from __future__ import annotations
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

@dataclass
class SearchConsoleQuery:
    query: str
    clicks: int
    impressions: int
    ctr: float
    position: float

@dataclass
class PerformanceMetrics:
    connected: bool
    site_url: str
    total_impressions: int = 0
    total_clicks: int = 0
    average_ctr: float = 0.0
    average_position: float = 0.0
    top_queries: List[SearchConsoleQuery] = field(default_factory=list)
    status_message: str = "Search Console offline (credentials not configured)"
    error: Optional[str] = None

class PerformanceMonitor:
    """Interacts with Google Search Console API."""

    def __init__(
        self,
        site_url: str = "sc-domain:aitoolgems.tech",
        client_id_env: str = "GSC_CLIENT_ID",
        client_secret_env: str = "GSC_CLIENT_SECRET",
        refresh_token_env: str = "GSC_REFRESH_TOKEN",
    ):
        self.site_url = site_url
        if not (os.environ.get(client_id_env) and os.environ.get(refresh_token_env)):
            env_file = Path(".env")
            if env_file.exists():
                try:
                    with open(env_file, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                k_s = k.strip()
                                if k_s not in os.environ:
                                    os.environ[k_s] = v.strip().strip('"').strip("'")
                except Exception:
                    pass
        self.client_id = os.environ.get(client_id_env, "").strip()
        self.client_secret = os.environ.get(client_secret_env, "").strip()
        self.refresh_token = os.environ.get(refresh_token_env, "").strip()

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    def _get_access_token(self) -> Optional[str]:
        """Exchanges refresh token for short-lived access token."""
        if not self.is_configured():
            return None

        token_url = "https://oauth2.googleapis.com/token"
        data = urllib.parse.urlencode({
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }).encode("utf-8")

        req = urllib.request.Request(token_url, data=data, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("access_token")
        except Exception:
            return None

    def fetch_metrics(self, days: int = 28) -> PerformanceMetrics:
        """Fetches recent search metrics for aitoolgems.tech."""
        if not self.is_configured():
            return PerformanceMetrics(
                connected=False,
                site_url=self.site_url,
                status_message="GSC offline: Environment secrets not set.",
            )

        token = self._get_access_token()
        if not token:
            return PerformanceMetrics(
                connected=False,
                site_url=self.site_url,
                error="OAuth token exchange failed",
                status_message="GSC auth error: Invalid client credentials or refresh token.",
            )

        # Date range
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
        start_date = (datetime.now(timezone.utc) - timedelta(days=days + 2)).strftime("%Y-%m-%d")

        payload = json.dumps({
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 15,
        }).encode("utf-8")

        candidate_urls = [
            self.site_url,
            "https://aitoolgems.tech/",
            "https://aitoolgems.tech",
            "sc-domain:aitoolgems.tech",
        ]
        # Deduplicate while preserving order
        unique_candidates = list(dict.fromkeys(candidate_urls))

        last_error = None
        for candidate in unique_candidates:
            api_url = f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(candidate, safe='')}/searchAnalytics/query"
            req = urllib.request.Request(
                api_url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    rows = data.get("rows", [])
                    
                    total_impr = sum(int(r.get("impressions", 0)) for r in rows)
                    total_clk = sum(int(r.get("clicks", 0)) for r in rows)
                    avg_ctr = (total_clk / total_impr * 100.0) if total_impr > 0 else 0.0
                    avg_pos = sum(float(r.get("position", 0)) for r in rows) / len(rows) if rows else 0.0

                    top_q = [
                        SearchConsoleQuery(
                            query=r.get("keys", [""])[0],
                            clicks=int(r.get("clicks", 0)),
                            impressions=int(r.get("impressions", 0)),
                            ctr=round(float(r.get("ctr", 0)) * 100, 2),
                            position=round(float(r.get("position", 0)), 1),
                        )
                        for r in rows
                    ]

                    return PerformanceMetrics(
                        connected=True,
                        site_url=candidate,
                        total_impressions=total_impr,
                        total_clicks=total_clk,
                        average_ctr=round(avg_ctr, 2),
                        average_position=round(avg_pos, 1),
                        top_queries=top_q,
                        status_message=f"Live GSC data retrieved ({len(rows)} queries, {total_impr} impressions)",
                    )
            except urllib.error.HTTPError as e:
                last_error = f"HTTP {e.code}"
                continue
            except Exception as e:
                last_error = str(e)
                continue

        return PerformanceMetrics(
            connected=False,
            site_url=self.site_url,
            error=last_error,
            status_message=f"GSC query failed ({last_error}) across all candidate properties",
        )
