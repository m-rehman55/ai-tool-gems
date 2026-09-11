"""Command-line control plane for the AI Tool Gems organic marketing agent."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime

from .config import get_settings
from .content import generate_days
from .db import database_status, initialize
from .learning import learn, recommendations
from .metrics import capture_telegram_subscribers, record_metrics
from .posting import approve_posts, list_posts, publish_due
from .reporting import build_report, report_already_sent, save_report, send_report
from .telegram import TelegramClient


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="python -m marketing_agent", description="AI Tool Gems organic marketing agent")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Create/update the local SQLite database")
    commands.add_parser("status", help="Show database and configuration status")

    generate = commands.add_parser("generate", help="Generate rotating Telegram drafts")
    generate.add_argument("--days", type=int, default=1)
    generate.add_argument("--start", default=date.today().isoformat())
    generate.add_argument("--approve", action="store_true", help="Schedule generated drafts immediately")

    listing = commands.add_parser("list", help="List posts")
    listing.add_argument("--status", choices=["draft", "approved", "scheduled", "published", "failed"])
    listing.add_argument("--limit", type=int, default=30)

    approve = commands.add_parser("approve", help="Approve drafts for publishing")
    approve.add_argument("ids", nargs="*", type=int, help="Post IDs; omit to approve all drafts")

    publish = commands.add_parser("publish-due", help="Publish due Telegram posts")
    publish.add_argument("--dry-run", action="store_true")

    metric = commands.add_parser("record", help="Record real, attributable performance data")
    metric.add_argument("--post", type=int)
    metric.add_argument("--impressions", type=int, default=0)
    metric.add_argument("--clicks", type=int, default=0)
    metric.add_argument("--orders", type=int, default=0)
    metric.add_argument("--revenue", type=int, default=0)
    metric.add_argument("--reactions", type=int, default=0)
    metric.add_argument("--forwards", type=int, default=0)
    metric.add_argument("--source", default="manual")

    commands.add_parser("capture-subscribers", help="Capture Telegram channel member count")
    commands.add_parser("learn", help="Update evidence-based winning-content rules")
    commands.add_parser("recommendations", help="Show current learning rules")

    report = commands.add_parser("report", help="Build or send a daily owner report")
    report.add_argument("--date", default=date.today().isoformat())
    report.add_argument("--send", action="store_true")

    commands.add_parser("test-telegram", help="Verify the configured bot and channel")
    commands.add_parser("test-owner", help="Send a private owner-connection confirmation")
    commands.add_parser("discover-owner", help="Find the latest private chat that started the bot")
    tick = commands.add_parser("tick", help="Idempotent scheduler tick: generate, publish due, report after 21:00")
    tick.add_argument("--dry-run", action="store_true")
    return root


def _print_posts(rows) -> None:
    if not rows:
        print("No matching posts.")
        return
    for row in rows:
        print(f"#{row['id']:03d} {row['status']:<9} {row['scheduled_at']} | {row['product_name']} | {row['segment']} | {row['variant']}")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parser().parse_args(argv)
    settings = get_settings()
    initialize(settings.database_path)

    if args.command == "init":
        print(f"Database ready: {settings.database_path}")
    elif args.command == "status":
        result = database_status(settings.database_path)
        result.update({"telegram_ready": settings.telegram_ready, "owner_reports_ready": settings.owner_reports_ready})
        print(json.dumps(result, indent=2))
    elif args.command == "generate":
        inserted, duplicates = generate_days(settings, date.fromisoformat(args.start), args.days, args.approve)
        print(f"Generated {inserted}; skipped {duplicates} duplicates. Status: {'scheduled' if args.approve else 'draft'}")
    elif args.command == "list":
        _print_posts(list_posts(settings, args.status, args.limit))
    elif args.command == "approve":
        print(f"Approved {approve_posts(settings, args.ids or None)} post(s).")
    elif args.command == "publish-due":
        print(json.dumps(publish_due(settings, dry_run=args.dry_run), indent=2))
    elif args.command == "record":
        row_id = record_metrics(settings, args.post, impressions=args.impressions, clicks=args.clicks,
                                orders=args.orders, revenue=args.revenue, reactions=args.reactions,
                                forwards=args.forwards, source=args.source)
        print(f"Metric row #{row_id} recorded.")
    elif args.command == "capture-subscribers":
        print(f"Telegram subscribers: {capture_telegram_subscribers(settings):,}")
    elif args.command == "learn":
        print(json.dumps(learn(settings), indent=2))
    elif args.command == "recommendations":
        print(json.dumps(recommendations(settings), indent=2))
    elif args.command == "report":
        report_date = date.fromisoformat(args.date)
        body = send_report(settings, report_date) if args.send else build_report(settings, report_date)
        if not args.send:
            save_report(settings, report_date, body)
        print(body)
    elif args.command == "test-telegram":
        if not settings.telegram_ready:
            raise RuntimeError("Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID to .env first")
        bot = TelegramClient(settings.telegram_bot_token).verify()
        count = TelegramClient(settings.telegram_bot_token).member_count(settings.telegram_channel_id)
        print(f"Connected as @{bot.get('username', bot.get('first_name'))}; channel members: {count}")
    elif args.command == "test-owner":
        if not settings.owner_reports_ready:
            raise RuntimeError("Add TELEGRAM_BOT_TOKEN and TELEGRAM_OWNER_CHAT_ID first")
        TelegramClient(settings.telegram_bot_token).send_with_retry(
            settings.telegram_owner_chat_id,
            "✅ AI Tool Gems marketing agent connected successfully.\n\n"
            "Your private owner reports are now configured. No reply is required.",
        )
        print("Owner confirmation delivered.")
    elif args.command == "discover-owner":
        if not settings.telegram_bot_token:
            raise RuntimeError("Add TELEGRAM_BOT_TOKEN first")
        chat = TelegramClient(settings.telegram_bot_token).latest_private_chat()
        if not chat:
            raise RuntimeError("No private chat found. Open the bot in Telegram and press Start, then retry.")
        public_name = chat.get("username") or chat.get("first_name") or "owner"
        print(f"OWNER_CHAT_ID={chat['id']}")
        print(f"OWNER_PUBLIC_NAME={public_name}")
    elif args.command == "tick":
        today = datetime.now(settings.timezone).date()
        inserted, duplicates = generate_days(settings, today, 1, settings.auto_approve)
        result = publish_due(settings, dry_run=args.dry_run)
        print(json.dumps({"generated": inserted, "duplicates": duplicates, "publishing": result}, indent=2))
        if (datetime.now(settings.timezone).hour >= 21 and settings.owner_reports_ready
                and not args.dry_run and not report_already_sent(settings, today)):
            print(send_report(settings, today))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
