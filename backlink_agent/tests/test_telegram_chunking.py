"""Unit tests for Telegram Safe Message Chunking, Unicode Preservation, and Error Redaction."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "seo-agent") not in sys.path:
    sys.path.insert(0, str(ROOT / "seo-agent"))

from backlink_agent.telegram_utils import redact_bot_token, split_message_into_chunks
from agent.telegram_notifier import TelegramNotifier, TelegramNotificationResult


class TestTelegramChunking(unittest.TestCase):

    def test_short_message_not_split(self):
        text = "Short SEO update: All 40 pages verified clean."
        chunks = split_message_into_chunks(text, max_chars=3800)
        self.assertEqual(chunks, [text])

    def test_4k_message_split_cleanly(self):
        # Build 4,500 char message with paragraph breaks
        para1 = "Paragraph 1: " + "A" * 2000
        para2 = "Paragraph 2: " + "B" * 2500
        text = f"{para1}\n\n{para2}"
        chunks = split_message_into_chunks(text, max_chars=3800)

        self.assertGreater(len(chunks), 1)
        for idx, chunk in enumerate(chunks):
            self.assertLessEqual(len(chunk), 3800, f"Chunk {idx} exceeds 3800 chars")
        # Ensure full content is preserved across chunks
        combined = "".join(chunks)
        self.assertIn("Paragraph 1:", combined)
        self.assertIn("Paragraph 2:", combined)

    def test_20k_message_split_into_multiple_bounded_chunks(self):
        paragraphs = [f"Report Section {i}: " + ("x" * 900) for i in range(20)]
        text = "\n\n".join(paragraphs)
        chunks = split_message_into_chunks(text, max_chars=3800)

        self.assertGreaterEqual(len(chunks), 5)
        for idx, chunk in enumerate(chunks):
            self.assertLessEqual(len(chunk), 3800, f"Chunk {idx} exceeds 3800 limit")
            self.assertTrue(len(chunk.strip()) > 0)

    def test_unicode_and_emojis_preserved(self):
        # Urdu text + emojis + symbols
        urdu_sample = "پاکستان میں بہترین اور مصدقہ مصنوعی ذہانت کے ٹولز 💎🇵🇰 " * 200
        chunks = split_message_into_chunks(urdu_sample, max_chars=1000)

        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 1000)
            self.assertIn("پاکستان", chunk)
            self.assertIn("💎", chunk)

    def test_redact_bot_token_removes_token(self):
        secret_token = "123456789:ABCdef_GHIjkl-MNOpqr"
        raw_error = f"HTTP 401: Unauthorized request to https://api.telegram.org/bot{secret_token}/sendMessage"
        redacted = redact_bot_token(raw_error, secret_token)

        self.assertNotIn(secret_token, redacted)
        self.assertIn("[REDACTED_TOKEN]", redacted)

    def test_simulated_partial_delivery_failure_on_second_chunk(self):
        notifier = TelegramNotifier(bot_token="fake_token", chat_id="12345")
        long_text = ("Section 1\n\n" + "A" * 3000) + "\n\n" + ("Section 2\n\n" + "B" * 3000)

        # Mock urllib.request.urlopen: First call succeeds (message_id=101), second call raises HTTPError
        mock_resp_1 = MagicMock()
        mock_resp_1.read.return_value = json.dumps({"ok": True, "result": {"message_id": 101}}).encode("utf-8")
        mock_resp_1.__enter__.return_value = mock_resp_1

        import urllib.error
        http_err = urllib.error.HTTPError(
            url="https://api.telegram.org",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=None,
        )

        with patch("urllib.request.urlopen", side_effect=[mock_resp_1, http_err]):
            res = notifier.send_message(long_text)

        self.assertFalse(res.success)
        self.assertEqual(res.chunks_sent, 1)
        self.assertEqual(res.message_ids, [101])
        self.assertEqual(res.message_id, 101)  # Preserved first successful chunk ID
        self.assertIn("Chunk 2", res.error)
        self.assertIn("HTTP 429", res.error)


if __name__ == "__main__":
    unittest.main()
