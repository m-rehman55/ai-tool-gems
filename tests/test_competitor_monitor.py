"""
Unit tests for scripts/competitor_monitor.py
Verifies probe logic, offline mocking, snapshot output format, and uptime calculation.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.competitor_monitor import (
    DEFAULT_COMPETITORS,
    probe_competitor,
    run_competitor_monitoring,
)


class TestCompetitorMonitor(unittest.TestCase):
    def test_default_competitors_registry_count(self) -> None:
        """Ensures at least 14 competitors are registered in the default universe."""
        self.assertGreaterEqual(len(DEFAULT_COMPETITORS), 14)
        ids = [c["id"] for c in DEFAULT_COMPETITORS]
        self.assertIn("COMP-01", ids)
        self.assertIn("COMP-02", ids)
        self.assertIn("COMP-08", ids)

    def test_probe_competitor_offline_mock(self) -> None:
        """Verifies that offline mock probe returns expected structure without network access."""
        comp = {"id": "TEST-01", "name": "Mock Test Competitor", "url": "https://mock.local/"}
        res = probe_competitor(comp, timeout_seconds=1, offline=True)
        self.assertEqual(res["id"], "TEST-01")
        self.assertEqual(res["status"], 200)
        self.assertTrue(res.get("offline_mock"))
        self.assertIn("EasyPaisa", res["payment_rails"])
        self.assertIsNone(res["error"])

    def test_run_competitor_monitoring_summary_calculation(self) -> None:
        """Verifies aggregate uptime percentage and structure in offline execution."""
        sample = [
            {"id": "COMP-A", "name": "Comp A", "url": "https://a.local/"},
            {"id": "COMP-B", "name": "Comp B", "url": "https://b.local/"},
        ]
        summary = run_competitor_monitoring(
            competitors=sample, timeout_seconds=1, offline=True, save_snapshot=False
        )
        self.assertEqual(summary["total_monitored"], 2)
        self.assertEqual(summary["total_online"], 2)
        self.assertEqual(summary["uptime_percentage"], 100.0)
        self.assertEqual(len(summary["results"]), 2)


if __name__ == "__main__":
    unittest.main()

