#!/usr/bin/env python3
"""
scripts/build_public_site.py - GitHub Pages Fail-Closed Public Deployment Artifact Builder.

Strictly enforces an affirmative, explicit file-level allowlist for public customer-facing assets.
Design Principles:
1. Affirmative File-Level Whitelist: Only explicitly approved files or verified directory assets are staged.
2. Extension Whitelist: Only approved web extensions are permitted.
3. Fail-Closed on Unclassified Files: Unrecognized files in public directories abort the build.
4. Symlink Prohibition: Rejects any symbolic links to prevent directory escape / traversal.
5. Path Traversal Guard: Every destination path is checked for containment inside output_dir.
6. Deterministic Manifest: Generates a JSON manifest containing relative path, size, and SHA-256 hash.
7. Apex Domain CNAME Validation: Guarantees CNAME matches aitoolgems.tech.
8. Zero Leak Policy: Quarantines all private operational data, logs, credentials, and internal reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# 1. Approved Root Public Files (Exact match)
APPROVED_ROOT_FILES = {
    # Public Root HTML Pages
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
    # Public Core JavaScript & Attribution
    "app.js",
    "attribution.js",
    # Core Stylesheets
    "style.css",
    "styles.css",
    "light-theme.css",
    "tool-page.css",
    "guide.css",
    # PWA Manifest and Icons
    "manifest.json",
    "favicon.ico",
    # Search Engine Directives & Sitemaps
    "robots.txt",
    "sitemap.xml",
    "sitemap.txt",
    "sitemap.xsl",
    "llms.txt",
    "llms-full.txt",
    # Apex Domain Mapping
    "CNAME",
}

# 2. Approved Explicit Search Engine Verification Files
APPROVED_VERIFICATION_FILES = {
    "googleb36d12ee905644d9.html",
    "BingSiteAuth.xml",
    "e1a8c47f9d2b4f30a6c8116de5b97042.txt",
    "tiktokH6tjBYp7wfiuUxSHoxcdjeAaS7xub1s6.txt",
}

# 3. Approved Public Directories
APPROVED_PUBLIC_DIRS = {
    "assets",
    "tools",
    "category",
    "guides",
    "blog",
    "prices",
    "deals",
    "privacy-policy",
    "terms-of-service",
}

# 4. Strict Extension Whitelist per Public Directory
APPROVED_PUBLIC_DATASETS = {
    "prices/ai-tools-pricing-pakistan.csv",
    "prices/ai-tools-pricing-pakistan.json",
}

ALLOWED_EXTENSIONS_BY_DIR = {
    "assets": {".webp", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".css", ".mp4", ".woff", ".woff2", ".ttf"},
    "tools": {".html"},
    "category": {".html"},
    "guides": {".html"},
    "blog": {".html"},
    "prices": {".html", ".csv", ".json"},
    "deals": {".html"},
    "privacy-policy": {".html"},
    "terms-of-service": {".html"},
}

# 5. Prohibited File Names and Extensions (Universal Blacklist for Defense-in-Depth)
UNIVERSAL_PROHIBITED_EXTENSIONS = {
    ".env", ".pem", ".key", ".pfx", ".pkcs12", ".crt", ".cer",
    ".csv", ".tsv", ".sqlite", ".sqlite3", ".db",
    ".zip", ".tar", ".gz", ".tgz", ".rar", ".7z",
    ".log", ".trace", ".bak", ".tmp", ".old", ".swp",
    ".py", ".pyc", ".pyd", ".pyo", ".sh", ".bash", ".ps1", ".cmd", ".bat",
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf",
    ".md", ".jsonl",
}

UNIVERSAL_PROHIBITED_FILENAMES = {
    "admin.html",
    "admin.js",
    "admin.css",
    "admin-light.css",
    "gsc_daily_checklist.html",
    "gsc_checklist.txt",
}

FORBIDDEN_DIR_PREFIXES = {
    "data",
    "reports",
    "config",
    "tests",
    "scripts",
    "scratch",
    "hermes_core",
    ".github",
    ".git",
    "venv",
    ".venv",
}


class PublicSiteSecurityError(RuntimeError):
    """Raised when an unclassified, forbidden, or adversarial file is detected."""
    pass


def compute_sha256(file_path: Path) -> str:
    """Computes hexadecimal SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def validate_file_candidate(rel_path: str, src_path: Path) -> None:
    """Validates that a file candidate satisfies all fail-closed security rules."""
    # Check for symbolic links
    if src_path.is_symlink() or os.path.islink(src_path):
        raise PublicSiteSecurityError(f"Symbolic link strictly prohibited in public site build: {rel_path}")

    # Check for hidden files
    parts = Path(rel_path).parts
    for part in parts:
        if part.startswith(".") and part != ".":
            raise PublicSiteSecurityError(f"Hidden file/directory strictly prohibited in public site: {rel_path}")

    # Check against universal prohibited filenames
    filename = src_path.name.lower()
    if filename in UNIVERSAL_PROHIBITED_FILENAMES:
        raise PublicSiteSecurityError(f"Prohibited internal file rejected from public build: {rel_path}")

    # Check against universal prohibited extensions
    ext = src_path.suffix.lower()
    if ext in UNIVERSAL_PROHIBITED_EXTENSIONS and str(rel_path).replace("\\","/") not in APPROVED_PUBLIC_DATASETS:
        raise PublicSiteSecurityError(f"Prohibited file extension '{ext}' rejected from public build: {rel_path}")

    # Check against sensitive keywords in filename
    for marker in ("secret", "password", "credential", "private", "supplier", "export", "token", "backup"):
        if marker in filename and not (filename.startswith("tiktok") or filename.startswith("bing") or filename.startswith("google")):
            raise PublicSiteSecurityError(f"Suspicious sensitive marker '{marker}' in filename: {rel_path}")

    # Directory-specific extension enforcement
    top_dir = parts[0]
    if top_dir in ALLOWED_EXTENSIONS_BY_DIR:
        allowed_exts = ALLOWED_EXTENSIONS_BY_DIR[top_dir]
        if ext not in allowed_exts:
            raise PublicSiteSecurityError(
                f"File '{rel_path}' has extension '{ext}' which is not in the allowed set {allowed_exts} for directory '{top_dir}'"
            )


def build_public_site(project_dir: Path, output_dir: Path, clean: bool = True) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Builds the sanitized public customer-facing artifact into output_dir.
    Returns (file_count, manifest_entries).
    """
    project_dir = project_dir.resolve()
    output_dir = output_dir.resolve()

    if clean and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_entries: List[Dict[str, Any]] = []

    def copy_file_safe(src: Path, rel_target: str) -> None:
        validate_file_candidate(rel_target, src)
        dest = output_dir / rel_target
        dest_resolved = dest.resolve()

        # Path traversal guard
        try:
            dest_resolved.relative_to(output_dir)
        except ValueError:
            raise PublicSiteSecurityError(f"Path traversal attempt detected: {rel_target}")

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

        manifest_entries.append({
            "path": rel_target.replace("\\", "/"),
            "size_bytes": dest.stat().st_size,
            "sha256": compute_sha256(dest),
        })

    # 1. Stage Explicit Root Files
    all_approved_root = APPROVED_ROOT_FILES | APPROVED_VERIFICATION_FILES
    for filename in sorted(all_approved_root):
        src = project_dir / filename
        if src.is_file():
            copy_file_safe(src, filename)

    # 2. Stage Approved Public Directories
    for dir_name in sorted(APPROVED_PUBLIC_DIRS):
        src_dir = project_dir / dir_name
        if not src_dir.is_dir():
            continue

        for root, dirs, files in os.walk(src_dir):
            rel_root = Path(root).relative_to(project_dir)

            # Check directory symlinks
            if os.path.islink(root):
                raise PublicSiteSecurityError(f"Directory symlink detected: {rel_root}")

            # Never descend into hidden dirs, caches, or tests
            for d in list(dirs):
                if d.startswith(".") or d == "__pycache__" or d == "tests":
                    dirs.remove(d)
                elif os.path.islink(Path(root) / d):
                    raise PublicSiteSecurityError(f"Directory symlink detected: {rel_root / d}")

            for file in sorted(files):
                src_file = Path(root) / file
                rel_file = (rel_root / file).as_posix()
                copy_file_safe(src_file, rel_file)

    # 3. Apex Domain CNAME Validation & Enforcement
    cname_file = output_dir / "CNAME"
    if not cname_file.exists():
        cname_file.write_text("aitoolgems.tech\n", encoding="utf-8")
        manifest_entries.append({
            "path": "CNAME",
            "size_bytes": cname_file.stat().st_size,
            "sha256": compute_sha256(cname_file),
        })
    else:
        cname_val = cname_file.read_text(encoding="utf-8").strip()
        if cname_val != "aitoolgems.tech":
            raise PublicSiteSecurityError(f"Invalid CNAME value '{cname_val}'. Must be 'aitoolgems.tech'.")

    # 4. Post-Build Verification Guard: ensure zero forbidden patterns leaked
    violations: List[str] = []
    for root, dirs, files in os.walk(output_dir):
        for d in dirs:
            rel_d = Path(root, d).relative_to(output_dir).as_posix()
            parts = rel_d.split("/")
            if parts[0] in FORBIDDEN_DIR_PREFIXES:
                violations.append(f"Forbidden directory staged: {rel_d}")

        for file in files:
            rel = Path(root, file).relative_to(output_dir).as_posix()
            parts = rel.split("/")
            if parts[0] in FORBIDDEN_DIR_PREFIXES:
                violations.append(f"Forbidden directory staged: {rel}")
            if parts[-1].lower() in UNIVERSAL_PROHIBITED_FILENAMES:
                violations.append(f"Forbidden file staged: {rel}")
            ext = Path(file).suffix.lower()
            if ext in UNIVERSAL_PROHIBITED_EXTENSIONS and rel not in APPROVED_PUBLIC_DATASETS:
                violations.append(f"Forbidden extension staged: {rel}")

    if violations:
        raise PublicSiteSecurityError("CRITICAL: Public site build violated security policy:\n" + "\n".join(violations))

    # 5. Deterministic Manifest Generation
    manifest_entries.sort(key=lambda x: x["path"])
    manifest_path = output_dir / "manifest-public-build.json"
    manifest_data = {
        "build_version": "2.1",
        "domain": "aitoolgems.tech",
        "total_files": len(manifest_entries),
        "files": manifest_entries,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    return len(manifest_entries), manifest_entries


def main():
    parser = argparse.ArgumentParser(description="Build clean public GitHub Pages deployment artifact.")
    parser.add_argument("--out-dir", default="public-site", help="Destination directory for public artifact.")
    parser.add_argument("--verify-only", action="store_true", help="Simulate build in tempdir and verify rules.")
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent.parent

    if args.verify_only:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            count, manifest = build_public_site(project_dir, Path(tmp_dir), clean=True)
            print(f"VERIFICATION SUCCESS: {count} public files staged with 0 security policy violations.")
            return

    out_path = project_dir / args.out_dir
    count, manifest = build_public_site(project_dir, out_path, clean=True)
    print(f"Successfully built public deployment artifact: {count} customer-facing files staged in {out_path.name}/")


if __name__ == "__main__":
    main()
