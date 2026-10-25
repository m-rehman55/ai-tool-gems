"""
Unit tests for Instant Ping & Indexing Autonomous Agent (ping_agent).
"""

import unittest
from unittest.mock import patch, MagicMock
from ping_agent.dispatcher import dispatch_urls, ENDPOINTS, INDEXNOW_KEY, HOST
from ping_agent.verifier import get_sitemap_urls, verify_key_setup
from ping_agent.history import load_history, record_dispatch


class TestPingAgent(unittest.TestCase):

    def test_sitemap_url_extraction(self):
        """Verifies that the sitemap parser extracts valid canonical URLs."""
        urls = get_sitemap_urls()
        self.assertGreater(len(urls), 50)
        for u in urls[:10]:
            self.assertTrue(u.startswith("https://aitoolgems.tech/"))

    def test_local_key_verification(self):
        """Verifies that the local IndexNow verification key is present and correct."""
        status = verify_key_setup(remote_check=False)
        self.assertTrue(status["local_file_exists"])
        self.assertTrue(status["local_content_matches"])
        self.assertEqual(status["key"], "e1a8c47f9d2b4f30a6c8116de5b97042")

    def test_dispatch_dry_run(self):
        """Verifies that dry-run returns valid payload structure without network calls."""
        urls = ["https://aitoolgems.tech/tools/chatgpt/", "https://aitoolgems.tech/tools/claude/"]
        result = dispatch_urls(urls, dry_run=True)
        self.assertEqual(result["status"], "dry_run")
        self.assertEqual(result["urls_count"], 2)
        for ep in ENDPOINTS:
            self.assertIn(ep, result["endpoints"])
            self.assertTrue(result["endpoints"][ep]["success"])

    def test_dispatch_empty_urls(self):
        """Verifies graceful handling of empty URL input."""
        result = dispatch_urls([])
        self.assertEqual(result["status"], "error")

    @patch("urllib.request.urlopen")
    def test_dispatch_live_mocked_success(self, mock_urlopen):
        """Verifies that dispatch_urls correctly interacts with HTTP endpoints."""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        urls = ["https://aitoolgems.tech/tools/allinone/"]
        res = dispatch_urls(urls, dry_run=False)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["submitted_count"], 1)

    def test_history_recording(self):
        """Verifies that dispatch history is logged accurately."""
        urls = ["https://aitoolgems.tech/tools/test-sample/"]
        mock_res = {"status": "success", "endpoints": {"https://api.indexnow.org/indexnow": {"status_code": 200}}}
        record_dispatch(urls, mock_res)

        history = load_history()
        self.assertGreaterEqual(history["total_dispatches"], 1)
        self.assertIn("https://aitoolgems.tech/tools/test-sample/", history["url_history"])


if __name__ == "__main__":
    unittest.main()
