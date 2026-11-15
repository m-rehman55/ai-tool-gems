"""Durable Outbox Store Abstraction and Local SQLite Implementation for WP14."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
import json
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional
import uuid

from .models import OutboxMessage

logger = logging.getLogger(__name__)

DEFAULT_SQLITE_PATH = Path("seo-agent/data/backlink_outbox.db")


class OutboxStore(ABC):
    """Abstract interface for durable outbox persistence."""

    @abstractmethod
    def enqueue(self, message: OutboxMessage) -> None:
        """Persists a new pending message in the store."""
        pass

    @abstractmethod
    def get(self, message_id: str) -> Optional[OutboxMessage]:
        """Retrieves a message by ID."""
        pass

    @abstractmethod
    def list_by_status(self, status: str, limit: int = 50) -> List[OutboxMessage]:
        """Lists messages by status."""
        pass

    @abstractmethod
    def claim_pending_messages(
        self, worker_id: str, limit: int = 10, lease_timeout_seconds: int = 300
    ) -> List[OutboxMessage]:
        """Atomically claims pending or stale sending messages for dispatch."""
        pass

    @abstractmethod
    def update_delivery_status(
        self,
        message_id: str,
        status: str,
        error_message: Optional[str] = None,
        telegram_message_id: Optional[int] = None,
        expected_lease_token: Optional[str] = None,
    ) -> bool:
        """Updates the status and metadata of a message, fencing out stale worker leases."""
        pass

    @abstractmethod
    def recover_stale_leases(self, lease_timeout_seconds: int = 300) -> int:
        """Recovers messages stuck in 'sending' state beyond lease timeout."""
        pass

    @abstractmethod
    def get_status_counts(self) -> Dict[str, int]:
        """Returns aggregate message count breakdown across all statuses."""
        pass


class LocalSQLiteOutboxStore(OutboxStore):
    """Durable, crash-resilient SQLite outbox store with WAL mode and atomic lease locking."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS outbox_messages (
        message_id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        text TEXT NOT NULL,
        message_type TEXT NOT NULL,
        prospect_domain TEXT,
        draft_id TEXT,
        draft_hash TEXT,
        status TEXT NOT NULL,
        retry_count INTEGER NOT NULL DEFAULT 0,
        max_retries INTEGER NOT NULL DEFAULT 3,
        telegram_message_id INTEGER,
        error_message TEXT,
        locked_by TEXT,
        locked_at TEXT,
        lease_token TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        delivered_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_outbox_status ON outbox_messages(status);
    CREATE INDEX IF NOT EXISTS idx_outbox_draft_hash ON outbox_messages(draft_hash);
    CREATE INDEX IF NOT EXISTS idx_outbox_lease_token ON outbox_messages(lease_token);
    CREATE INDEX IF NOT EXISTS idx_outbox_created_at ON outbox_messages(created_at);
    """

    def __init__(self, db_path: Path = DEFAULT_SQLITE_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript(self.SCHEMA)
            # Schema migration safety if table already existed without lease_token
            try:
                conn.execute("ALTER TABLE outbox_messages ADD COLUMN lease_token TEXT")
            except sqlite3.OperationalError:
                pass  # Already present

    def checkpoint_wal(self) -> Dict[str, Any]:
        """Checkpoints SQLite WAL journal into main DB file to ensure zero uncommitted artifacts."""
        with self._get_connection() as conn:
            cursor = conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            res = cursor.fetchone()
            return {"busy": res[0], "log": res[1], "checkpointed": res[2]}

    def enqueue(self, message: OutboxMessage) -> None:
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO outbox_messages (
                    message_id, chat_id, text, message_type, prospect_domain,
                    draft_id, draft_hash, status, retry_count, max_retries,
                    telegram_message_id, error_message, locked_by, locked_at,
                    lease_token, created_at, updated_at, delivered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?)
                """,
                (
                    message.message_id,
                    message.chat_id,
                    message.text,
                    message.message_type,
                    message.prospect_domain,
                    getattr(message, "draft_id", None),
                    message.draft_hash,
                    message.status,
                    message.retry_count,
                    message.max_retries,
                    getattr(message, "telegram_message_id", None),
                    message.error_message,
                    getattr(message, "lease_token", None),
                    message.created_at,
                    now_str,
                    message.delivered_at,
                ),
            )

    def get(self, message_id: str) -> Optional[OutboxMessage]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM outbox_messages WHERE message_id = ?", (message_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_message(row)

    def list_by_status(self, status: str, limit: int = 50) -> List[OutboxMessage]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM outbox_messages
                WHERE status = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (status, limit),
            )
            return [self._row_to_message(r) for r in cursor.fetchall()]

    def claim_pending_messages(
        self, worker_id: str, limit: int = 10, lease_timeout_seconds: int = 300
    ) -> List[OutboxMessage]:
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        stale_threshold = (now - timedelta(seconds=lease_timeout_seconds)).isoformat()

        claimed_messages: List[OutboxMessage] = []
        with self._get_connection() as conn:
            cursor = conn.execute("BEGIN IMMEDIATE")
            # Select pending or expired-lease messages
            query = """
                SELECT * FROM outbox_messages
                WHERE status = 'pending'
                   OR status = 'retry_pending'
                   OR (status = 'sending' AND (locked_at IS NULL OR locked_at < ?))
                ORDER BY created_at ASC
                LIMIT ?
            """
            rows = conn.execute(query, (stale_threshold, limit)).fetchall()
            if not rows:
                return []

            for r in rows:
                m_id = r["message_id"]
                lease_tok = f"tok_{uuid.uuid4().hex[:12]}"
                conn.execute(
                    """
                    UPDATE outbox_messages
                    SET status = 'sending',
                        locked_by = ?,
                        locked_at = ?,
                        lease_token = ?,
                        updated_at = ?
                    WHERE message_id = ?
                    """,
                    (worker_id, now_iso, lease_tok, now_iso, m_id),
                )
                msg = self._row_to_message(r)
                msg.status = "sending"
                msg.locked_by = worker_id
                msg.locked_at = now_iso
                msg.lease_token = lease_tok
                claimed_messages.append(msg)

        return claimed_messages

    def update_delivery_status(
        self,
        message_id: str,
        status: str,
        error_message: Optional[str] = None,
        telegram_message_id: Optional[int] = None,
        expected_lease_token: Optional[str] = None,
    ) -> bool:
        now_iso = datetime.now(timezone.utc).isoformat()
        delivered_at = (
            now_iso
            if status in ("accepted_by_telegram", "delivered", "dry_run_simulated")
            else None
        )

        with self._get_connection() as conn:
            if expected_lease_token:
                cursor = conn.execute(
                    """
                    UPDATE outbox_messages
                    SET status = ?,
                        error_message = ?,
                        telegram_message_id = COALESCE(?, telegram_message_id),
                        delivered_at = COALESCE(?, delivered_at),
                        updated_at = ?,
                        locked_by = NULL,
                        locked_at = NULL,
                        lease_token = NULL
                    WHERE message_id = ? AND (lease_token IS NULL OR lease_token = ?)
                    """,
                    (status, error_message, telegram_message_id, delivered_at, now_iso, message_id, expected_lease_token),
                )
            else:
                cursor = conn.execute(
                    """
                    UPDATE outbox_messages
                    SET status = ?,
                        error_message = ?,
                        telegram_message_id = COALESCE(?, telegram_message_id),
                        delivered_at = COALESCE(?, delivered_at),
                        updated_at = ?,
                        locked_by = NULL,
                        locked_at = NULL,
                        lease_token = NULL
                    WHERE message_id = ?
                    """,
                    (status, error_message, telegram_message_id, delivered_at, now_iso, message_id),
                )
            return cursor.rowcount > 0

    def recover_stale_leases(self, lease_timeout_seconds: int = 300) -> int:
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        stale_threshold = (now - timedelta(seconds=lease_timeout_seconds)).isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE outbox_messages
                SET status = 'retry_pending',
                    retry_count = retry_count + 1,
                    error_message = 'Recovered from crashed/stale worker lease',
                    locked_by = NULL,
                    locked_at = NULL,
                    lease_token = NULL,
                    updated_at = ?
                WHERE status = 'sending' AND (locked_at IS NULL OR locked_at < ?)
                """,
                (now_iso, stale_threshold),
            )
            return cursor.rowcount

    def get_status_counts(self) -> Dict[str, int]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT status, COUNT(*) as count FROM outbox_messages GROUP BY status"
            )
            counts = {
                "pending": 0,
                "sending": 0,
                "dry_run_simulated": 0,
                "accepted_by_telegram": 0,
                "delivered": 0,
                "delivery_unknown": 0,
                "retry_pending": 0,
                "failed": 0,
                "expired": 0,
            }
            for row in cursor.fetchall():
                counts[row["status"]] = row["count"]
            return counts

    def _row_to_message(self, row: sqlite3.Row) -> OutboxMessage:
        msg = OutboxMessage(
            chat_id=row["chat_id"],
            text=row["text"],
            message_type=row["message_type"],
            message_id=row["message_id"],
            prospect_domain=row["prospect_domain"],
            draft_hash=row["draft_hash"],
            status=row["status"],
            retry_count=row["retry_count"],
            max_retries=row["max_retries"],
            error_message=row["error_message"],
            created_at=row["created_at"],
            delivered_at=row["delivered_at"],
        )
        if "telegram_message_id" in row.keys():
            msg.telegram_message_id = row["telegram_message_id"]
        if "draft_id" in row.keys():
            msg.draft_id = row["draft_id"]
        if "lease_token" in row.keys():
            msg.lease_token = row["lease_token"]
        return msg


class D1OutboxStoreSpec:
    """Architectural specification for future Cloudflare D1 unified outbox store.

    DO NOT instantiate or connect to WP12 Staging D1 during 48-hour burn-in observation.
    """

    TABLE_NAME = "outbox_messages"
    MIGRATION_VERSION = "0002_outbox_queue.sql"
