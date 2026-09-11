"""Approval and Telegram publishing workflow."""

from __future__ import annotations

from datetime import datetime, timezone

from .config import Settings
from .db import connect, utc_now
from .telegram import TelegramClient, TelegramError


def list_posts(settings: Settings, status: str | None = None, limit: int = 30):
    query = "SELECT p.*, pr.name AS product_name FROM posts p JOIN products pr ON pr.id=p.product_id"
    params: list[object] = []
    if status:
        query += " WHERE p.status=?"
        params.append(status)
    query += " ORDER BY p.scheduled_at LIMIT ?"
    params.append(limit)
    with connect(settings.database_path) as connection:
        return connection.execute(query, params).fetchall()


def approve_posts(settings: Settings, post_ids: list[int] | None = None) -> int:
    with connect(settings.database_path) as connection:
        if post_ids:
            placeholders = ",".join("?" for _ in post_ids)
            cursor = connection.execute(
                f"UPDATE posts SET status='scheduled', error=NULL WHERE status IN ('draft','approved') AND id IN ({placeholders})",
                post_ids,
            )
        else:
            cursor = connection.execute("UPDATE posts SET status='scheduled', error=NULL WHERE status IN ('draft','approved')")
        return cursor.rowcount


def publish_due(settings: Settings, *, dry_run: bool = False, now: datetime | None = None) -> dict[str, int]:
    current = now or datetime.now(settings.timezone)
    stats = {"due": 0, "published": 0, "failed": 0, "dry_run": 0}
    with connect(settings.database_path) as connection:
        rows = connection.execute(
            "SELECT * FROM posts WHERE status='scheduled' AND scheduled_at<=? ORDER BY scheduled_at",
            (current.isoformat(timespec="seconds"),),
        ).fetchall()
    stats["due"] = len(rows)
    if not rows:
        return stats
    if dry_run:
        stats["dry_run"] = len(rows)
        return stats
    if not settings.telegram_ready:
        raise RuntimeError("Telegram is not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID to .env")
    client = TelegramClient(settings.telegram_bot_token)
    for row in rows:
        try:
            response = client.send_with_retry(settings.telegram_channel_id, row["caption"], row["target_url"])
            with connect(settings.database_path) as connection:
                connection.execute(
                    "UPDATE posts SET status='published', published_at=?, platform_message_id=?, error=NULL WHERE id=?",
                    (utc_now(), str(response["message_id"]), row["id"]),
                )
            stats["published"] += 1
        except (TelegramError, KeyError) as exc:
            with connect(settings.database_path) as connection:
                connection.execute("UPDATE posts SET status='failed', error=? WHERE id=?", (str(exc)[:500], row["id"]))
            stats["failed"] += 1
    return stats
