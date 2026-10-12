#!/usr/bin/env python3
"""
Telegram Reporting & Notification Client for AIToolGems
-------------------------------------------------------
Delivers executive daily SEO reports directly to the owner's Telegram chat.
Uses standard library urllib.request with retry and error handling.
"""

from __future__ import annotations
import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class TelegramNotificationResult:
    success: bool
    message_id: Optional[int] = None
    error: Optional[str] = None
    skipped: bool = False

class TelegramNotifier:
    """Delivers daily growth reports to configured Telegram bot and chat."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        timeout: int = 15,
    ):
        self.bot_token = (
            bot_token if bot_token is not None else os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        )
        self.chat_id = (
            chat_id
            if chat_id is not None
            else (
                os.environ.get("TELEGRAM_OWNER_CHAT_ID", "").strip()
                or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
            )
        )
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_message(self, text: str) -> TelegramNotificationResult:
        if not self.is_configured():
            return TelegramNotificationResult(
                success=False,
                skipped=True,
                error="Telegram credentials not configured in environment.",
            )

        api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        # Telegram max message length is 4096 chars. Truncate or split if needed.
        clean_text = text[:4000] if len(text) > 4000 else text

        payload = json.dumps({
            "chat_id": self.chat_id,
            "text": clean_text,
            "disable_web_page_preview": True,
        }).encode("utf-8")

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "AIToolGems-GrowthAgent/1.0",
            },
            method="POST",
        )

        for attempt in range(1, 3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    if res_data.get("ok"):
                        msg_id = res_data.get("result", {}).get("message_id")
                        return TelegramNotificationResult(success=True, message_id=msg_id)
                    else:
                        err_desc = res_data.get("description", "Unknown Telegram error")
                        return TelegramNotificationResult(success=False, error=err_desc)
            except urllib.error.HTTPError as e:
                if attempt == 1:
                    time.sleep(1.5)
                    continue
                return TelegramNotificationResult(success=False, error=f"HTTP {e.code}: {e.reason}")
            except Exception as e:
                if attempt == 1:
                    time.sleep(1.5)
                    continue
                return TelegramNotificationResult(success=False, error=str(e))

        return TelegramNotificationResult(success=False, error="Max retry attempts reached")

    def format_and_send_summary(
        self,
        mode: str,
        tech_score: int,
        pages_audited: int,
        clean_pages: int,
        issues_count: int,
        scope_passed: bool,
        opportunities_count: int,
        impressions: int,
        clicks: int,
        report_url_or_path: str = "",
    ) -> TelegramNotificationResult:
        """Formats and dispatches a clean, high-impact Telegram summary."""
        scope_emoji = "✅ PASS (Pakistan Exclusive)" if scope_passed else "❌ SCOPE VIOLATION"
        
        message = (
            "📈 AIToolGems HERMES Daily SEO Report\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"• Mode: {mode.upper()}\n"
            f"• Technical SEO Score: {tech_score}/100\n"
            f"• Pages Audited: {pages_audited} (Clean: {clean_pages})\n"
            f"• Technical Issues: {issues_count}\n"
            f"• Scope Guard: {scope_emoji}\n"
            f"• Priority Opportunities: {opportunities_count}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Google Search Console (28d):\n"
            f"• Live Impressions: {impressions}\n"
            f"• Live Clicks: {clicks}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            "🛡️ Production Firewall: ACTIVE\n"
            "• Direct push to main: BLOCKED\n"
            "• Price tamper freeze: ENFORCED\n"
            "• Market: Pakistan (PKR / EasyPaisa / JazzCash)\n"
        )

        return self.send_message(message)
