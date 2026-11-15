"""Outbox Queue and Dispatch Manager for Telegram Notifications with Durable Store."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import socket
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request
import uuid

from backlink_agent.telegram_utils import redact_bot_token, split_message_into_chunks
from .models import OutboxMessage
from .outbox_store import LocalSQLiteOutboxStore, OutboxStore

logger = logging.getLogger(__name__)


class TelegramOutboxManager:
    """Durable SQLite-backed outbox queue and dispatcher for Telegram messages."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        store: Optional[OutboxStore] = None,
        db_path: Optional[Path] = None,
        dry_run: bool = False,
    ):
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        self.dry_run = dry_run or os.environ.get("BACKLINK_AGENT_DRY_RUN", "false").lower() == "true"
        self.store = store or LocalSQLiteOutboxStore(db_path=db_path or Path("seo-agent/data/backlink_outbox.db"))
        self.worker_id = f"worker_{uuid.uuid4().hex[:8]}"

    def enqueue(
        self,
        text: str,
        message_type: str = "opportunity_card",
        prospect_domain: Optional[str] = None,
        draft_id: Optional[str] = None,
        draft_hash: Optional[str] = None,
        chat_id: Optional[str] = None,
    ) -> List[OutboxMessage]:
        """Splits long text into <= 3800 char chunks and stores them in durable store."""
        target_chat = chat_id or self.chat_id
        chunks = split_message_into_chunks(text)
        created_messages: List[OutboxMessage] = []

        for chunk in chunks:
            msg = OutboxMessage(
                chat_id=target_chat,
                text=chunk,
                message_type=message_type,
                prospect_domain=prospect_domain,
                draft_id=draft_id,
                draft_hash=draft_hash,
            )
            self.store.enqueue(msg)
            created_messages.append(msg)

        return created_messages

    def list_pending(self, limit: int = 50) -> List[OutboxMessage]:
        """Lists pending or retry-pending messages in the store."""
        pending = self.store.list_by_status("pending", limit=limit)
        retry_pending = self.store.list_by_status("retry_pending", limit=limit)
        return pending + retry_pending

    def dispatch_message(self, msg: OutboxMessage) -> bool:
        """Dispatches an individual OutboxMessage to Telegram or records dry-run simulation."""
        if self.dry_run or not self.bot_token or not msg.chat_id:
            # Explicit dry run simulation: zero external network calls
            msg.mark_dry_run_simulated()
            self.store.update_delivery_status(
                message_id=msg.message_id,
                status="dry_run_simulated",
                expected_lease_token=msg.lease_token,
            )
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
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                if resp.status == 200 and resp_data.get("ok"):
                    remote_msg_id = resp_data.get("result", {}).get("message_id")
                    msg.mark_accepted_by_telegram(remote_msg_id)
                    self.store.update_delivery_status(
                        message_id=msg.message_id,
                        status="accepted_by_telegram",
                        telegram_message_id=remote_msg_id,
                        expected_lease_token=msg.lease_token,
                    )
                    return True
                else:
                    err_msg = f"Telegram API error HTTP {resp.status}: {resp_data}"
                    msg.mark_retry_pending(err_msg)
                    self.store.update_delivery_status(
                        message_id=msg.message_id,
                        status=msg.status,
                        error_message=err_msg,
                        expected_lease_token=msg.lease_token,
                    )
                    return False

        except (socket.timeout, TimeoutError) as e:
            # Network timeout after dispatch: delivery status is UNKNOWN
            err_msg = f"Dispatch timeout (delivery_unknown): {e}"
            msg.mark_delivery_unknown(err_msg)
            self.store.update_delivery_status(
                message_id=msg.message_id,
                status="delivery_unknown",
                error_message=err_msg,
                expected_lease_token=msg.lease_token,
            )
            return False

        except Exception as e:
            sanitized_err = redact_bot_token(str(e), self.bot_token)
            msg.mark_retry_pending(sanitized_err)
            self.store.update_delivery_status(
                message_id=msg.message_id,
                status=msg.status,
                error_message=sanitized_err,
                expected_lease_token=msg.lease_token,
            )
            return False

    def flush_outbox(self, limit: int = 50) -> Dict[str, int]:
        """Atomically claims and dispatches pending messages in the queue."""
        # First recover any stale leases from crashed workers
        self.store.recover_stale_leases(lease_timeout_seconds=300)

        claimed = self.store.claim_pending_messages(
            worker_id=self.worker_id,
            limit=limit,
        )

        results = {
            "processed": len(claimed),
            "dry_run_simulated": 0,
            "accepted_by_telegram": 0,
            "delivery_unknown": 0,
            "retry_pending": 0,
            "failed": 0,
            "sent": 0,  # Combined successful dispatches (dry-run or accepted)
        }

        for msg in claimed:
            success = self.dispatch_message(msg)
            status = msg.status
            if status == "dry_run_simulated":
                results["dry_run_simulated"] += 1
                results["sent"] += 1
            elif status == "accepted_by_telegram":
                results["accepted_by_telegram"] += 1
                results["sent"] += 1
            elif status == "delivery_unknown":
                results["delivery_unknown"] += 1
            elif status == "retry_pending":
                results["retry_pending"] += 1
            elif status == "failed":
                results["failed"] += 1

        return results
