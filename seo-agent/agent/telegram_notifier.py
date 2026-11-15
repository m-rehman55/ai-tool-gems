#!/usr/bin/env python3
"""
Telegram Reporting & Notification Client for AIToolGems
-------------------------------------------------------
Delivers executive daily SEO reports directly to the owner's Telegram chat.
Uses standard library urllib.request with safe Unicode chunking and error handling.
"""

from __future__ import annotations

import json
import os
import re
import socket
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import urllib.error
import urllib.request


@dataclass
class TelegramNotificationResult:
    success: bool
    message_id: Optional[int] = None
    message_ids: List[int] = field(default_factory=list)
    chunks_sent: int = 0
    error: Optional[str] = None
    skipped: bool = False


try:
    from backlink_agent.telegram_utils import split_message_into_chunks, redact_bot_token
except ImportError:
    # Standalone fallback when backlink_agent is not on path
    def split_message_into_chunks(text: str, max_chars: int = 3800) -> List[str]:
        if not text:
            return []
        if len(text) <= max_chars:
            return [text]
        return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]

    def redact_bot_token(text: str, token: str) -> str:
        if token and token in text:
            return text.replace(token, "[REDACTED_BOT_TOKEN]")
        return re.sub(r"bot\d+:[a-zA-Z0-9_-]+", "bot[REDACTED_BOT_TOKEN]", text)


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

    def _redact_secrets(self, text: str) -> str:
        return redact_bot_token(text, self.bot_token or "")

    def send_message(self, text: str) -> TelegramNotificationResult:
        if not self.is_configured():
            return TelegramNotificationResult(
                success=False,
                skipped=True,
                error="Telegram credentials not configured in environment.",
            )

        api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        chunks = split_message_into_chunks(text, max_chars=3800)

        sent_ids: List[int] = []

        for idx, chunk in enumerate(chunks):
            payload = json.dumps({
                "chat_id": self.chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            }).encode("utf-8")

            req = urllib.request.Request(
                api_url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "AIToolGems-GrowthAgent/2.0",
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    if res_data.get("ok"):
                        msg_id = res_data.get("result", {}).get("message_id")
                        if msg_id is not None:
                            sent_ids.append(int(msg_id))
                    else:
                        err_desc = self._redact_secrets(res_data.get("description", "Unknown Telegram error"))
                        return TelegramNotificationResult(
                            success=False,
                            message_id=sent_ids[0] if sent_ids else None,
                            message_ids=sent_ids,
                            chunks_sent=len(sent_ids),
                            error=f"Chunk {idx + 1}/{len(chunks)} rejected: {err_desc}",
                        )
            except urllib.error.HTTPError as e:
                err_text = self._redact_secrets(f"HTTP {e.code}: {e.reason}")
                return TelegramNotificationResult(
                    success=False,
                    message_id=sent_ids[0] if sent_ids else None,
                    message_ids=sent_ids,
                    chunks_sent=len(sent_ids),
                    error=f"Chunk {idx + 1}/{len(chunks)} failed: {err_text}",
                )
            except (socket.timeout, TimeoutError):
                # Avoid blind retries after ambiguous network timeout to prevent duplicate messages
                return TelegramNotificationResult(
                    success=False,
                    message_id=sent_ids[0] if sent_ids else None,
                    message_ids=sent_ids,
                    chunks_sent=len(sent_ids),
                    error=f"Chunk {idx + 1}/{len(chunks)} timed out after {self.timeout}s (retry avoided to prevent duplicate send)",
                )
            except Exception as e:
                err_text = self._redact_secrets(str(e))
                return TelegramNotificationResult(
                    success=False,
                    message_id=sent_ids[0] if sent_ids else None,
                    message_ids=sent_ids,
                    chunks_sent=len(sent_ids),
                    error=f"Chunk {idx + 1}/{len(chunks)} network error: {err_text}",
                )

        return TelegramNotificationResult(
            success=True,
            message_id=sent_ids[0] if sent_ids else None,
            message_ids=sent_ids,
            chunks_sent=len(sent_ids),
        )

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
            "━━━━━━━━━━━━━━━━━━━\n"
            f"• Mode: {mode.upper()}\n"
            f"• Technical SEO Score: {tech_score}/100\n"
            f"• Pages Audited: {pages_audited} (Clean: {clean_pages})\n"
            f"• Technical Issues: {issues_count}\n"
            f"• Scope Guard: {scope_emoji}\n"
            f"• Priority Opportunities: {opportunities_count}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "📊 Google Search Console (28d):\n"
            f"• Live Impressions: {impressions}\n"
            f"• Live Clicks: {clicks}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🛡️ Production Firewall: ACTIVE\n"
            "• Direct push to main: BLOCKED\n"
            "• Price tamper freeze: ENFORCED\n"
            "• Market: Pakistan (PKR / EasyPaisa / JazzCash)\n"
        )

        return self.send_message(message)
