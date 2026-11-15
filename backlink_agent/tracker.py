"""Tracker CSV Schema Validation, Auditing, and Non-Destructive Update Engine."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import Prospect, VerificationResult
from .verifier import parse_and_verify_html, verify_prospect_url

DEFAULT_CSV_PATH = Path("seo-agent/data/offpage_authority_tracker.csv")
DEFAULT_INDEX_PATH = Path("index.html")
AUDIT_LOG_PATH = Path("seo-agent/data/backlink_verification_log.jsonl")

REQUIRED_COLS = [
    "prospect_domain",
    "prospect_url",
    "site_type",
    "relevance",
    "eligibility",
    "link_terms",
    "action_status",
    "source_page",
    "target_url",
    "anchor_text",
    "link_status",
    "discovered_by_bing",
    "discovered_by_gsc",
    "referral_activity",
    "last_checked",
    "evidence",
]

DISALLOWED_SAMEAS = (
    "saashub.com",
    "futuretools.io",
    "toolpilot.ai",
    "aitooldiscovery.com",
    "altftool.com",
    "hooshware.net",
    "startupnetwork.pk",
    "agentwebmap.com",
)

ALLOWED_LINK_STATUSES = {
    "live",
    "not_live",
    "rejected",
    "investigate",
    "pending",
    "removed",
    "wrong_target",
    "source_noindex",
}

ALLOWED_ACTION_STATUSES = {
    "active",
    "draft_ready",
    "needs_owner_account",
    "submitted_pending_review",
    "backlog_tier2",
    "blocked_tls_error",
    "rejected",
    "on_hold",
    "investigate",
}

ALLOWED_DISCOVERY = {"yes", "no", "pending"}


def load_tracker_rows(path: Path = DEFAULT_CSV_PATH) -> List[Dict[str, str]]:
    """Loads tracker rows from CSV ensuring exact header match."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Tracker CSV not found: {p}")

    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != REQUIRED_COLS:
            raise ValueError(f"Header mismatch in {p}. Expected {REQUIRED_COLS}, got {reader.fieldnames}")
        return list(reader)


def validate_tracker_data(
    path: Path = DEFAULT_CSV_PATH,
    index_path: Path = DEFAULT_INDEX_PATH,
) -> Tuple[List[Dict[str, str]], List[str]]:
    """Validates tracker CSV schema, types, constraints, and index.html sameAs hygiene.

    Returns:
        (rows, errors_list)
    """
    rows = load_tracker_rows(path)
    errors: List[str] = []

    if not rows:
        return rows, ["Tracker has zero rows"]

    seen_prospects: Set[Tuple[str, str, str]] = set()

    for idx, row in enumerate(rows, start=2):
        row_id = f"Row {idx}"
        domain = row.get("prospect_domain", "").strip()
        url = row.get("prospect_url", "").strip()
        site_type = row.get("site_type", "").strip()
        rel_raw = row.get("relevance", "").strip()
        action_status = row.get("action_status", "").strip()
        link_status = row.get("link_status", "").strip()
        source_page = row.get("source_page", "").strip()
        target_url = row.get("target_url", "").strip()
        anchor_text = row.get("anchor_text", "").strip()
        link_terms = row.get("link_terms", "").strip()
        last_checked = row.get("last_checked", "").strip()
        discovered_by_bing = row.get("discovered_by_bing", "").strip()
        discovered_by_gsc = row.get("discovered_by_gsc", "").strip()
        evidence = row.get("evidence", "").strip()

        # Domain & URL checks
        if not domain or not url.startswith("https://"):
            errors.append(f"{row_id}: invalid prospect domain or prospect_url (https required)")

        # Relevance score type-safe check
        try:
            score = int(rel_raw)
            if not (0 <= score <= 100):
                errors.append(f"{row_id}: bad score {score} (must be between 0 and 100)")
        except ValueError:
            errors.append(f"{row_id}: malformed non-integer relevance score '{rel_raw}'")

        # Allowed statuses check
        if action_status and action_status not in ALLOWED_ACTION_STATUSES:
            errors.append(f"{row_id}: unknown action_status '{action_status}'")

        if link_status and link_status not in ALLOWED_LINK_STATUSES:
            errors.append(f"{row_id}: unknown link_status '{link_status}'")

        # Date format check (YYYY-MM-DD)
        if last_checked:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", last_checked):
                errors.append(f"{row_id}: invalid last_checked date format '{last_checked}' (expected YYYY-MM-DD)")

        # Strict rules for "live" links
        if link_status == "live":
            if action_status == "rejected":
                errors.append(f"{row_id}: rejected cannot be live")
            for k in ("source_page", "target_url", "anchor_text", "evidence"):
                if not row.get(k, "").strip():
                    errors.append(f"{row_id}: missing {k}")
            if not source_page.startswith("https://"):
                errors.append(f"{row_id}: https required for source_page")
            if "reciprocal" in link_terms.lower():
                errors.append(f"{row_id}: reciprocal disallowed")

        # Duplicate detection (domain + target + source_page)
        if source_page:
            key = (domain.lower(), target_url.lower(), source_page.lower())
            if key in seen_prospects:
                errors.append(f"{row_id}: duplicate prospect entry ({domain}, {source_page})")
            seen_prospects.add(key)

    # Check index.html sameAs hygiene
    if Path(index_path).exists():
        html = Path(index_path).read_text(encoding="utf-8")
        for m in re.findall(r'"sameAs"\s*:\s*\[(.*?)\]', html, re.S):
            for bad in DISALLOWED_SAMEAS:
                if bad in m:
                    errors.append(f"sameAs must not contain {bad}")

    return rows, errors


def summarize_tracker(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """Generates a summary breakdown of tracker rows."""
    return {
        "total": len(rows),
        "by_action": dict(Counter(x.get("action_status", "") for x in rows)),
        "by_link": dict(Counter(x.get("link_status", "") for x in rows)),
        "bing": dict(Counter(x.get("discovered_by_bing", "") for x in rows)),
        "gsc": dict(Counter(x.get("discovered_by_gsc", "") for x in rows)),
    }


def append_verification_audit_log(results: List[VerificationResult], log_path: Path = AUDIT_LOG_PATH) -> None:
    """Appends verification results to immutable JSONL audit log without erasing past history."""
    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r.to_dict()) + "\n")


def execute_verification(
    rows: List[Dict[str, str]],
    write_back: bool = False,
    csv_path: Path = DEFAULT_CSV_PATH,
    audit_log_path: Path = AUDIT_LOG_PATH,
) -> List[VerificationResult]:
    """Verifies all rows with source_page over HTTPS, returning detailed classifications."""
    results: List[VerificationResult] = []
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for row in rows:
        source_page = row.get("source_page", "").strip()
        target_url = row.get("target_url", "").strip()
        link_status = row.get("link_status", "").strip()

        # Only verify rows that have a source_page or claim to be live
        if not source_page:
            continue

        res = verify_prospect_url(source_page, target_url)
        results.append(res)

        if write_back:
            row["last_checked"] = today_str
            # Append verification classification to evidence without overwriting historical notes
            existing_ev = row.get("evidence", "").strip()
            verif_note = f"[Verified {today_str}: {res.classification}]"
            if verif_note not in existing_ev:
                row["evidence"] = f"{existing_ev}; {verif_note}" if existing_ev else verif_note

            # Update link status according to verified truth
            if res.is_live:
                row["link_status"] = "live"
            elif res.classification in ("removed", "wrong_target", "source_noindex"):
                row["link_status"] = res.classification

    if write_back:
        # Write back updated rows to CSV
        with Path(csv_path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REQUIRED_COLS)
            writer.writeheader()
            writer.writerows(rows)

    append_verification_audit_log(results, audit_log_path)
    return results
