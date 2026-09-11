"""Small official Telegram Bot API client using the Python standard library."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TelegramError(RuntimeError):
    pass


@dataclass(frozen=True)
class TelegramClient:
    token: str
    timeout: int = 20

    @property
    def base_url(self) -> str:
        if not self.token:
            raise TelegramError("TELEGRAM_BOT_TOKEN is missing")
        return f"https://api.telegram.org/bot{self.token}"

    def call(self, method: str, payload: dict[str, Any] | None = None) -> Any:
        body = json.dumps(payload or {}).encode("utf-8")
        request = Request(
            f"{self.base_url}/{method}", body,
            headers={"Content-Type": "application/json", "User-Agent": "AI-Tool-Gems-Marketing-Agent/1.0"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise TelegramError(f"Telegram HTTP {exc.code}: {detail[:300]}") from exc
        except (URLError, TimeoutError) as exc:
            raise TelegramError(f"Telegram connection failed: {exc}") from exc
        if not data.get("ok"):
            raise TelegramError(data.get("description", "Telegram API returned an error"))
        return data.get("result")

    def verify(self) -> dict[str, Any]:
        return self.call("getMe")

    def member_count(self, chat_id: str) -> int:
        return int(self.call("getChatMemberCount", {"chat_id": chat_id}))

    def updates(self) -> list[dict[str, Any]]:
        result = self.call("getUpdates", {"allowed_updates": ["message"]})
        return list(result or [])

    def latest_private_chat(self) -> dict[str, Any] | None:
        for update in reversed(self.updates()):
            message = update.get("message") or {}
            chat = message.get("chat") or {}
            if chat.get("type") == "private":
                return chat
        return None

    def send_message(self, chat_id: str, text: str, button_url: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": False,
        }
        if button_url:
            payload["reply_markup"] = {
                "inline_keyboard": [[{"text": "View offer & order", "url": button_url}]]
            }
        return self.call("sendMessage", payload)

    def send_with_retry(self, chat_id: str, text: str, button_url: str | None = None) -> dict[str, Any]:
        try:
            return self.send_message(chat_id, text, button_url)
        except TelegramError:
            time.sleep(2)
            return self.send_message(chat_id, text, button_url)
