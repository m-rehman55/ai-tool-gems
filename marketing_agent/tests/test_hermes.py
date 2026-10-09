from __future__ import annotations

import json
import tempfile
import unittest
from urllib.error import HTTPError
from pathlib import Path
from unittest.mock import patch

from marketing_agent.config import Settings, resolve_timezone
from marketing_agent.hermes import audit, format_report, send_report
from marketing_agent.hermes_audit import audit_repository
from marketing_agent.hermes_connectors import collect_ga4, collect_gsc
from marketing_agent.hermes_models import DataStatus, MetricRecord, Provenance
from marketing_agent.hermes_store import HermesStore
from marketing_agent.telegram import TelegramError


class HermesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "index.html").write_text(
            """<html><head><title>PK Home</title><meta name='description' content='Pakistan home'>
            <link rel='canonical' href='https://example.test/'></head>
            <body><h1>Pakistan Home</h1><img src='x.png' alt='x'></body></html>""",
            encoding="utf-8",
        )
        (self.root / "about.html").write_text(
            """<html><head><title>About</title><meta name='description' content='About Pakistan'>
            <link rel='canonical' href='https://example.test/about.html'></head>
            <body><h1>About Us</h1><img src='x.png' alt='x'></body></html>""",
            encoding="utf-8",
        )
        (self.root / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://example.test/sitemap.xml\n", encoding="utf-8")
        (self.root / "sitemap.xml").write_text("<urlset><url><loc>https://example.test/</loc></url><url><loc>https://example.test/about.html</loc></url></urlset>", encoding="utf-8")
        self.settings = Settings(
            database_path=self.root / "marketing.db",
            site_url="https://example.test",
            whatsapp_number="923236715731",
            timezone=resolve_timezone("Asia/Karachi"),
            telegram_bot_token="",
            telegram_channel_id="",
            telegram_owner_chat_id="",
            buffer_api_key="",
            posts_per_day=3,
            auto_approve=False,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_offline_audit_does_not_open_network(self) -> None:
        with patch("marketing_agent.hermes_audit.urlopen", side_effect=AssertionError("network used")):
            result = audit_repository(self.root, self.settings.site_url)
        self.assertEqual(result.summary["pages"], 2)
        self.assertEqual(result.summary["pk_pages"], 2)
        self.assertIn("https://example.test/", [p["url"] for p in result.pages])

    def test_missing_title_is_reported(self) -> None:
        (self.root / "bad.html").write_text("<html><head><meta name='description' content='test'><link rel='canonical' href='https://example.test/bad.html'></head><body><h1>Bad</h1></body></html>", encoding="utf-8")
        result = audit_repository(self.root, self.settings.site_url)
        codes = {issue["code"] for issue in result.issues}
        self.assertIn("MISSING_TITLE", codes)

    def test_missing_online_credentials_are_explicit(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(collect_gsc(self.settings.site_url).status, DataStatus.ACCESS_REQUIRED)
            self.assertEqual(collect_ga4(self.settings.site_url).status, DataStatus.ACCESS_REQUIRED)

    def test_gsc_connector_preserves_verified_zero(self) -> None:
        payload = {"rows": [{"keys": ["query", "https://example.test/", "pak", "MOBILE"], "clicks": 0, "impressions": 2, "ctr": 0, "position": 8.5}]}
        with patch.dict("os.environ", {"GSC_ACCESS_TOKEN": "test-token"}, clear=True), patch("marketing_agent.hermes_connectors._json_request", return_value=payload):
            result = collect_gsc(self.settings.site_url, days=(7,))
        self.assertEqual(result.status, DataStatus.VERIFIED)
        self.assertEqual(result.records[0].value["clicks"], 0)
        self.assertEqual(result.records[0].provenance.status, DataStatus.VERIFIED)

    def test_connector_errors_are_not_reported_as_no_data(self) -> None:
        failure = HTTPError("https://example.test", 500, "failure", {}, None)
        with patch.dict("os.environ", {"GSC_ACCESS_TOKEN": "test-token"}, clear=True), patch("marketing_agent.hermes_connectors._json_request", side_effect=failure):
            result = collect_gsc(self.settings.site_url, days=(7,))
        self.assertEqual(result.status, DataStatus.ERROR)
        self.assertEqual(result.records, [])

    def test_provenance_preserves_explicit_zero(self) -> None:
        record = MetricRecord("clicks", 0, Provenance("gsc", "property", "2026-10-01T00:00:00+00:00", status=DataStatus.ZERO))
        self.assertEqual(record.to_dict()["provenance"]["status"], "ZERO")
        self.assertEqual(record.to_dict()["value"], 0)

    def test_store_round_trip_and_report(self) -> None:
        result = audit(self.settings, self.root)
        repeated = audit(self.settings, self.root)
        store = HermesStore(self.root / "marketing_agent" / "data" / "hermes.db", self.root / ".seo-cache" / "hermes")
        self.assertIsNotNone(store.latest())
        self.assertEqual(result["run_id"], repeated["run_id"])
        self.assertIn("DATA HEALTH", format_report(result))
        snapshot = Path(result["snapshot"])
        self.assertTrue(snapshot.exists())
        self.assertEqual(json.loads(snapshot.read_text(encoding="utf-8"))["run_id"], result["run_id"])

    def test_telegram_failure_is_reported_without_crashing(self) -> None:
        settings = self.settings.__class__(**{**self.settings.__dict__, "telegram_bot_token": "token", "telegram_owner_chat_id": "owner"})
        with patch("marketing_agent.hermes.TelegramClient.send_with_retry", side_effect=TelegramError("timeout")):
            result = send_report(settings, {"run_id": "test", "mode": "OFFLINE", "audit": {"summary": {}}, "sources": {}})
        self.assertEqual(result["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
