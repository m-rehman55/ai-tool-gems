#!/usr/bin/env python3
"""
SEO Step 6: Schema Completeness Audit — Saare HTML Pages Check
Har page ke liye:
- JSON-LD schema present?
- @context present?
- FAQPage (tool pages)?
- Product (tool pages)?
- BreadcrumbList?
- og:url sahi?
"""

import json
import os
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")


def audit_page(page_path: Path) -> dict:
    """Audit a single HTML page for schema completeness."""
    html = page_path.read_text(encoding="utf-8", errors="replace")

    result = {
        "page": str(page_path.relative_to(BASE)),
        "issues": [],
        "warnings": [],
        "score": 0,
        "max_score": 0,
    }

    # Check 1: JSON-LD script present
    jsonld_match = re.search(r'<script\s+type=["\']application/ld\+json["\']>', html)
    if not jsonld_match:
        result["issues"].append("No JSON-LD schema found")
    else:
        result["max_score"] += 10
        result["score"] += 10

        # Check 2: Valid JSON inside
        json_content_match = re.search(
            r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>',
            html, re.DOTALL
        )
        if json_content_match:
            content = json_content_match.group(1).strip()
            try:
                data = json.loads(content)
                result["max_score"] += 10
                result["score"] += 10
            except json.JSONDecodeError:
                result["issues"].append("Invalid JSON in schema")
                result["max_score"] += 10

        # Check 3: @context present
        if '"@context"' in html or "'@context'" in html:
            result["max_score"] += 5
            result["score"] += 5
        else:
            result["issues"].append("Missing @context in schema")

    # Check 4: og:url present
    og_url_match = re.search(r'<meta\s+property=["\']og:url["\']\s+content=["\']([^"\']+)', html)
    if og_url_match:
        result["max_score"] += 5
        result["score"] += 5
        url = og_url_match.group(1)
        if page_path.suffix == ".html":
            expected = f"https://aitoolgems.tech{page_path.as_posix()}"
            if url != expected and not url.startswith("https://aitoolgems.tech/jp"):
                result["warnings"].append(f"og:url may be incorrect: {url}")
    else:
        result["warnings"].append("Missing og:url")

    # Check 5: Canonical link present
    canonical_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', html)
    if canonical_match:
        result["max_score"] += 5
        result["score"] += 5
    else:
        result["warnings"].append("Missing canonical link")

    # Check 6: H1 present (only one)
    h1_count = len(re.findall(r'<h1[^>]*>', html))
    if h1_count == 0:
        result["issues"].append("No H1 tag found")
    elif h1_count > 1:
        result["issues"].append(f"Multiple H1 tags: {h1_count}")
    else:
        result["max_score"] += 5
        result["score"] += 5

    # Check 7: Title tag present
    title_match = re.search(r'<title>([^<]+)</title>', html)
    if title_match:
        result["max_score"] += 5
        result["score"] += 5
        title = title_match.group(1)
        if len(title) < 10:
            result["warnings"].append(f"Title too short: {title}")
    else:
        result["issues"].append("No title tag")

    # Check 8: Meta description present
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)', html)
    if desc_match:
        result["max_score"] += 5
        result["score"] += 5
    else:
        result["warnings"].append("Missing meta description")

    # Tool pages specific checks
    if "tools/" in str(page_path) and "/jp/" not in str(page_path):
        # Check for FAQPage on PK tool pages
        if '"@type": "FAQPage"' in html:
            result["max_score"] += 15
            result["score"] += 15
        else:
            result["issues"].append("Missing FAQPage schema")

        # Check for Product schema
        if '"@type": "Product"' in html:
            result["max_score"] += 10
            result["score"] += 10
        else:
            result["warnings"].append("Missing Product schema")

        # Check for BreadcrumbList
        if '"@type": "BreadcrumbList"' in html:
            result["max_score"] += 5
            result["score"] += 5

    if "/jp/tools/" in str(page_path):
        # Check for FAQPage on JP tool pages
        if '"@type": "FAQPage"' in html:
            result["max_score"] += 15
            result["score"] += 15
        else:
            result["issues"].append("Missing FAQPage schema")

        # Check for Product schema
        if '"@type": "Product"' in html:
            result["max_score"] += 10
            result["score"] += 10
        else:
            result["warnings"].append("Missing Product schema")

    # Guide pages specific
    if "/guides/" in str(page_path) and "jp" not in str(page_path):
        if '"@type": "CollectionPage"' in html or '"@type": "WebPage"' in html:
            result["max_score"] += 5
            result["score"] += 5
        # TOC check
        if '<nav class="toc"' in html:
            result["max_score"] += 5
            result["score"] += 5
        else:
            result["warnings"].append("Missing Table of Contents")

    if "jp/guides/" in str(page_path):
        if '"@type": "CollectionPage"' in html or '"@type": "WebPage"' in html:
            result["max_score"] += 5
            result["score"] += 5
        if '<nav class="toc"' in html:
            result["max_score"] += 5
            result["score"] += 5
        else:
            result["warnings"].append("Missing Table of Contents")

    # About pages
    if page_path.name == "about.html":
        if '"@type": "Person"' in html:
            result["max_score"] += 10
            result["score"] += 10
        else:
            result["issues"].append("Missing Person schema")

    if "jp/about.html" == str(page_path):
        if '"@type": "Person"' in html:
            result["max_score"] += 10
            result["score"] += 10
        else:
            result["issues"].append("Missing Person schema")

    return result


def main():
    print("=" * 60)
    print("📊 SEO Step 6: Schema Completeness Audit")
    print("=" * 60)

    all_results = []
    total_score = 0
    total_max = 0
    perfect_pages = 0
    failed_pages = 0

    # Collect all HTML pages
    html_files = []
    for root, dirs, files in os.walk(BASE):
        # Skip build artifacts
        if ".git" in root or "__pycache__" in root or "node_modules" in root:
            continue
        for f in files:
            if f.endswith(".html"):
                html_files.append(Path(root) / f)

    html_files.sort()

    print(f"\nScanning {len(html_files)} HTML pages...\n")

    for page_path in html_files:
        result = audit_page(page_path)
        all_results.append(result)
        total_score += result["score"]
        total_max += result["max_score"]

        if result["score"] == result["max_score"]:
            perfect_pages += 1
        elif result["score"] < result["max_score"] - 5:
            failed_pages += 1

        # Print summary line
        pct = (result["score"] / result["max_score"] * 100) if result["max_score"] > 0 else 0
        status = "✅" if pct == 100 else "⚠️" if pct >= 80 else "❌"
        print(f"{status} {result['page']}: {result['score']}/{result['max_score']} ({pct:.0f}%)")

        if result["issues"]:
            for issue in result["issues"]:
                print(f"   🔴 {issue}")
        if result["warnings"]:
            for warn in result["warnings"]:
                print(f"   🟡 {warn}")

    print("\n" + "=" * 60)
    print(f"📈 Overall Audit Results:")
    print(f"   Pages scanned:   {len(html_files)}")
    print(f"   Perfect pages:   {perfect_pages}")
    print(f"   Needs attention: {failed_pages}")
    print(f"   Total score:     {total_score}/{total_max} ({total_score/total_max*100:.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    main()