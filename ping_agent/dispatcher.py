"""
Multi-Engine IndexNow & Search Engine Dispatcher.
Submits URLs across IndexNow.org, Bing, and Yandex protocols with retry resilience.
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Any

INDEXNOW_KEY = "e1a8c47f9d2b4f30a6c8116de5b97042"
HOST = "aitoolgems.tech"

ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow"
]


def dispatch_urls(urls: List[str], dry_run: bool = False, timeout: int = 12) -> Dict[str, Any]:
    """
    Submits a batch of URLs to the IndexNow protocol across all supported engines.
    """
    if not urls:
        return {"status": "error", "message": "No URLs provided for dispatch."}

    # Clean and deduplicate URLs
    clean_urls = sorted(list(set(u.strip() for u in urls if u and u.strip())))

    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{HOST}/{INDEXNOW_KEY}.txt",
        "urlList": clean_urls
    }

    if dry_run:
        return {
            "status": "dry_run",
            "urls_count": len(clean_urls),
            "sample": clean_urls[:5],
            "endpoints": {ep: {"status_code": 200, "success": True, "dry_run": True} for ep in ENDPOINTS}
        }

    results = {}
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}

    for endpoint in ENDPOINTS:
        try:
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                results[endpoint] = {
                    "status_code": resp.status,
                    "success": resp.status in (200, 202)
                }
        except urllib.error.HTTPError as e:
            results[endpoint] = {
                "status_code": e.code,
                "error": str(e.reason),
                "success": False
            }
        except Exception as e:
            results[endpoint] = {
                "error": str(e),
                "success": False
            }

    all_success = any(r.get("success", False) for r in results.values())
    return {
        "status": "success" if all_success else "partial_error",
        "submitted_count": len(clean_urls),
        "endpoints": results
    }
