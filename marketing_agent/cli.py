"""Command-line control plane for the AI Tool Gems organic marketing agent."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

from .commands import process_updates, setup_bot
from .buffer import (
    campaign_preflight,
    connection_status as buffer_connection_status,
    delivery_audit,
    format_publish_confirmation,
    publish_daily_deal,
    repair_future_posts,
    refresh_performance,
    render_daily_media,
    render_platform_media,
)
from .config import get_settings
from .content import generate_days
from .db import database_status, initialize
from .learning import learn, recommendations
from .metrics import capture_telegram_subscribers, record_metrics
from .posting import approve_posts, list_posts, publish_due
from .reporting import build_report, report_already_sent, save_report, send_report
from .seo_monitor import format_report as format_seo_report, run_monitor
from .social import daily_pack, send_automation_failure_alert, send_daily_pack
from .telegram import TelegramClient
from .trial import claim_slot, publish_payload, send_trial_report, trial_plan


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
    commands.add_parser("setup-bot", help="Install the Telegram bot command menu and descriptions")
    commands.add_parser("process-commands", help="Reply to new private Telegram bot commands")

    social = commands.add_parser("social-pack", help="Build or privately send the daily organic social pack")
    social.add_argument("--date", default=date.today().isoformat())
    social.add_argument("--send", action="store_true")
    commands.add_parser("social-alert", help="Send the owner a generic hosted-campaign failure alert")

    commands.add_parser("buffer-status", help="Verify Buffer access and list the three owned social channels")
    buffer_prepare = commands.add_parser("buffer-prepare", help="Create today's branded social image and scheduled video")
    buffer_prepare.add_argument("--date", default=date.today().isoformat())
    buffer_prepare_platform = commands.add_parser("buffer-prepare-platform", help="Render one platform/slot asset for a targeted repair")
    buffer_prepare_platform.add_argument("--date", default=date.today().isoformat())
    buffer_prepare_platform.add_argument("--service", required=True, choices=["instagram", "facebook", "tiktok"])
    buffer_prepare_platform.add_argument("--slot", required=True, choices=["morning", "evening"])
    buffer_publish = commands.add_parser("buffer-publish", help="Schedule today's deal on Instagram, Facebook and TikTok")
    buffer_publish.add_argument("--date", default=date.today().isoformat())
    buffer_publish.add_argument("--send", action="store_true", help="Send a Telegram owner confirmation when new posts schedule")
    buffer_preflight = commands.add_parser("buffer-preflight", help="Check all channels, captions, media and recent delivery before scheduling")
    buffer_preflight.add_argument("--date", default=date.today().isoformat())
    buffer_repair = commands.add_parser("buffer-repair-future", help="Safely replace future queued posts without creating duplicates")
    buffer_repair.add_argument("--date", default=date.today().isoformat())
    buffer_repair.add_argument("--send", action="store_true", help="Send a private Telegram repair receipt")
    commands.add_parser("buffer-learn", help="Refresh real delivery and engagement results from Buffer")
    buffer_delivery = commands.add_parser("buffer-delivery-check", help="Verify all six daily Buffer deliveries")
    buffer_delivery.add_argument("--date", default=date.today().isoformat())
    buffer_delivery.add_argument("--strict", action="store_true", help="Fail when a post is missing or rejected")

    commands.add_parser("trial-plan", help="Print the duplicate-safe three-day campaign plan")
    trial_claim = commands.add_parser("trial-claim", help="Claim one trial slot before publishing")
    trial_claim.add_argument("--date", required=True)
    trial_claim.add_argument("--slot", required=True, type=int, choices=[0, 1, 2])
    trial_claim.add_argument("--payload", required=True)
    trial_publish = commands.add_parser("trial-publish", help="Publish a previously claimed trial payload")
    trial_publish.add_argument("--payload", required=True)
    trial_report = commands.add_parser("trial-report", help="Send the honest hosted-trial daily report")
    trial_report.add_argument("--date", required=True)
    seo_monitor = commands.add_parser("seo-monitor", help="Audit live SEO/GEO integrity and optionally alert the owner")
    seo_monitor.add_argument("--send", action="store_true")
    seo_monitor.add_argument("--json", action="store_true")
    seo_api = commands.add_parser("seo-api-report", help="Pull Google Search Console + Bing data and send a Telegram summary")
    seo_api.add_argument("--days", type=int, default=7, help="Lookback window in days")
    seo_api.add_argument("--send", action="store_true", help="Send to Telegram owner chat (requires credentials)")
    seo_api.add_argument("--authorize", action="store_true", help="Start GSC OAuth2 browser consent flow")
    tick = commands.add_parser("tick", help="Idempotent scheduler tick: generate, publish due, report after 21:00")
    tick.add_argument("--dry-run", action="store_true")
    return root


def _print_posts(rows) -> None:
    if not rows:
        print("No matching posts.")
        return
    for row in rows:
        print(f"#{row['id']:03d} {row['status']:<9} {row['scheduled_at']} | {row['product_name']} | {row['segment']} | {row['variant']}")


def _format_search_report(report: dict) -> list[str]:
    """Turn the search_apis.build_search_report dict into Telegram-ready lines."""
    lines: list[str] = []
    lines.append("📊 AI Tool Gems — Google + Bing Search Report")
    lines.append("")
    lines.append(f"📅 Period: {report.get('period', 'unknown')}")
    lines.append("")

    gsc = report.get("gsc", {})
    metadata = gsc.get("metadata", {})
    if "error" in metadata:
        lines.append(f"🔴 GSC Error: {metadata['error']}")
    else:
        lines.append(f"🔍 GSC — Impressions: {metadata.get('total_impressions', 0):,}")
        lines.append(f"🔍 GSC — Clicks: {metadata.get('total_clicks', 0):,}")
        lines.append("")
        lines.append("🏆 Top queries (by impressions):")
        for row in gsc.get("top_queries", []):
            q = row.get("keys", ["?"])[0]
            imp = int(row.get("impressions", 0))
            clk = int(row.get("clicks", 0))
            ctr = float(row.get("ctr", 0)) * 100
            pos = float(row.get("position", 0))
            lines.append(f"  • {q[:60]}")
            lines.append(f"    Impressions: {imp:,} | Clicks: {clk:,} | CTR: {ctr:.1f}% | Pos: {pos:.1f}")
        lines.append("")

    site_status = gsc.get("site_status", {})
    if "error" not in site_status:
        lines.append("🛡️ GSC Site Status:")
        coverage = site_status.get("coverageState", {})
        lines.append(f"  Coverage issues: {coverage.get('coverageState', 'unknown')}")
        sitemaps = site_status.get("sitemaps", [])
        for s in sitemaps:
            lines.append(f"  Sitemap: {s.get('path', '?')} — {s.get('lastSubmitted', '?')} | Status: {s.get('sitemapStatus', '?')}")
        lines.append("")

    bing = report.get("bing", {})
    if bing.get("site_info", {}).get("error"):
        lines.append(f"🔴 Bing Error: {bing['site_info']['error']}")
    else:
        info = bing.get("site_info", {}).get("siteInfo", {})
        lines.append("🌐 Bing Webmaster:")
        lines.append(f"  Site: {info.get('siteUrl', '?')}")
        lines.append(f"  Ownership: {info.get('ownershipType', '?')}")
        lines.append(f"  Crawl rate: {info.get('crawlRate', '?')}")

    crawl = bing.get("crawl_stats", {}).get("crawlStats", {})
    if crawl:
        lines.append("")
        lines.append("  Last crawl: " + crawl.get("lastCrawled", "?"))
        lines.append(f"  Crawled URLs (7d): {crawl.get('pagesCrawled', '?'):,}")
        lines.append(f"  Pages requested: {crawl.get('pagesRequested', '?'):,}")

    lines.append("")
    lines.append("— This report runs daily via GitHub Actions.")
    return lines


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
    elif args.command == "setup-bot":
        setup_bot(settings)
        print("Telegram bot commands and descriptions configured.")
    elif args.command == "process-commands":
        print(f"Handled {process_updates(settings)} new private command(s).")
    elif args.command == "social-pack":
        pack_date = date.fromisoformat(args.date)
        if args.send:
            print(f"Sent {send_daily_pack(settings, pack_date)} private content-pack message(s).")
        else:
            print("\n\n---\n\n".join(daily_pack(settings, pack_date)))
    elif args.command == "social-alert":
        send_automation_failure_alert(settings)
        print("Owner failure alert delivered.")
    elif args.command == "buffer-status":
        print(json.dumps(buffer_connection_status(settings), indent=2, ensure_ascii=False))
    elif args.command == "buffer-prepare":
        for asset in render_daily_media(date.fromisoformat(args.date)):
            print(asset.relative_to(Path.cwd()))
    elif args.command == "buffer-prepare-platform":
        asset = render_platform_media(date.fromisoformat(args.date), args.service, args.slot)
        print(asset.relative_to(Path.cwd()))
    elif args.command == "buffer-publish":
        publish_date = date.fromisoformat(args.date)
        result = publish_daily_deal(settings, publish_date)
        if args.send:
            confirmation = format_publish_confirmation(settings, publish_date, result)
            if confirmation:
                if not settings.owner_reports_ready:
                    raise RuntimeError("Owner Telegram credentials are missing")
                TelegramClient(settings.telegram_bot_token).send_with_retry(
                    settings.telegram_owner_chat_id, confirmation
                )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "buffer-preflight":
        print(json.dumps(campaign_preflight(settings, date.fromisoformat(args.date)), indent=2, ensure_ascii=False))
    elif args.command == "buffer-repair-future":
        repair_date = date.fromisoformat(args.date)
        result = repair_future_posts(settings, repair_date)
        if args.send and settings.owner_reports_ready and result["repaired"]:
            repaired = ", ".join(key.replace(":", " ").title() for key in result["repaired"])
            TelegramClient(settings.telegram_bot_token).send_with_retry(
                settings.telegram_owner_chat_id,
                "✅ Buffer queue repaired safely\n\n"
                f"Updated in place: {repaired}\n"
                "New WhatsApp number, improved caption and current media are applied. No duplicate post was created.",
            )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "buffer-learn":
        print(json.dumps(refresh_performance(settings), indent=2, ensure_ascii=False))
    elif args.command == "buffer-delivery-check":
        print(json.dumps(
            delivery_audit(settings, date.fromisoformat(args.date), strict=args.strict),
            indent=2,
            ensure_ascii=False,
        ))
    elif args.command == "trial-plan":
        print(json.dumps(trial_plan(settings), indent=2, ensure_ascii=False))
    elif args.command == "trial-claim":
        payload = claim_slot(settings, date.fromisoformat(args.date), args.slot, Path(args.payload))
        print("already-claimed" if payload is None else f"claimed:{payload['key']}")
    elif args.command == "trial-publish":
        payload = publish_payload(settings, Path(args.payload))
        print(f"published:{payload['key']}:{payload['product_name']}")
    elif args.command == "trial-report":
        sent = send_trial_report(settings, date.fromisoformat(args.date))
        print("report-sent" if sent else "report-already-sent")
    elif args.command == "seo-monitor":
        result = run_monitor(settings, send=args.send)
        print(json.dumps(result, indent=2) if args.json else format_seo_report(result))
    elif args.command == "seo-api-report":
        from .search_apis import GSCClient, BingClient, build_search_report

        if args.authorize:
            if not settings.gsc_client_id or not settings.gsc_client_secret:
                raise RuntimeError("Set GSC_CLIENT_ID and GSC_CLIENT_SECRET in .env or GitHub secrets first")
            client = GSCClient(settings.gsc_client_id, settings.gsc_client_secret, settings.site_url)
            client.authorize()
            print("Done. Run without --authorize next time.")
        else:
            if not settings.gsc_client_id or not settings.gsc_client_secret:
                raise RuntimeError("GSC_CLIENT_ID and GSC_CLIENT_SECRET are required for seo-api-report")
            if not settings.bing_api_key:
                print("⚠️  BING_API_KEY not set — Bing data skipped")
            gsc = GSCClient(settings.gsc_client_id, settings.gsc_client_secret, settings.site_url)
            bing = BingClient(settings.bing_api_key, settings.site_url) if settings.bing_api_key else None
            report = build_search_report(gsc, bing, days=args.days)
            lines = _format_search_report(report)
            print("\n".join(lines))
            if args.send:
                if not settings.owner_reports_ready:
                    raise RuntimeError("Owner Telegram credentials are missing")
                TelegramClient(settings.telegram_bot_token).send_with_retry(
                    settings.telegram_owner_chat_id, "\n".join(lines)
                )
                print("→ Telegram report sent.")
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
