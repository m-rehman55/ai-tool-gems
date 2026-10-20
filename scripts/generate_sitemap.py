#!/usr/bin/env python3
"""
AIToolGems Robust XML Sitemap Generator & Validator
--------------------------------------------------
Generates and strictly validates sitemap.xml for aitoolgems.tech:
1. Discovers all indexable public HTML pages.
2. Excludes noindex, administrative, test, cache, and noncanonical files.
3. Extracts canonical URLs and verifies domain/protocol consistency.
4. Uses trustworthy modification dates (article modified_time, git history, or mtime).
5. Employs xml.etree.ElementTree with proper escaping and sitemap namespace.
6. Validates syntax, URL uniqueness, canonical match, and absence of noindex URLs.
"""

import sys
import os
import re
import datetime
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

EXCLUDED_DIRS = {
    ".git", ".github", ".seo-cache", "reports", "scratch",
    "node_modules", "tests", ".gemini", "coverage", "__pycache__"
}

EXCLUDED_FILES = {
    "404.html", "admin.html", "gsc_daily_checklist.html"
}


def get_git_lastmod(file_path: Path) -> str | None:
    """Extract the last commit date (YYYY-MM-DD) for a file using git log."""
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%as", "--", str(file_path)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if res.returncode == 0 and res.stdout.strip():
            date_str = res.stdout.strip()
            # Validate format YYYY-MM-DD
            if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
                return date_str
    except Exception:
        pass
    return None


def get_file_lastmod(file_path: Path, html_content: str) -> str:
    """Determine trustworthy lastmod date using article meta, git, or file mtime."""
    # 1. Check article:modified_time meta tag
    m_mod = re.search(r'<meta[^>]*property=["\']article:modified_time["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.I)
    if m_mod:
        raw_val = m_mod.group(1).strip()
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", raw_val)
        if date_match:
            return date_match.group(1)

    # 2. Check git commit date
    git_date = get_git_lastmod(file_path)
    if git_date:
        return git_date

    # 3. Fallback to filesystem mtime
    try:
        mtime = file_path.stat().st_mtime
        return datetime.date.fromtimestamp(mtime).isoformat()
    except Exception:
        return datetime.date.today().isoformat()


def collect_indexable_pages(base_dir: Path = None) -> list[dict]:
    """Scan base_dir for all canonical, indexable HTML pages with accurate metadata."""
    root = (base_dir or BASE_DIR).resolve()
    pages = []
    seen_canonicals = set()

    for path in sorted(root.rglob("*.html")):
        # Check excluded directories
        rel_parts = path.relative_to(root).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts[:-1]):
            continue

        filename = path.name
        if filename in EXCLUDED_FILES or "googleb36" in filename:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Robots check
        m_robots = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', content, re.I)
        robots = m_robots.group(1).lower() if m_robots else "index, follow"
        if "noindex" in robots:
            continue

        # Canonical check
        m_canon = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content, re.I)
        if not m_canon:
            m_canon = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', content, re.I)

        if not m_canon:
            continue

        canonical_url = m_canon.group(1).strip()

        # Enforce canonical URL standards
        if not canonical_url.startswith("https://aitoolgems.tech/"):
            continue

        if canonical_url in seen_canonicals:
            # Deduplicate by canonical URL
            continue

        seen_canonicals.add(canonical_url)
        lastmod = get_file_lastmod(path, content)

        pages.append({
            "path": path,
            "url": canonical_url,
            "lastmod": lastmod
        })

    return pages


def order_sitemap_urls(pages: list[dict]) -> list[dict]:
    """Sort URLs in logical hierarchy: hubs, trust/policy, guides, tools, remaining."""
    hubs = []
    trust = []
    guides = []
    tools = []
    remaining = []

    trust_suffixes = (
        "about.html", "contact.html", "policies.html", "privacy-policy/",
        "terms-of-service/", "how-we-price.html", "how-we-review.html",
        "how-we-source.html", "product-verification.html", "correction-policy.html"
    )

    for p in pages:
        u = p["url"]
        if u in ("https://aitoolgems.tech/", "https://aitoolgems.tech/deals/", "https://aitoolgems.tech/prices/"):
            hubs.append(p)
        elif any(u.endswith(s) for s in trust_suffixes):
            trust.append(p)
        elif "/guides" in u:
            guides.append(p)
        elif "/tools" in u:
            tools.append(p)
        else:
            remaining.append(p)

    hubs.sort(key=lambda x: x["url"])
    trust.sort(key=lambda x: x["url"])
    guides.sort(key=lambda x: x["url"])
    tools.sort(key=lambda x: x["url"])
    remaining.sort(key=lambda x: x["url"])

    return hubs + trust + guides + tools + remaining


def build_sitemap(base_dir: Path = None, output_file: Path = None) -> tuple[bool, str, int]:
    """Generate valid XML sitemap with ElementTree and validate output."""
    root_dir = (base_dir or BASE_DIR).resolve()
    target = (output_file or (root_dir / "sitemap.xml")).resolve()

    pages = collect_indexable_pages(root_dir)
    if not pages:
        return False, "No indexable pages discovered.", 0

    ordered = order_sitemap_urls(pages)

    ET.register_namespace('', SITEMAP_NS)
    urlset = ET.Element(f'{{{SITEMAP_NS}}}urlset')

    for p in ordered:
        url_el = ET.SubElement(urlset, f'{{{SITEMAP_NS}}}url')
        loc_el = ET.SubElement(url_el, f'{{{SITEMAP_NS}}}loc')
        loc_el.text = p["url"]
        lastmod_el = ET.SubElement(url_el, f'{{{SITEMAP_NS}}}lastmod')
        lastmod_el.text = p["lastmod"]

    if hasattr(ET, "indent"):
        ET.indent(urlset, space="  ")

    raw_xml = ET.tostring(urlset, encoding="utf-8", xml_declaration=True).decode("utf-8")
    if not raw_xml.endswith("\n"):
        raw_xml += "\n"

    target.write_text(raw_xml, encoding="utf-8")

    # Validate generated file
    ok, errors = validate_sitemap_file(target)
    if not ok:
        return False, f"Sitemap validation failed: {'; '.join(errors)}", len(ordered)

    return True, f"Successfully generated valid sitemap with {len(ordered)} canonical URLs.", len(ordered)


def validate_sitemap_file(sitemap_path: Path) -> tuple[bool, list[str]]:
    """Strictly audit sitemap XML for syntax, duplicate URLs, domain format, and noindex exclusions."""
    errors = []
    if not sitemap_path.exists():
        return False, [f"Sitemap file does not exist: {sitemap_path}"]

    try:
        tree = ET.parse(str(sitemap_path))
        root = tree.getroot()
    except Exception as e:
        return False, [f"Malformed XML syntax in sitemap: {e}"]

    locs = []
    for url in root.findall(f'{{{SITEMAP_NS}}}url'):
        loc_el = url.find(f'{{{SITEMAP_NS}}}loc')
        if loc_el is None or not loc_el.text:
            errors.append("Encountered <url> block missing <loc> element")
            continue
        u = loc_el.text.strip()
        locs.append(u)

        if not u.startswith("https://aitoolgems.tech/"):
            errors.append(f"URL outside production canonical domain: {u}")

        lastmod_el = url.find(f'{{{SITEMAP_NS}}}lastmod')
        if lastmod_el is not None and lastmod_el.text:
            lm = lastmod_el.text.strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", lm):
                errors.append(f"Invalid lastmod date format '{lm}' in {u}")

    # Check duplicates
    seen = set()
    for u in locs:
        if u in seen:
            errors.append(f"Duplicate URL in sitemap: {u}")
        seen.add(u)

    # Disallow known noindex pages
    prohibited_noindex_suffixes = [
        "404.html", "admin.html", "gsc_daily_checklist.html"
    ]
    for u in locs:
        if any(u.endswith(p) for p in prohibited_noindex_suffixes):
            errors.append(f"Prohibited noindex page leaked into sitemap: {u}")

    return len(errors) == 0, errors


def main():
    check_only = "--check" in sys.argv
    sitemap_file = BASE_DIR / "sitemap.xml"

    if check_only:
        print(f"🔍 Validating sitemap: {sitemap_file}")
        ok, errors = validate_sitemap_file(sitemap_file)
        if ok:
            print("✅ Sitemap XML and canonical integrity PASSED.")
            sys.exit(0)
        else:
            print(f"❌ Sitemap validation FAILED with {len(errors)} error(s):")
            for err in errors:
                print(f"  • {err}")
            sys.exit(1)

    print("🚀 Generating robust XML sitemap...")
    ok, msg, count = build_sitemap()
    if ok:
        print(f"✅ {msg}")
        sys.exit(0)
    else:
        print(f"❌ Sitemap generation FAILED: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
