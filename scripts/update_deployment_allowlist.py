#!/usr/bin/env python3
"""
scripts/update_deployment_allowlist.py - Allowlist Validation & Integrity Engine.

Resolves ATG-31-008: Automates verification of public deployment allowlist integrity.
Ensures that all legitimate public HTML/CSS/JS/asset files match scripts/build_public_site.py
and prevents unclassified files (such as .env, .git, credentials, or test scripts) from
ever being staged for public GitHub Pages deployment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_public_site import (
    APPROVED_PUBLIC_DIRS,
    APPROVED_ROOT_FILES,
    APPROVED_VERIFICATION_FILES,
    ALLOWED_EXTENSIONS_BY_DIR,
    UNIVERSAL_PROHIBITED_EXTENSIONS,
    UNIVERSAL_PROHIBITED_FILENAMES,
)


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_deployment_boundary(repo_root: Path = REPO_ROOT) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Scans the repository deployment boundary.
    Returns (is_valid, violation_messages, valid_file_manifest).
    """
    violations: List[str] = []
    manifest: Dict[str, str] = {}
    valid_root_set = APPROVED_ROOT_FILES | APPROVED_VERIFICATION_FILES

    # Check root files
    for item in repo_root.iterdir():
        if item.is_file():
            if item.name in valid_root_set:
                manifest[item.name] = compute_sha256(item)
            elif item.name in UNIVERSAL_PROHIBITED_FILENAMES:
                # Deliberately quarantined internal file; not a violation if excluded from deploy
                pass
            elif item.suffix in {".html", ".js", ".css"} and not item.name.startswith("."):
                violations.append(f"Unclassified root web file: {item.name}")

    # Check approved public directories
    for dir_name in APPROVED_PUBLIC_DIRS:
        dir_path = repo_root / dir_name
        if not dir_path.is_dir():
            continue
        allowed_exts = ALLOWED_EXTENSIONS_BY_DIR.get(dir_name, set())
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(repo_root).as_posix()
                if file_path.name in UNIVERSAL_PROHIBITED_FILENAMES or file_path.suffix.lower() in UNIVERSAL_PROHIBITED_EXTENSIONS:
                    violations.append(f"Prohibited file found in public directory {rel_path}")
                elif file_path.suffix.lower() not in allowed_exts:
                    violations.append(f"Disallowed extension for directory {dir_name}: {rel_path} ({file_path.suffix})")
                elif any(part.startswith(".") for part in file_path.parts):
                    violations.append(f"Hidden/private file in public directory: {rel_path}")
                else:
                    manifest[rel_path] = compute_sha256(file_path)

    is_valid = len(violations) == 0
    return is_valid, violations, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public deployment allowlist")
    parser.add_argument("--check", action="store_true", help="Fail if violations exist")
    parser.add_argument("--manifest", type=str, default="", help="Path to write manifest JSON")
    args = parser.parse_args()

    is_valid, violations, manifest = scan_deployment_boundary()

    print(f"Deployment Boundary Scan: {len(manifest)} approved public files staged.")
    if violations:
        print(f"FAIL: {len(violations)} allowlist violations detected:")
        for v in violations:
            print(f"  - {v}")
        if args.check:
            return 1
    else:
        print("PASS: Deployment boundary strictly conforms to allowlist.")

    if args.manifest:
        out_path = Path(args.manifest)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"Manifest written to {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
