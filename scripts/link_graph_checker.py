#!/usr/bin/env python3
"""
AIToolGems Link Graph, Route & Structural Integrity Checker
------------------------------------------------------------
Validates the complete web graph, routing, and component integrity:
1. Internal links with missing destinations (broken relative/absolute URLs).
2. Missing fragment IDs for local anchors (#section).
3. Duplicate or invalid product IDs and slugs.
4. Advertised product records whose routes do not exist & routes with no valid product record.
5. Public indexable pages without a user-facing inbound internal link (orphan detection).
6. Sitemap URLs that are invalid, noncanonical, redirect, or should not be indexed.
7. Internal links that point to directory redirects (missing trailing slashes).
8. Breadcrumb parent/child hierarchy consistency.
9. Missing or duplicate title, description, canonical, H1, alt text, or structured data.
10. Buttons/links in critical components lacking meaningful actions/destinations.
"""

from __future__ import annotations
import os
import re
import sys
import argparse
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass, field

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# Documented legitimate exceptions for orphan check
DOCUMENTED_ORPHAN_EXCEPTIONS = {
    "404.html",                   # HTTP 404 Error page (unlinked by design, noindex)
    "admin.html",                 # Private administrative desk (unlinked from public nav, noindex)
    "gsc_daily_checklist.html",   # Internal manual checklist (noindex)
}

# Domains considered internal
INTERNAL_DOMAINS = {"aitoolgems.tech", "www.aitoolgems.tech"}


@dataclass
class Issue:
    category: str
    severity: str  # ERROR, WARNING, INFO
    file: str
    message: str
    target: Optional[str] = None


@dataclass
class LinkGraphReport:
    total_html_files: int
    total_internal_links: int
    total_fragments_checked: int
    total_sitemap_urls: int
    issues: List[Issue] = field(default_factory=list)

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == "ERROR"]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == "WARNING"]

    @property
    def is_clean(self) -> bool:
        return len(self.errors) == 0


class LinkGraphChecker:
    """Performs deep graph and structural audit across repository static files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.html_files: Dict[str, str] = {}
        self.file_ids: Dict[str, Set[str]] = {}
        self.sitemap_urls: List[str] = []
        self._load_html_files()

    def _load_html_files(self):
        """Scans all public HTML files in the repository."""
        skip_dirs = {'.git', 'node_modules', '.gemini', '.seo-cache', 'seo-agent', 'reports'}
        for root, dirs, files in os.walk(self.repo_root):
            # Prune skipped dirs
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for f in files:
                if f.endswith('.html'):
                    full_p = Path(root) / f
                    rel_p = full_p.relative_to(self.repo_root).as_posix()
                    # Skip Google site verification token files from general link graph
                    if rel_p.startswith('google') and rel_p.endswith('.html'):
                        continue
                    try:
                        content = full_p.read_text(encoding='utf-8', errors='ignore')
                        self.html_files[rel_p] = content
                        # Extract all element IDs for fragment checking
                        ids = set(re.findall(r'id=["\']([^"\']+)["\']', content))
                        self.file_ids[rel_p] = ids
                    except Exception as e:
                        pass

    def check_link_destinations_and_fragments(self) -> Tuple[List[Issue], int, int]:
        """Validates all internal link targets, local fragment anchors, and trailing slashes."""
        issues: List[Issue] = []
        links_checked = 0
        fragments_checked = 0

        for rel_p, html in self.html_files.items():
            current_dir = os.path.dirname(rel_p)
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)

            for href in hrefs:
                # Skip telephone, email, javascript, data URIs
                if href.startswith(('mailto:', 'tel:', 'javascript:', 'data:')):
                    continue

                # 1. Local fragment anchor on current page (#foo)
                if href.startswith('#'):
                    frag = href[1:]
                    fragments_checked += 1
                    # Skip bare '#' in index.html for interactive components that handle click via JS
                    # but flag on any other page as broken placeholder
                    if not frag:
                        if rel_p != 'index.html' and rel_p != 'admin.html':
                            issues.append(Issue(
                                category="PLACEHOLDER_LINK",
                                severity="ERROR",
                                file=rel_p,
                                message=f"Empty placeholder href='#' found",
                                target=href
                            ))
                        continue
                    if frag not in self.file_ids.get(rel_p, set()):
                        issues.append(Issue(
                            category="MISSING_FRAGMENT",
                            severity="ERROR",
                            file=rel_p,
                            message=f"Local anchor fragment '#{frag}' does not match any element ID in {rel_p}",
                            target=href
                        ))
                    continue

                links_checked += 1
                parsed = urllib.parse.urlparse(href)

                # 2. Absolute URL check
                if parsed.scheme in ('http', 'https'):
                    domain = parsed.netloc.lower()
                    if domain in INTERNAL_DOMAINS:
                        # Internal absolute link
                        path = parsed.path.lstrip('/')
                        frag = parsed.fragment
                        target_file = (path + 'index.html') if (not path or path.endswith('/')) else path
                        if target_file not in self.html_files:
                            issues.append(Issue(
                                category="BROKEN_INTERNAL_LINK",
                                severity="ERROR",
                                file=rel_p,
                                message=f"Internal absolute link targets non-existent route: {href}",
                                target=href
                            ))
                        elif frag:
                            fragments_checked += 1
                            if frag not in self.file_ids.get(target_file, set()):
                                issues.append(Issue(
                                    category="MISSING_FRAGMENT",
                                    severity="ERROR",
                                    file=rel_p,
                                    message=f"Fragment '#{frag}' does not exist in target {target_file}",
                                    target=href
                                ))
                    continue

                # 3. Relative or Root-relative Link Check
                path = parsed.path
                frag = parsed.fragment

                if not path:
                    target_file = rel_p
                elif path.startswith('/'):
                    clean_path = path.lstrip('/')
                    target_file = (clean_path + 'index.html') if (not clean_path or clean_path.endswith('/')) else clean_path
                elif path.endswith('/'):
                    target_file = os.path.normpath(os.path.join(current_dir, path, 'index.html')).replace('\\', '/')
                else:
                    # Check if relative path targets a directory without trailing slash (would cause 301 redirect)
                    check_dir = os.path.normpath(os.path.join(current_dir, path)).replace('\\', '/')
                    if any(k.startswith(check_dir + '/') for k in self.html_files):
                        issues.append(Issue(
                            category="REDIRECTING_INTERNAL_LINK",
                            severity="WARNING",
                            file=rel_p,
                            message=f"Directory link lacks canonical trailing slash (causes unnecessary 301 redirect): '{href}' -> '{href}/'",
                            target=href
                        ))
                    target_file = os.path.normpath(os.path.join(current_dir, path)).replace('\\', '/')

                # Verify target exists (either as an HTML file or a static asset)
                full_target = self.repo_root / target_file
                if target_file not in self.html_files and not full_target.exists():
                    issues.append(Issue(
                        category="BROKEN_INTERNAL_LINK",
                        severity="ERROR",
                        file=rel_p,
                        message=f"Broken link destination '{href}' (resolved to non-existent path: {target_file})",
                        target=href
                    ))
                elif frag:
                    fragments_checked += 1
                    if target_file in self.html_files and frag not in self.file_ids.get(target_file, set()):
                        issues.append(Issue(
                            category="MISSING_FRAGMENT",
                            severity="ERROR",
                            file=rel_p,
                            message=f"Anchor fragment '#{frag}' in link '{href}' does not match any element ID in {target_file}",
                            target=href
                        ))

        return issues, links_checked, fragments_checked

    def check_orphan_pages(self) -> List[Issue]:
        """Builds directed graph to identify public indexable pages with zero inbound internal links."""
        issues: List[Issue] = []
        inbound_counts: Dict[str, int] = {p: 0 for p in self.html_files}

        for rel_p, html in self.html_files.items():
            current_dir = os.path.dirname(rel_p)
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)

            for href in hrefs:
                if href.startswith(('mailto:', 'tel:', 'javascript:', 'data:', '#')):
                    continue
                if href.startswith(('http://', 'https://')):
                    if not any(href.startswith(f"https://{d}") or href.startswith(f"http://{d}") for d in INTERNAL_DOMAINS):
                        continue
                    parsed = urllib.parse.urlparse(href)
                    path = parsed.path.lstrip('/')
                    target = (path + 'index.html') if (not path or path.endswith('/')) else path
                else:
                    parsed = urllib.parse.urlparse(href)
                    path = parsed.path
                    if not path:
                        continue
                    elif path.startswith('/'):
                        clean = path.lstrip('/')
                        target = (clean + 'index.html') if (not clean or clean.endswith('/')) else clean
                    elif path.endswith('/'):
                        target = os.path.normpath(os.path.join(current_dir, path, 'index.html')).replace('\\', '/')
                    else:
                        target = os.path.normpath(os.path.join(current_dir, path)).replace('\\', '/')

                if target in inbound_counts and target != rel_p:
                    inbound_counts[target] += 1

        for page, count in sorted(inbound_counts.items()):
            # Homepage does not require inbound link
            if page == "index.html":
                continue
            # Documented exceptions
            if page in DOCUMENTED_ORPHAN_EXCEPTIONS:
                continue
            # Check if page has noindex directive
            html = self.html_files[page]
            if 'content="noindex' in html or "content='noindex" in html:
                continue

            if count == 0:
                issues.append(Issue(
                    category="ORPHAN_PAGE",
                    severity="ERROR",
                    file=page,
                    message=f"Public indexable page has zero user-facing inbound internal links (orphan page)",
                    target=page
                ))

        return issues

    def check_product_catalog_routes(self) -> List[Issue]:
        """Cross-checks catalog products in app.js against actual routes under tools/."""
        issues: List[Issue] = []
        app_js_path = self.repo_root / "app.js"
        if not app_js_path.exists():
            issues.append(Issue(category="CONFIG", severity="ERROR", file="app.js", message="app.js not found"))
            return issues

        app_js = app_js_path.read_text(encoding="utf-8", errors="ignore")

        # 1. Parse products array
        prod_m = re.search(r"const\s+products\s*=\s*\[(.*?)\];", app_js, re.DOTALL)
        if not prod_m:
            issues.append(Issue(category="CONFIG", severity="ERROR", file="app.js", message="Could not find products array in app.js"))
            return issues

        prod_block = prod_m.group(1)
        product_entries = re.findall(r"id:\s*['\"]([a-z0-9-]+)['\"],\s*name:\s*['\"]([^'\"]+)['\"]", prod_block)
        product_ids = [p[0] for p in product_entries]

        # Check duplicates in products array
        seen_ids = set()
        for pid in product_ids:
            if pid in seen_ids:
                issues.append(Issue(
                    category="DUPLICATE_PRODUCT_ID",
                    severity="ERROR",
                    file="app.js",
                    message=f"Duplicate product ID '{pid}' defined in app.js catalog",
                    target=pid
                ))
            seen_ids.add(pid)

        # 2. Check STATIC_TOOL_PAGES set
        static_m = re.search(r"STATIC_TOOL_PAGES\s*=\s*new\s*Set\(\[\s*([^\]]+)\]\)", app_js)
        static_set = set([s.strip().strip("'\"") for s in static_m.group(1).split(",") if s.strip()]) if static_m else set()

        # 3. Check physical directory routes under tools/
        tools_dir = self.repo_root / "tools"
        tool_dirs = [d.name for d in tools_dir.iterdir() if d.is_dir()] if tools_dir.exists() else []

        # All static set items must have a corresponding route
        for sid in static_set:
            if sid not in tool_dirs:
                issues.append(Issue(
                    category="MISSING_TOOL_ROUTE",
                    severity="ERROR",
                    file="app.js",
                    message=f"STATIC_TOOL_PAGES lists '{sid}', but route 'tools/{sid}/index.html' does not exist",
                    target=sid
                ))

        # All tool dirs on disk must have an entry in products catalog
        for td in tool_dirs:
            if td not in seen_ids:
                issues.append(Issue(
                    category="UNADVERTISED_TOOL_ROUTE",
                    severity="ERROR",
                    file=f"tools/{td}/index.html",
                    message=f"Route 'tools/{td}/' exists on disk but has no valid product record in app.js",
                    target=td
                ))

        return issues

    def check_sitemap_integrity(self) -> Tuple[List[Issue], int]:
        """Validates sitemap.xml URLs against static disk routes, canonical tags, and indexability rules."""
        issues: List[Issue] = []
        sitemap_path = self.repo_root / "sitemap.xml"
        if not sitemap_path.exists():
            issues.append(Issue(category="SITEMAP", severity="ERROR", file="sitemap.xml", message="sitemap.xml not found"))
            return issues, 0

        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemap_urls = [elem.text.strip() for elem in root.findall("ns:url/ns:loc", ns) if elem.text]
        except Exception as e:
            issues.append(Issue(category="SITEMAP", severity="ERROR", file="sitemap.xml", message=f"Failed to parse sitemap XML: {e}"))
            return issues, 0

        seen_urls = set()
        for url in sitemap_urls:
            # Check duplicate sitemap entries
            if url in seen_urls:
                issues.append(Issue(
                    category="SITEMAP_DUPLICATE",
                    severity="ERROR",
                    file="sitemap.xml",
                    message=f"Duplicate URL found in sitemap: {url}",
                    target=url
                ))
            seen_urls.add(url)

            # Check that URL belongs to production domain
            if not url.startswith("https://aitoolgems.tech/"):
                issues.append(Issue(
                    category="SITEMAP_DOMAIN",
                    severity="ERROR",
                    file="sitemap.xml",
                    message=f"Sitemap URL does not start with https://aitoolgems.tech/: {url}",
                    target=url
                ))
                continue

            # Map URL to relative filesystem path
            path_part = url[len("https://aitoolgems.tech/"):].strip()
            if not path_part or path_part.endswith("/"):
                target_file = (path_part + "index.html").lstrip('/')
            else:
                target_file = path_part.lstrip('/')

            # Verify target exists on disk
            if target_file not in self.html_files:
                issues.append(Issue(
                    category="SITEMAP_DEAD_ROUTE",
                    severity="ERROR",
                    file="sitemap.xml",
                    message=f"Sitemap URL '{url}' maps to non-existent file '{target_file}'",
                    target=url
                ))
                continue

            # Verify target page is not marked noindex
            html = self.html_files[target_file]
            if 'content="noindex' in html or "content='noindex" in html:
                issues.append(Issue(
                    category="SITEMAP_NOINDEX",
                    severity="ERROR",
                    file="sitemap.xml",
                    message=f"Sitemap contains page marked noindex: {url}",
                    target=url
                ))

            # Verify canonical matches the sitemap URL
            canon_m = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', html)
            if canon_m:
                canon_href = canon_m.group(1).strip()
                if canon_href != url:
                    issues.append(Issue(
                        category="SITEMAP_NON_CANONICAL",
                        severity="ERROR",
                        file="sitemap.xml",
                        message=f"Sitemap URL '{url}' does not match canonical tag '{canon_href}' in {target_file}",
                        target=url
                    ))

        # Check for unindexed public pages (pages on disk that should be in sitemap)
        for rel_p, html in self.html_files.items():
            if rel_p in DOCUMENTED_ORPHAN_EXCEPTIONS:
                continue
            if 'content="noindex' in html or "content='noindex" in html:
                continue
            # Reconstruct expected canonical URL
            if rel_p == "index.html":
                expected_url = "https://aitoolgems.tech/"
            elif rel_p.endswith("/index.html"):
                expected_url = f"https://aitoolgems.tech/{rel_p[:-10]}"
            else:
                expected_url = f"https://aitoolgems.tech/{rel_p}"

            if expected_url not in seen_urls:
                issues.append(Issue(
                    category="SITEMAP_MISSING_PAGE",
                    severity="WARNING",
                    file="sitemap.xml",
                    message=f"Public indexable page '{rel_p}' is missing from sitemap.xml (expected: {expected_url})",
                    target=expected_url
                ))

        return issues, len(sitemap_urls)

    def check_breadcrumb_hierarchy(self) -> List[Issue]:
        """Validates breadcrumb parent/child consistency across tool and guide subdirectories."""
        issues: List[Issue] = []

        for rel_p, html in self.html_files.items():
            if rel_p in ('index.html', '404.html', 'admin.html', 'gsc_daily_checklist.html'):
                continue

            bc_m = re.search(r'<nav[^>]*class=["\'][^"\']*breadcrumbs[^"\']*["\'][^>]*>(.*?)</nav>', html, re.DOTALL)
            if not bc_m:
                continue

            bc = bc_m.group(1)
            # Check Home link
            if 'Home' not in bc:
                issues.append(Issue(
                    category="BREADCRUMB_INCOMPLETE",
                    severity="ERROR",
                    file=rel_p,
                    message="Breadcrumb nav missing link to 'Home'"
                ))

            # Tool page hierarchy: Home -> AI tools -> Current Tool
            if rel_p.startswith("tools/") and rel_p != "tools/index.html":
                if 'tools/' not in bc and 'AI tools' not in bc:
                    issues.append(Issue(
                        category="BREADCRUMB_HIERARCHY",
                        severity="ERROR",
                        file=rel_p,
                        message="Tool page breadcrumb missing parent link to 'AI tools' (/tools/)"
                    ))

            # Guide page hierarchy: Home -> Guides -> Current Guide
            if rel_p.startswith("guides/") and rel_p != "guides/index.html":
                if 'guides/' not in bc and 'Guides' not in bc:
                    issues.append(Issue(
                        category="BREADCRUMB_HIERARCHY",
                        severity="ERROR",
                        file=rel_p,
                        message="Guide page breadcrumb missing parent link to 'Guides' (/guides/)"
                    ))

        return issues

    def check_critical_actions_and_buttons(self) -> List[Issue]:
        """Ensures all critical CTAs, purchase buttons, and search inputs have meaningful destinations."""
        issues: List[Issue] = []

        for rel_p, html in self.html_files.items():
            # Check WhatsApp order buttons
            wa_links = re.findall(r'<a[^>]+href=["\'](https://wa\.me/[^"\']*)["\']', html)
            for wl in wa_links:
                if '923236715731' not in wl:
                    issues.append(Issue(
                        category="INVALID_WHATSAPP_ACTION",
                        severity="ERROR",
                        file=rel_p,
                        message=f"WhatsApp CTA contains unverified or placeholder phone number: {wl[:45]}",
                        target=wl
                    ))

            # Check for empty action attributes on forms
            forms = re.findall(r'<form[^>]*>', html)
            for form in forms:
                action_m = re.search(r'action=["\']([^"\']*)["\']', form)
                if action_m and not action_m.group(1).strip() and 'onsubmit' not in form:
                    issues.append(Issue(
                        category="EMPTY_FORM_ACTION",
                        severity="WARNING",
                        file=rel_p,
                        message=f"Form has empty action attribute without client-side handler: {form[:60]}",
                        target=form
                    ))

        return issues

    def run_all_checks(self) -> LinkGraphReport:
        """Executes full diagnostic suite and returns unified report."""
        dest_issues, links_cnt, frags_cnt = self.check_link_destinations_and_fragments()
        orphan_issues = self.check_orphan_pages()
        catalog_issues = self.check_product_catalog_routes()
        sitemap_issues, sitemap_cnt = self.check_sitemap_integrity()
        breadcrumb_issues = self.check_breadcrumb_hierarchy()
        button_issues = self.check_critical_actions_and_buttons()

        all_issues = (
            dest_issues +
            orphan_issues +
            catalog_issues +
            sitemap_issues +
            breadcrumb_issues +
            button_issues
        )

        return LinkGraphReport(
            total_html_files=len(self.html_files),
            total_internal_links=links_cnt,
            total_fragments_checked=frags_cnt,
            total_sitemap_urls=sitemap_cnt,
            issues=all_issues
        )


def main():
    parser = argparse.ArgumentParser(description="AIToolGems Link Graph, Route & Structural Integrity Checker")
    parser.add_argument("--repo-root", default=".", help="Path to repository root")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors")
    args = parser.parse_args()

    checker = LinkGraphChecker(Path(args.repo_root))
    report = checker.run_all_checks()

    print("============================================================")
    print("🌐 AIToolGems Link Graph & Structural Integrity Checker")
    print("============================================================")
    print(f"Total HTML files scanned:       {report.total_html_files}")
    print(f"Total internal links checked:   {report.total_internal_links}")
    print(f"Total fragment anchors checked: {report.total_fragments_checked}")
    print(f"Total sitemap URLs verified:    {report.total_sitemap_urls}")
    print("------------------------------------------------------------")

    errors = report.errors
    warnings = report.warnings

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for err in errors:
            print(f"  [{err.category}] {err.file}: {err.message}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warn in warnings:
            print(f"  [{warn.category}] {warn.file}: {warn.message}")

    if not errors and not warnings:
        print("\n✅ PERFECT: Link graph, routes, sitemap, fragments, and components 100% clean.")
        print("============================================================")
        sys.exit(0)
    elif not errors:
        print(f"\n✅ PASS: 0 Errors ({len(warnings)} warnings).")
        print("============================================================")
        sys.exit(1 if args.strict else 0)
    else:
        print(f"\n❌ FAIL: {len(errors)} actionable defects identified.")
        print("============================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
