"""Data models for Telegram Delivery Outbox and Daily Reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class OutboxMessage:
    """Represents an atomic Telegram notification in the delivery outbox."""

    chat_id: str
    text: str
    message_type: str = "opportunity_card"  # opportunity_card, daily_summary, alert, status
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:10]}")
    prospect_domain: Optional[str] = None
    draft_id: Optional[str] = None
    draft_hash: Optional[str] = None
    status: str = "pending"  # pending, sending, dry_run_simulated, accepted_by_telegram, delivered, delivery_unknown, retry_pending, failed, expired
    retry_count: int = 0
    max_retries: int = 3
    telegram_message_id: Optional[int] = None
    error_message: Optional[str] = None
    locked_by: Optional[str] = None
    locked_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    delivered_at: Optional[str] = None

    def mark_dry_run_simulated(self) -> None:
        """Records dry-run simulation without making external API calls."""
        now_iso = datetime.now(timezone.utc).isoformat()
        self.status = "dry_run_simulated"
        self.delivered_at = now_iso
        self.updated_at = now_iso
        self.error_message = None

    def mark_accepted_by_telegram(self, telegram_msg_id: int) -> None:
        """Records confirmed acceptance by official Telegram Bot API with remote message ID."""
        now_iso = datetime.now(timezone.utc).isoformat()
        self.status = "accepted_by_telegram"
        self.telegram_message_id = telegram_msg_id
        self.delivered_at = now_iso
        self.updated_at = now_iso
        self.error_message = None

    def mark_delivered(self) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        self.status = "delivered"
        self.delivered_at = now_iso
        self.updated_at = now_iso
        self.error_message = None

    def mark_delivery_unknown(self, error: str) -> None:
        """Flagged when network timeout occurs after request submission."""
        now_iso = datetime.now(timezone.utc).isoformat()
        self.status = "delivery_unknown"
        self.error_message = error
        self.updated_at = now_iso

    def mark_retry_pending(self, error: str) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        self.retry_count += 1
        self.updated_at = now_iso
        if self.retry_count >= self.max_retries:
            self.status = "failed"
            self.error_message = f"Max retries exceeded ({self.max_retries}): {error}"
        else:
            self.status = "retry_pending"
            self.error_message = error

    def mark_failed(self, error: str) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        self.status = "failed"
        self.error_message = error
        self.updated_at = now_iso

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "text": self.text,
            "message_type": self.message_type,
            "prospect_domain": self.prospect_domain,
            "draft_id": self.draft_id,
            "draft_hash": self.draft_hash,
            "status": self.status,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "telegram_message_id": self.telegram_message_id,
            "error_message": self.error_message,
            "locked_by": self.locked_by,
            "locked_at": self.locked_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "delivered_at": self.delivered_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OutboxMessage:
        msg = cls(
            chat_id=data["chat_id"],
            text=data["text"],
            message_type=data.get("message_type", "opportunity_card"),
            message_id=data.get("message_id", f"msg_{uuid.uuid4().hex[:10]}"),
            prospect_domain=data.get("prospect_domain"),
            draft_id=data.get("draft_id"),
            draft_hash=data.get("draft_hash"),
            status=data.get("status", "pending"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            telegram_message_id=data.get("telegram_message_id"),
            error_message=data.get("error_message"),
            locked_by=data.get("locked_by"),
            locked_at=data.get("locked_at"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            delivered_at=data.get("delivered_at"),
        )
        return msg
