#!/usr/bin/env python3
"""
scripts/build_public_site.py - GitHub Pages Public Deployment Artifact Builder.

Strictly enforces an allowlist of public customer-facing assets.
Explicitly isolates and excludes:
- data/ (supplier wholesale inventory, customer orders, hold registers)
- reports/ (internal audit logs, security diagnostics, gap analyses)
- admin.html, admin.js, admin.css (unrouted developer prototype)
- CLI agents and internal tools (*_agent/, hermes_core/, scripts/)
- Test suites (tests/, *_agent/tests/)
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Set, Tuple

PUBLIC_ALLOWLIST_PATTERNS = [
    # Root Customer-Facing HTML Pages
    "index.html",
    "about.html",
    "contact.html",
    "policies.html",
    "correction-policy.html",
    "how-we-price.html",
    "how-we-review.html",
    "how-we-source.html",
    "product-verification.html",
    "404.html",
    "app.js",
    "attribution.js",
    "style.css",
    "manifest.json",
    "favicon.ico",
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
    "llms-full.txt",
]

PUBLIC_ALLOWLIST_DIRS = [
    "assets",
    "tools",
    "guides",
    "blog",
]

STRICT_EXCLUDE_FILES = {
    "admin.html",
    "admin.js",
    "admin.css",
    "admin-light.css",
    "gsc_daily_checklist.html",
}

STRICT_EXCLUDE_PREFIXES = {
    "data",
    "reports",
    "tests",
    "scripts",
    "hermes_core",
    "aio_agent",
    "backlink_agent",
    "bing_agent",
    "competitor_agent",
    "content_agent",
    "conversion_agent",
    "crawler_agent",
    "ga4_agent",
    "gsc_agent",
    "keyword_agent",
    "marketing_agent",
    "merchant_agent",
    "pagespeed_agent",
    "ping_agent",
    "posthog_agent",
    "security_agent",
    "seo-agent",
    ".github",
    ".git",
    "venv",
    ".venv",
}


def build_public_site(project_dir: Path, output_dir: Path, clean: bool = True) -> Tuple[int, List[str]]:
    """Builds the sanitized public customer-facing artifact into output_dir."""
    project_dir = project_dir.resolve()
    output_dir = output_dir.resolve()

    if clean and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    copied_files: List[str] = []

    # 1. Copy allowlisted root files
    for pattern in PUBLIC_ALLOWLIST_PATTERNS:
        src = project_dir / pattern
        if src.is_file():
            dest = output_dir / pattern
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied_files.append(str(dest.relative_to(output_dir)).replace("\\", "/"))

    # Also copy search engine verification files in root (e.g., google*.html, bing_*.xml, IndexNow txt)
    for root_file in project_dir.glob("*"):
        if root_file.is_file():
            name = root_file.name
            if (name.startswith("google") and name.endswith(".html")) or \
               (name.startswith("bing_") and name.endswith(".xml")) or \
               (len(name) == 36 and name.endswith(".txt")):
                dest = output_dir / name
                shutil.copy2(root_file, dest)
                copied_files.append(name)

    # 2. Copy allowlisted directories recursively
    for dir_name in PUBLIC_ALLOWLIST_DIRS:
        src_dir = project_dir / dir_name
        if src_dir.is_dir():
            for root, dirs, files in os.walk(src_dir):
                # Never descend into tests or hidden dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__" and d != "tests"]
                rel_root = Path(root).relative_to(project_dir)

                for file in files:
                    if file.endswith((".py", ".pyc", ".sh", ".jsonl", ".bak")):
                        continue
                    if file.startswith("."):
                        continue

                    src_file = Path(root) / file
                    dest_file = output_dir / rel_root / file
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_file)
                    copied_files.append(str(dest_file.relative_to(output_dir)).replace("\\", "/"))

    # 3. Post-build Verification Guard: ensure zero forbidden files leaked
    violations = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            rel = Path(root, file).relative_to(output_dir).as_posix()
            parts = rel.split("/")
            if parts[0] in STRICT_EXCLUDE_PREFIXES:
                violations.append(f"Forbidden directory staged: {rel}")
            if parts[-1] in STRICT_EXCLUDE_FILES:
                violations.append(f"Forbidden file staged: {rel}")

    if violations:
        raise RuntimeError(f"CRITICAL: Public site build violated security policy:\n" + "\n".join(violations))

    return len(copied_files), copied_files


def main():
    parser = argparse.ArgumentParser(description="Build clean public GitHub Pages deployment artifact.")
    parser.add_argument("--out-dir", default="public-site", help="Destination directory for public artifact.")
    parser.add_argument("--verify-only", action="store_true", help="Simulate build in tempdir and verify rules.")
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent.parent

    if args.verify_only:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            count, files = build_public_site(project_dir, Path(tmp_dir), clean=True)
            print(f"VERIFICATION SUCCESS: {count} public files staged with 0 security policy violations.")
            return

    out_path = project_dir / args.out_dir
    count, files = build_public_site(project_dir, out_path, clean=True)
    print(f"✅ Successfully built public deployment artifact: {count} customer-facing files staged in {out_path.name}/")


if __name__ == "__main__":
    main()
