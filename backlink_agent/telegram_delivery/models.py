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
    draft_hash: Optional[str] = None
    status: str = "pending"  # pending, delivered, failed
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    delivered_at: Optional[str] = None

    def mark_delivered(self) -> None:
        self.status = "delivered"
        self.delivered_at = datetime.now(timezone.utc).isoformat()
        self.error_message = None

    def mark_failed(self, error: str) -> None:
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.status = "failed"
        self.error_message = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "text": self.text,
            "message_type": self.message_type,
            "prospect_domain": self.prospect_domain,
            "draft_hash": self.draft_hash,
            "status": self.status,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message,
            "created_at": self.created_at,
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
            draft_hash=data.get("draft_hash"),
            status=data.get("status", "pending"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            error_message=data.get("error_message"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            delivered_at=data.get("delivered_at"),
        )
        return msg
