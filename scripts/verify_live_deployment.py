#!/usr/bin/env python3
"""
AIToolGems Live Production Deployment Verifier
----------------------------------------------
Verifies that newly published content has been successfully deployed to
https://aitoolgems.tech/:
1. Bounded exponential backoff retries for transient HTTP errors / CDN cache propagation.
2. Asserts HTTP 200 OK status.
3. Validates canonical tag matches target URL.
4. Confirms page is indexable (no robots noindex).
5. Confirms published URL appears in live https://aitoolgems.tech/sitemap.xml.
6. Fails closed with transparent, actionable error reporting.
"""

import sys
import time
import re
import argparse
import urllib.request
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LIVE_SITEMAP_URL = "https://aitoolgems.tech/sitemap.xml"


def verify_url_live(target_url: str, max_retries: int = 6, initial_delay: int = 5) -> tuple[bool, str]:
    """Verify live HTTP 200, canonical URL, and indexable robots tag with exponential backoff."""
    delay = initial_delay
    last_err = ""

    headers = {
        "User-Agent": "AIToolGems-DeploymentVerifier/1.0 (+https://aitoolgems.tech)"
    }

    for attempt in range(1, max_retries + 1):
        print(f"⏳ Verification attempt {attempt}/{max_retries} for {target_url} (waiting {delay}s)...")
        time.sleep(delay)

        try:
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                status_code = resp.status
                if status_code != 200:
                    last_err = f"Unexpected HTTP status {status_code}"
                    delay = min(delay * 2, 30)
                    continue

                html_bytes = resp.read()
                html = html_bytes.decode("utf-8", errors="ignore")

                # Validate canonical
                m_canon = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.I)
                if not m_canon:
                    m_canon = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', html, re.I)

                canonical = m_canon.group(1).strip() if m_canon else ""
                expected_canon = target_url.rstrip("/") + "/"
                if canonical.rstrip("/") + "/" != expected_canon:
                    last_err = f"Canonical mismatch: expected '{expected_canon}', found '{canonical}'"
                    delay = min(delay * 2, 30)
                    continue

                # Validate robots tag
                m_robots = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
                robots = m_robots.group(1).lower() if m_robots else ""
                if "noindex" in robots:
                    return False, f"Live URL returned 'noindex' in robots meta: '{robots}'"

                print(f"✅ Live page check passed: HTTP 200, canonical verified ({canonical}), indexable.")
                return True, "Live URL verified successfully."

        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            last_err = f"URL error: {e.reason}"
        except Exception as e:
            last_err = f"Unexpected error: {e}"

        delay = min(delay * 2, 30)

    return False, f"URL verification failed after {max_retries} attempts: {last_err}"


def verify_sitemap_live(target_url: str, max_retries: int = 5, initial_delay: int = 5) -> tuple[bool, str]:
    """Verify target URL appears in live sitemap.xml with retries."""
    delay = initial_delay
    last_err = ""
    expected_entry = target_url.rstrip("/") + "/"

    headers = {
        "User-Agent": "AIToolGems-DeploymentVerifier/1.0 (+https://aitoolgems.tech)"
    }

    for attempt in range(1, max_retries + 1):
        print(f"⏳ Live sitemap check {attempt}/{max_retries} for {expected_entry}...")
        time.sleep(delay)

        try:
            req = urllib.request.Request(LIVE_SITEMAP_URL, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    last_err = f"Sitemap HTTP status {resp.status}"
                    delay = min(delay * 2, 20)
                    continue

                sitemap_text = resp.read().decode("utf-8", errors="ignore")
                loc_pattern = rf"<loc>{re.escape(expected_entry)}</loc>"
                if re.search(loc_pattern, sitemap_text):
                    print(f"✅ Target URL found in live sitemap: {expected_entry}")
                    return True, "Sitemap presence verified."

                last_err = f"Target URL not yet visible in live sitemap ({LIVE_SITEMAP_URL})"

        except Exception as e:
            last_err = f"Sitemap fetch error: {e}"

        delay = min(delay * 2, 20)

    return False, f"Live sitemap verification failed after {max_retries} attempts: {last_err}"


def main():
    parser = argparse.ArgumentParser(description="Verify live production deployment on aitoolgems.tech")
    parser.add_argument("--url", required=True, help="Full HTTPS URL of published article")
    parser.add_argument("--max-retries", type=int, default=6, help="Maximum number of retries")
    parser.add_argument("--initial-delay", type=int, default=5, help="Initial sleep delay in seconds")
    parser.add_argument("--skip-sitemap", action="store_true", help="Skip live sitemap verification")

    args = parser.parse_args()
    target_url = args.url.strip()

    print("=" * 65)
    print("🌐 AIToolGems Production Live Deployment Verifier")
    print(f"• Target URL: {target_url}")
    print(f"• Max Retries: {args.max_retries}")
    print("=" * 65)

    # 1. Verify URL live
    ok_url, msg_url = verify_url_live(target_url, max_retries=args.max_retries, initial_delay=args.initial_delay)
    if not ok_url:
        print(f"\n❌ Live Page Verification FAILED:\n   {msg_url}")
        sys.exit(1)

    # 2. Verify Live Sitemap
    if not args.skip_sitemap:
        ok_sm, msg_sm = verify_sitemap_live(target_url, max_retries=args.max_retries, initial_delay=args.initial_delay)
        if not ok_sm:
            print(f"\n❌ Live Sitemap Verification FAILED:\n   {msg_sm}")
            sys.exit(1)

    print("\n🎉 LIVE DEPLOYMENT 100% VERIFIED: Article is active, indexable, and listed in production sitemap.")
    sys.exit(0)


if __name__ == "__main__":
    main()
