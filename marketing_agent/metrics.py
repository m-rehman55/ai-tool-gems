"""Metrics capture without invented Telegram view data."""

from __future__ import annotations

from .config import Settings
from .db import connect, utc_now
from .telegram import TelegramClient


def record_metrics(
    settings: Settings,
    post_id: int | None,
    *,
    impressions: int = 0,
    clicks: int = 0,
    orders: int = 0,
    revenue: int = 0,
    reactions: int = 0,
    forwards: int = 0,
    subscriber_count: int | None = None,
    source: str = "manual",
) -> int:
    values = (impressions, clicks, orders, revenue, reactions, forwards)
    if any(value < 0 for value in values):
        raise ValueError("Metrics cannot be negative")
    with connect(settings.database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO metrics(post_id,captured_at,impressions,clicks,orders,revenue,reactions,forwards,subscriber_count,source)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (post_id, utc_now(), impressions, clicks, orders, revenue, reactions, forwards,
             subscriber_count, source),
        )
        return int(cursor.lastrowid)


def capture_telegram_subscribers(settings: Settings) -> int:
    if not settings.telegram_ready:
        raise RuntimeError("Telegram is not configured")
    count = TelegramClient(settings.telegram_bot_token).member_count(settings.telegram_channel_id)
    record_metrics(settings, None, subscriber_count=count, source="telegram_bot_api")
    return count
