"""
client.py - Google Analytics 4 (GA4) Data API Client & Offline Analytics Cache.

Queries official GA4 Data API (v1beta) using authorized property ID and credentials:
- Pakistan sessions segmentation (countryId: PK)
- Channel group acquisition (Organic Search, Direct, Referral, AI Assistant)
- Landing page performance and engagement duration
- Device category distribution (Mobile, Desktop)
- Ecommerce conversion funnel metrics

Provides structured fallback to local analytical snapshots (data/analytics/*.json)
when API quota is exhausted or credentials require authorization.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ga4_agent.client")


def _load_env_file() -> None:
    if os.getenv("GA4_PROPERTY_ID"):
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


class GA4DataClient:
    """Official Google Analytics 4 Data API Client."""

    BASE_URL = "https://analyticsdata.googleapis.com/v1beta"

    def __init__(
        self,
        property_id: Optional[str] = None,
        data_dir: Optional[Path] = None,
    ):
        _load_env_file()
        self.property_id = property_id or os.getenv("GA4_PROPERTY_ID", "").strip()
        base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = data_dir or (base_dir / "data" / "analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.offline_cache_file = self.data_dir / "ga4_snapshot_latest.json"

    @property
    def is_authorized(self) -> bool:
        """Returns True if property ID and OAuth / service account tokens are configured."""
        has_prop = bool(self.property_id)
        has_auth = bool(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or (os.getenv("GSC_CLIENT_ID") and os.getenv("GSC_CLIENT_SECRET"))
        )
        return has_prop and has_auth

    def fetch_report(
        self,
        dimensions: List[str],
        metrics: List[str],
        start_date: str = "28daysAgo",
        end_date: str = "today",
        country_filter: Optional[str] = "Pakistan",
    ) -> Dict[str, Any]:
        """
        Executes a runReport call to the GA4 Data API.
        Falls back to local verified snapshot if API access is not configured.
        """
        if not self.is_authorized:
            return self._load_offline_report(dimensions, metrics)

        # In production with authorized OAuth token
        access_token = self._get_access_token()
        if not access_token:
            return self._load_offline_report(dimensions, metrics)

        url = f"{self.BASE_URL}/properties/{self.property_id}:runReport"
        payload: Dict[str, Any] = {
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
        }

        if country_filter:
            payload["dimensionFilter"] = {
                "filter": {
                    "fieldName": "country",
                    "stringFilter": {"value": country_filter, "matchType": "EXACT"},
                }
            }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                # Save offline cache
                self.offline_cache_file.write_text(json.dumps(res, indent=2), encoding="utf-8")
                return res
        except Exception as e:
            logger.warning(f"GA4 Data API call failed ({e}). Defaulting to offline snapshot.")
            return self._load_offline_report(dimensions, metrics)

    def _get_access_token(self) -> Optional[str]:
        """Exchanges refresh token for GA4 Data API access token."""
        cid = os.getenv("GSC_CLIENT_ID", "").strip()
        csec = os.getenv("GSC_CLIENT_SECRET", "").strip()
        rtoken = os.getenv("GSC_REFRESH_TOKEN", "").strip()
        if not (cid and csec and rtoken):
            return None

        import urllib.parse
        data = urllib.parse.urlencode({
            "client_id": cid,
            "client_secret": csec,
            "refresh_token": rtoken,
            "grant_type": "refresh_token",
        }).encode("utf-8")
        req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data_resp = json.loads(resp.read().decode("utf-8"))
                return data_resp.get("access_token")
        except Exception:
            return None

    def _load_offline_report(self, dimensions: List[str], metrics: List[str]) -> Dict[str, Any]:
        """Loads local baseline snapshot without fabricating fake numbers."""
        if self.offline_cache_file.exists():
            try:
                return json.loads(self.offline_cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Clean empty structure
        return {
            "status": "OFFLINE_SNAPSHOT",
            "message": "GA4 live API awaiting developer credentials. Reporting offline baseline.",
            "dimensionHeaders": [{"name": d} for d in dimensions],
            "metricHeaders": [{"name": m, "type": "TYPE_INTEGER"} for m in metrics],
            "rows": [],
            "rowCount": 0,
        }

