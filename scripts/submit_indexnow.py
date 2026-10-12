#!/usr/bin/env python3
"""
AIToolGems IndexNow Automated Dispatcher
Submits changed and all sitemap URLs to IndexNow (IndexNow.org and Bing API)
Ensures Ahrefs, Bing, Yandex, and Seznam index updated content immediately.
"""

import sys
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

INDEXNOW_KEY = "e1a8c47f9d2b4f30a6c8116de5b97042"
HOST = "aitoolgems.tech"
BASE_DIR = Path(__file__).resolve().parent.parent

ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow"
]


def get_sitemap_urls() -> List[str]:
    """Extract all indexable URLs from sitemap.xml."""
    sitemap_path = BASE_DIR / "sitemap.xml"
    if not sitemap_path.exists():
        print(f"❌ Error: sitemap.xml not found at {sitemap_path}", file=sys.stderr)
        return []
    content = sitemap_path.read_text(encoding="utf-8")
    return re.findall(r"<loc>(.*?)</loc>", content)


def submit_to_indexnow(urls: List[str], dry_run: bool = False) -> Dict[str, Any]:
    """Submit a list of URLs to the IndexNow protocol across all major endpoints."""
    if not urls:
        return {"status": "error", "message": "No URLs provided for IndexNow submission."}

    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{HOST}/{INDEXNOW_KEY}.txt",
        "urlList": urls
    }

    if dry_run:
        return {
            "status": "dry_run",
            "urls_count": len(urls),
            "sample": urls[:5]
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
            with urllib.request.urlopen(req, timeout=12) as resp:
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
        "submitted_count": len(urls),
        "endpoints": results
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AIToolGems IndexNow Fast Dispatcher")
    parser.add_argument("--all", action="store_true", help="Submit all URLs from sitemap.xml")
    parser.add_argument("--dry-run", action="store_true", help="Simulate submission without network call")
    parser.add_argument("--urls", nargs="+", help="Specific URLs to submit")

    args = parser.parse_args()

    if args.urls:
        target_urls = args.urls
    else:
        target_urls = get_sitemap_urls()

    print("=" * 60)
    print("⚡ AIToolGems IndexNow Automated Dispatcher")
    print(f"• Target URLs: {len(target_urls)}")
    print(f"• Dry Run: {args.dry_run}")
    print("=" * 60)

    result = submit_to_indexnow(target_urls, dry_run=args.dry_run)

    print(json.dumps(result, indent=2))
    if result.get("status") in ("success", "dry_run"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
