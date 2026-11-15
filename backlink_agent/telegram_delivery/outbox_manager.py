"""Outbox Queue and Dispatch Manager for Telegram Notifications."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request

from backlink_agent.telegram_utils import redact_bot_token, split_message_into_chunks
from .models import OutboxMessage

logger = logging.getLogger(__name__)

DEFAULT_OUTBOX_DIR = Path("seo-agent/data/outbox")


class TelegramOutboxManager:
    """Durable file-backed outbox queue and dispatcher for Telegram messages."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        outbox_dir: Path = DEFAULT_OUTBOX_DIR,
        dry_run: bool = False,
    ):
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        self.outbox_dir = Path(outbox_dir)
        self.dry_run = dry_run or os.environ.get("BACKLINK_AGENT_DRY_RUN", "false").lower() == "true"

        self.pending_dir = self.outbox_dir / "pending"
        self.sent_dir = self.outbox_dir / "sent"
        self.failed_dir = self.outbox_dir / "failed"

        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.sent_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)

    def enqueue(
        self,
        text: str,
        message_type: str = "opportunity_card",
        prospect_domain: Optional[str] = None,
        draft_hash: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> List[OutboxMessage]:
        """Splits long text into <= 3800 char chunks and stores them in pending outbox."""
        target_chat = chat_id or self.chat_id
        chunks = split_message_into_chunks(text)
        created_messages: List[OutboxMessage] = []

        for chunk in chunks:
            msg = OutboxMessage(
                chat_id=target_chat,
                text=chunk,
                message_type=message_type,
                prospect_domain=prospect_domain,
                draft_hash=draft_hash,
            )
            file_path = self.pending_dir / f"{msg.message_id}.json"
            file_path.write_text(json.dumps(msg.to_dict(), indent=2), encoding="utf-8")
            created_messages.append(msg)

        return created_messages

    def list_pending(self) -> List[OutboxMessage]:
        """Lists all pending messages in outbox queue ordered by creation."""
        messages: List[OutboxMessage] = []
        for file in sorted(self.pending_dir.glob("*.json")):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                messages.append(OutboxMessage.from_dict(data))
            except Exception as e:
                logger.error(f"Failed to read outbox file {file}: {e}")
        return messages

    def dispatch_message(self, msg: OutboxMessage) -> bool:
        """Dispatches an individual OutboxMessage to Telegram."""
        if not self.bot_token or self.dry_run or not msg.chat_id:
            # Dry-run or unconfigured token: mark delivered safely
            msg.mark_delivered()
            self._move_message(msg, self.sent_dir)
            return True

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": msg.chat_id,
            "text": msg.text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    msg.mark_delivered()
                    self._move_message(msg, self.sent_dir)
                    return True
                else:
                    msg.mark_failed(f"HTTP {resp.status}")
        except Exception as e:
            sanitized_err = redact_bot_token(str(e), self.bot_token)
            msg.mark_failed(sanitized_err)

        if msg.status == "failed":
            self._move_message(msg, self.failed_dir)
        else:
            # Update pending with retry count
            p_file = self.pending_dir / f"{msg.message_id}.json"
            p_file.write_text(json.dumps(msg.to_dict(), indent=2), encoding="utf-8")

        return False

    def flush_outbox(self) -> Dict[str, int]:
        """Dispatches all pending messages in the queue."""
        pending = self.list_pending()
        sent = 0
        failed = 0

        for msg in pending:
            success = self.dispatch_message(msg)
            if success:
                sent += 1
            else:
                failed += 1

        return {"processed": len(pending), "sent": sent, "failed": failed}

    def _move_message(self, msg: OutboxMessage, target_dir: Path) -> None:
        source_file = self.pending_dir / f"{msg.message_id}.json"
        target_file = target_dir / f"{msg.message_id}.json"
        target_file.write_text(json.dumps(msg.to_dict(), indent=2), encoding="utf-8")
        if source_file.exists():
            source_file.unlink()
