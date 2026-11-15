"""Unit tests for Tracker Schema Validation and Non-Destructive Storage."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
import unittest

from backlink_agent.tracker import (
    REQUIRED_COLS,
    append_verification_audit_log,
    load_tracker_rows,
    summarize_tracker,
    validate_tracker_data,
)
from backlink_agent.models import VerificationResult


class TestTrackerValidation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "tracker.csv"
        self.index_path = Path(self.temp_dir.name) / "index.html"
        self.index_path.write_text('<html><head><script type="application/ld+json">{"sameAs": ["https://github.com/m-rehman55"]}</script></head></html>')

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_csv(self, rows_data):
        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(REQUIRED_COLS)
            for r in rows_data:
                writer.writerow(r)

    def test_valid_tracker_passes(self):
        self._write_csv([[
            "example.com", "https://example.com/submit", "Directory", "80", "Eligible",
            "Editorial", "active", "https://example.com/item", "https://aitoolgems.tech/",
            "AI Tool Gems", "live", "no", "no", "none", "2026-11-12", "Verified listing"
        ]])
        rows, errs = validate_tracker_data(self.csv_path, self.index_path)
        self.assertEqual(errs, [])
        self.assertEqual(len(rows), 1)

    def test_malformed_non_integer_relevance_does_not_crash(self):
        # Malformed score "eighty" or "abc" should return row-specific error, not uncaught ValueError
        self._write_csv([[
            "example.com", "https://example.com/submit", "Directory", "eighty", "Eligible",
            "Editorial", "active", "https://example.com/item", "https://aitoolgems.tech/",
            "AI Tool Gems", "live", "no", "no", "none", "2026-11-12", "Verified listing"
        ]])
        rows, errs = validate_tracker_data(self.csv_path, self.index_path)
        self.assertTrue(any("malformed non-integer relevance" in e for e in errs))

    def test_out_of_bounds_relevance_score(self):
        self._write_csv([[
            "example.com", "https://example.com/submit", "Directory", "105", "Eligible",
            "Editorial", "active", "https://example.com/item", "https://aitoolgems.tech/",
            "AI Tool Gems", "live", "no", "no", "none", "2026-11-12", "Verified listing"
        ]])
        rows, errs = validate_tracker_data(self.csv_path, self.index_path)
        self.assertTrue(any("bad score 105" in e for e in errs))

    def test_invalid_date_format_flagged(self):
        self._write_csv([[
            "example.com", "https://example.com/submit", "Directory", "85", "Eligible",
            "Editorial", "active", "https://example.com/item", "https://aitoolgems.tech/",
            "AI Tool Gems", "live", "no", "no", "none", "12/11/2026", "Verified listing"
        ]])
        rows, errs = validate_tracker_data(self.csv_path, self.index_path)
        self.assertTrue(any("invalid last_checked date format" in e for e in errs))

    def test_duplicate_prospect_detected(self):
        row = [
            "example.com", "https://example.com/submit", "Directory", "80", "Eligible",
            "Editorial", "active", "https://example.com/item", "https://aitoolgems.tech/",
            "AI Tool Gems", "live", "no", "no", "none", "2026-11-12", "Verified listing"
        ]
        self._write_csv([row, row])
        rows, errs = validate_tracker_data(self.csv_path, self.index_path)
        self.assertTrue(any("duplicate prospect entry" in e for e in errs))

    def test_disallowed_sameas_in_index_flagged(self):
        self.index_path.write_text('<html><head><script type="application/ld+json">{"sameAs": ["https://saashub.com/p/test"]}</script></head></html>')
        self._write_csv([[
            "example.com", "https://example.com/submit", "Directory", "80", "Eligible",
            "Editorial", "active", "https://example.com/item", "https://aitoolgems.tech/",
            "AI Tool Gems", "live", "no", "no", "none", "2026-11-12", "Verified listing"
        ]])
        rows, errs = validate_tracker_data(self.csv_path, self.index_path)
        self.assertTrue(any("sameAs must not contain saashub.com" in e for e in errs))

    def test_append_verification_audit_log_immutable(self):
        log_path = Path(self.temp_dir.name) / "audit.jsonl"
        r1 = VerificationResult(source_page="https://a.com", target_url="https://aitoolgems.tech/", classification="live_follow", target_found=True)
        r2 = VerificationResult(source_page="https://b.com", target_url="https://aitoolgems.tech/", classification="removed", target_found=False)
        append_verification_audit_log([r1], log_path)
        append_verification_audit_log([r2], log_path)

        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 2)
        d1 = json.loads(lines[0])
        d2 = json.loads(lines[1])
        self.assertEqual(d1["classification"], "live_follow")
        self.assertEqual(d2["classification"], "removed")


if __name__ == "__main__":
    unittest.main()
