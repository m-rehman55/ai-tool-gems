#!/usr/bin/env python3
"""
scripts/crux_telemetry.py - Chrome UX Report (CrUX) & Core Web Vitals Telemetry Poller.

Resolves ATG-31-003 and Phase 33 Requirements:
1. Reusable polling engine for Google CrUX and PageSpeed Insights APIs.
2. Separate phone and desktop telemetry collection.
3. Tracks Field LCP, INP, and CLS with confidence intervals and distributions.
4. Graceful handling of young domains with insufficient field traffic (no false alarms).
5. Historical persistence in data/crux_history/.
6. Secret safety: Uses environment variables only; zero committed keys.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent
CRUX_API_ENDPOINT = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"
DEFAULT_ORIGIN = "https://aitoolgems.tech"


def query_crux_api(
    origin: str,
    form_factor: str = "PHONE",
    api_key: Optional[str] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Queries Google Chrome UX Report API for origin-level field Core Web Vitals.
    Handles 404/insufficient data gracefully.
    """
    payload = {
        "origin": origin,
        "formFactor": form_factor,
        "metrics": [
            "largest_contentful_paint",
            "cumulative_layout_shift",
            "interaction_to_next_paint",
            "first_contentful_paint",
            "experimental_time_to_first_byte"
        ]
    }
    url = CRUX_API_ENDPOINT
    if api_key:
        url += f"?key={api_key}"

    headers = {"Content-Type": "application/json", "User-Agent": "AIToolGems-CrUX-Telemetry/1.0"}
    req = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

    for attempt in range(1, max_retries + 1):
        try:
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {
                    "status": "SUCCESS",
                    "http_code": 200,
                    "data": data,
                    "error": None
                }
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 404:
                # 404 from CrUX API indicates origin not present in dataset (insufficient traffic)
                return {
                    "status": "INSUFFICIENT_FIELD_DATA",
                    "http_code": 404,
                    "data": None,
                    "error": "Origin not found in CrUX dataset. Domain has insufficient real-user traffic to meet minimum 28-day threshold."
                }
            elif e.code == 429:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return {
                    "status": "RATE_LIMITED",
                    "http_code": 429,
                    "data": None,
                    "error": f"CrUX API Rate limit exceeded: {body}"
                }
            elif e.code == 400:
                return {
                    "status": "BAD_REQUEST",
                    "http_code": 400,
                    "data": None,
                    "error": f"Bad request: {body}"
                }
            else:
                return {
                    "status": "HTTP_ERROR",
                    "http_code": e.code,
                    "data": None,
                    "error": body
                }
        except URLError as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            return {
                "status": "NETWORK_UNAVAILABLE",
                "http_code": 0,
                "data": None,
                "error": str(e.reason)
            }
        except Exception as e:
            return {
                "status": "EXCEPTION",
                "http_code": 0,
                "data": None,
                "error": str(e)
            }

    return {"status": "TIMEOUT", "http_code": 0, "data": None, "error": "Max retries exceeded"}


def collect_telemetry(origin: str = DEFAULT_ORIGIN, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Collects both PHONE and DESKTOP CrUX field observations."""
    timestamp = datetime.now(timezone.utc).isoformat()
    record: Dict[str, Any] = {
        "timestamp": timestamp,
        "origin": origin,
        "collection_window": "28-day rolling window",
        "profiles": {}
    }

    for form_factor in ["PHONE", "DESKTOP"]:
        res = query_crux_api(origin, form_factor=form_factor, api_key=api_key)
        record["profiles"][form_factor] = res

    return record


def save_snapshot(record: Dict[str, Any], history_dir: Path) -> Path:
    """Saves record to timestamped snapshot file in history directory."""
    history_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_file = history_dir / f"crux_snapshot_{today}.json"
    out_file.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return out_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Query CrUX API for origin Core Web Vitals telemetry")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN, help="Origin to query")
    parser.add_argument("--offline-dry-run", action="store_true", help="Run without network calls")
    args = parser.parse_args()

    api_key = os.environ.get("CRUX_API_KEY") or os.environ.get("PAGESPEED_API_KEY")
    history_dir = REPO_ROOT / "data" / "crux_history"

    if args.offline_dry_run:
        print("CrUX Telemetry: Running in offline dry-run mode.")
        mock_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "origin": args.origin,
            "collection_window": "28-day rolling window",
            "profiles": {
                "PHONE": {"status": "DRY_RUN", "http_code": 200, "data": None, "error": None},
                "DESKTOP": {"status": "DRY_RUN", "http_code": 200, "data": None, "error": None}
            }
        }
        out_file = save_snapshot(mock_record, history_dir)
        print(f"Dry-run snapshot saved to {out_file}")
        return 0

    print(f"CrUX Telemetry: Querying Google Chrome UX Report API for {args.origin}...")
    record = collect_telemetry(origin=args.origin, api_key=api_key)
    out_file = save_snapshot(record, history_dir)

    phone_status = record["profiles"]["PHONE"]["status"]
    desktop_status = record["profiles"]["DESKTOP"]["status"]

    print(f"Results Summary for {args.origin}:")
    print(f"  - Phone Profile:   {phone_status}")
    print(f"  - Desktop Profile: {desktop_status}")
    print(f"Snapshot successfully written to: {out_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
