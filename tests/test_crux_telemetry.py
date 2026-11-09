"""
tests/test_crux_telemetry.py - Unit Tests for CrUX Telemetry Polling Engine.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from scripts.crux_telemetry import collect_telemetry, query_crux_api, save_snapshot

REPO_ROOT = Path(__file__).resolve().parent.parent


class CruxTelemetryTests(unittest.TestCase):
    """Tests CrUX API integration and offline error handling."""

    @patch("scripts.crux_telemetry.urlopen")
    def test_query_crux_api_success(self, mock_urlopen):
        """Validates successful 200 parsing of field metrics."""
        mock_response = MagicMock()
        sample_payload = {
            "record": {
                "key": {"origin": "https://aitoolgems.tech"},
                "metrics": {
                    "largest_contentful_paint": {
                        "percentiles": {"p75": 1200}
                    }
                }
            }
        }
        mock_response.read.return_value = json.dumps(sample_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = query_crux_api("https://aitoolgems.tech", form_factor="PHONE")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["http_code"], 200)
        self.assertIn("largest_contentful_paint", res["data"]["record"]["metrics"])

    @patch("scripts.crux_telemetry.urlopen")
    def test_query_crux_api_insufficient_data(self, mock_urlopen):
        """Validates that a 404 from CrUX API maps gracefully to INSUFFICIENT_FIELD_DATA."""
        mock_error = HTTPError(
            url="https://chromeuxreport.googleapis.com",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=MagicMock(read=lambda: b'{"error": {"message": "record not found"}}')
        )
        mock_urlopen.side_effect = mock_error

        res = query_crux_api("https://aitoolgems.tech", form_factor="PHONE")
        self.assertEqual(res["status"], "INSUFFICIENT_FIELD_DATA")
        self.assertEqual(res["http_code"], 404)
        self.assertIn("insufficient real-user traffic", res["error"])

    def test_save_snapshot(self):
        """Validates saving snapshot to temporary directory."""
        test_dir = REPO_ROOT / "scratch" / "test_crux"
        record = {
            "timestamp": "2026-11-09T12:00:00Z",
            "origin": "https://aitoolgems.tech",
            "profiles": {}
        }
        out_file = save_snapshot(record, test_dir)
        self.assertTrue(out_file.exists())
        loaded = json.loads(out_file.read_text(encoding="utf-8"))
        self.assertEqual(loaded["origin"], "https://aitoolgems.tech")


if __name__ == "__main__":
    unittest.main()
