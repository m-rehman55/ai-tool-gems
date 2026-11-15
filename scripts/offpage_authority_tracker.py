#!/usr/bin/env python3
"""Off-Page Authority Tracker & Backlink Verifier CLI for AI Tool Gems.

Maintains backward compatibility with existing tests while integrating the robust
HTML anchor parsing, SSRF-safe URL verification, and type-safe schema validation
from backlink_agent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Ensure repository root is in sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backlink_agent.tracker import (
    DEFAULT_CSV_PATH,
    DEFAULT_INDEX_PATH,
    DISALLOWED_SAMEAS,
    REQUIRED_COLS,
    execute_verification,
    load_tracker_rows,
    summarize_tracker,
    validate_tracker_data,
)
from backlink_agent.verifier import verify_prospect_url

DEFAULT_CSV = DEFAULT_CSV_PATH


def load_rows(path=DEFAULT_CSV):
    return load_tracker_rows(Path(path))


def validate_tracker(path=DEFAULT_CSV, index_path=DEFAULT_INDEX_PATH):
    return validate_tracker_data(Path(path), Path(index_path))


def verify_live(rows):
    """Verifies live links using robust HTML anchor parsing and SSRF protection."""
    res = []
    for row in rows:
        if row.get("link_status") != "live":
            continue
        source_page = row.get("source_page", "").strip()
        target_url = row.get("target_url", "").strip()
        if not source_page:
            continue
        v_res = verify_prospect_url(source_page, target_url)
        # Returns tuple of (source_page, status_code/str, is_live_bool) for backward compatibility
        st = v_res.status_code if v_res.status_code else (v_res.error_message or "ERROR")
        res.append((source_page, st, v_res.is_live))
    return res


def main():
    ap = argparse.ArgumentParser(description="AI Tool Gems Off-Page Authority Tracker")
    ap.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to tracker CSV")
    ap.add_argument("--validate", action="store_true", help="Validate CSV schema and integrity")
    ap.add_argument("--summary", action="store_true", help="Print summary breakdown")
    ap.add_argument("--verify-live", action="store_true", help="Perform network probe of live links")
    ap.add_argument("--write-verification", action="store_true", help="Write verification results back to CSV")
    a = ap.parse_args()

    csv_path = Path(a.csv)
    rows, errs = validate_tracker(csv_path)

    if a.validate:
        if errs:
            print("ERRORS:", errs)
            sys.exit(1)
        print(f"PASS: {len(rows)} rows valid")

    if a.summary:
        print(json.dumps(summarize_tracker(rows), indent=2))

    if a.verify_live:
        print(f"Probing {len(rows)} rows for verified backlinks (strict anchor parsing)...")
        results = execute_verification(rows, write_back=a.write_verification, csv_path=csv_path)
        for r in results:
            print(
                f"{r.source_page} -> classification={r.classification} "
                f"status={r.status_code} target_found={r.target_found} rel={r.rel_tokens}"
            )


if __name__ == "__main__":
    main()
