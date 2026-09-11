"""Daily owner report generation and delivery."""

from __future__ import annotations

from datetime import date

from .config import Settings
from .db import connect, utc_now
from .telegram import TelegramClient


def build_report(settings: Settings, report_date: date) -> str:
    day = report_date.isoformat()
    with connect(settings.database_path) as connection:
        post_counts = {
            row["status"]: row["count"]
            for row in connection.execute(
                "SELECT status, COUNT(*) AS count FROM posts WHERE substr(scheduled_at,1,10)=? GROUP BY status", (day,)
            )
        }
        totals = connection.execute(
            """
            SELECT COALESCE(SUM(m.clicks),0) clicks, COALESCE(SUM(m.orders),0) orders,
              COALESCE(SUM(m.revenue),0) revenue, COALESCE(SUM(m.reactions),0) reactions,
              COALESCE(SUM(m.forwards),0) forwards
            FROM metrics m LEFT JOIN posts p ON p.id=m.post_id
            WHERE substr(m.captured_at,1,10)=?
            """, (day,)
        ).fetchone()
        top = connection.execute(
            """
            SELECT pr.name, COALESCE(SUM(m.orders),0) orders, COALESCE(SUM(m.clicks),0) clicks,
              COALESCE(SUM(m.revenue),0) revenue
            FROM posts p JOIN products pr ON pr.id=p.product_id
            LEFT JOIN metrics m ON m.post_id=p.id
            WHERE substr(p.scheduled_at,1,10)=?
            GROUP BY p.product_id
            HAVING COALESCE(SUM(m.orders),0) > 0 OR COALESCE(SUM(m.clicks),0) > 0
            ORDER BY orders DESC, clicks DESC LIMIT 1
            """, (day,)
        ).fetchone()
        subscriber_rows = connection.execute(
            "SELECT subscriber_count FROM metrics WHERE subscriber_count IS NOT NULL ORDER BY captured_at DESC LIMIT 2"
        ).fetchall()
    subscriber_line = "Not captured"
    if subscriber_rows:
        latest = subscriber_rows[0][0]
        change = latest - subscriber_rows[1][0] if len(subscriber_rows) > 1 else 0
        subscriber_line = f"{latest:,} ({change:+,})"
    top_line = "No performance data yet"
    if top:
        top_line = f"{top['name']} — {top['orders']} orders, {top['clicks']} tracked clicks"
    return (
        f"📊 AI Tool Gems — Daily organic report\n{day}\n\n"
        f"Posts: {post_counts.get('published', 0)} published • {post_counts.get('scheduled', 0)} scheduled "
        f"• {post_counts.get('draft', 0)} drafts • {post_counts.get('failed', 0)} failed\n"
        f"Tracked clicks: {totals['clicks']}\nOrders: {totals['orders']}\n"
        f"Attributed revenue: Rs. {totals['revenue']:,}\n"
        f"Reactions/forwards (manual import): {totals['reactions']}/{totals['forwards']}\n"
        f"Telegram subscribers: {subscriber_line}\n"
        f"Top product: {top_line}\n\n"
        "Note: Bot API delivery and subscriber counts are automatic. Clicks, orders, views and "
        "engagement remain zero until tracked or imported; no figures are estimated."
    )


def save_report(settings: Settings, report_date: date, body: str) -> None:
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO reports(report_date,body,created_at) VALUES(?,?,?)
            ON CONFLICT(report_date) DO UPDATE SET body=excluded.body,created_at=excluded.created_at
            """, (report_date.isoformat(), body, utc_now()),
        )


def send_report(settings: Settings, report_date: date) -> str:
    if not settings.owner_reports_ready:
        raise RuntimeError("Owner reporting needs TELEGRAM_BOT_TOKEN and TELEGRAM_OWNER_CHAT_ID")
    body = build_report(settings, report_date)
    TelegramClient(settings.telegram_bot_token).send_with_retry(settings.telegram_owner_chat_id, body)
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO reports(report_date,body,sent_at,created_at) VALUES(?,?,?,?)
            ON CONFLICT(report_date) DO UPDATE SET body=excluded.body,sent_at=excluded.sent_at
            """, (report_date.isoformat(), body, utc_now(), utc_now()),
        )
    return body


def report_already_sent(settings: Settings, report_date: date) -> bool:
    with connect(settings.database_path) as connection:
        row = connection.execute(
            "SELECT sent_at FROM reports WHERE report_date=?", (report_date.isoformat(),)
        ).fetchone()
        return bool(row and row["sent_at"])
