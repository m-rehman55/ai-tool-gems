#!/usr/bin/env python3
"""
Unit tests for TelegramNotifier in seo-agent
--------------------------------------------
"""

import sys
from pathlib import Path
import unittest

AGENT_DIR = Path(__file__).resolve().parent.parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from agent.telegram_notifier import TelegramNotifier

class TestTelegramNotifier(unittest.TestCase):

    def test_unconfigured_skips_gracefully(self):
        # Empty tokens
        notifier = TelegramNotifier(bot_token="", chat_id="")
        self.assertFalse(notifier.is_configured())
        res = notifier.send_message("Test message")
        self.assertFalse(res.success)
        self.assertTrue(res.skipped)
        self.assertIn("not configured", res.error)

    def test_format_and_send_unconfigured_skips(self):
        notifier = TelegramNotifier(bot_token="", chat_id="")
        res = notifier.format_and_send_summary(
            mode="AUDIT",
            tech_score=100,
            pages_audited=57,
            clean_pages=57,
            issues_count=0,
            scope_passed=True,
            opportunities_count=3,
            impressions=25,
            clicks=4,
        )
        self.assertTrue(res.skipped)

if __name__ == "__main__":
    unittest.main()
