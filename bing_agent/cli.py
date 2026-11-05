"""
cli.py - Command-Line Interface for bing_agent.

Commands:
- python -m bing_agent status: Check Bing API authorization, site verification, quota, and key files.
- python -m bing_agent crawl-stats: Inspect crawl statistics, errors, and in-index progression.
- python -m bing_agent query-stats: Inspect real Bing queries, impressions, and rankings.
- python -m bing_agent indexnow-queue: View durable IndexNow submission queue status.
- python -m bing_agent submit-deltas: Detect modified/new URLs and dispatch delta batch to IndexNow.
- python -m bing_agent audit: Run complete Bing Webmaster intelligence audit & export report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Fix Windows cp1252 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from bing_agent.client import BingWebmasterClient
from bing_agent.indexnow_queue import IndexNowQueueEngine
from bing_agent.analyzer import BingWebmasterAnalyzer


def run_status(args: argparse.Namespace) -> int:
    """Checks Bing Webmaster authorization, quota, and key setup."""
    print("\n🌐 AIToolGems Bing Webmaster & IndexNow Status")
    print("=" * 65)

    client = BingWebmasterClient()
    queue_engine = IndexNowQueueEngine()
    key_info = queue_engine.verify_key_infrastructure()

    print(f"🔑 API Key Present:      {'Yes ✅' if client.is_authorized else 'No ❌'}")
    print(f"🛡️ Local Key File:       {'Valid ✅' if key_info['content_valid'] else 'Invalid ❌'} ({key_info['key_file']})")
    print(f"📍 Key Location:         {key_info['key_location']}")

    if not client.is_authorized:
        print("\n❌ Set BING_API_KEY in .env to enable official Bing Webmaster Tools API access.")
        return 1

    try:
        sites = client.get_user_sites()
        print(f"\n📂 Verified Sites ({len(sites)}):")
        for s in sites:
            v_sym = "✅ Verified" if s.is_verified else "❌ Unverified"
            print(f"   • {s.url} [{v_sym}]")

        quota = client.get_submission_quota()
        print(f"\n📊 IndexNow & URL Quota:")
        print(f"   • Daily Quota:   {quota.daily_quota}")
        print(f"   • Monthly Quota: {quota.monthly_quota}")

        queue = queue_engine.load_queue()
        pending = sum(1 for item in queue.values() if item.status == "QUEUED")
        submitted = sum(1 for item in queue.values() if item.status == "SUBMITTED")
        print(f"\n📬 Durable Submission Queue:")
        print(f"   • Pending Deltas:  {pending}")
        print(f"   • Total Submitted: {submitted}")
        print("=" * 65 + "\n")
        return 0

    except Exception as e:
        print(f"\n❌ Error querying Bing Webmaster API: {e}\n")
        return 1


def run_crawl_stats(args: argparse.Namespace) -> int:
    """Inspects crawl statistics and in-index count."""
    client = BingWebmasterClient()
    if not client.is_authorized:
        print("[ERROR] BING_API_KEY not configured.")
        return 1

    stats = client.get_crawl_stats()
    print(f"\n🕷️ Bing Crawl Statistics & In-Index Progression ({len(stats)} days):")
    print("=" * 75)
    print(f"{'Date':<12} | {'Crawled':<8} | {'In-Index':<9} | {'Errors':<8} | {'2xx':<6} | {'4xx':<6}")
    print("-" * 75)
    for s in stats[-14:]:  # last 14 days
        print(f"{s.date:<12} | {s.crawled_pages:<8} | {s.in_index:<9} | {s.crawl_errors:<8} | {s.code_2xx:<6} | {s.code_4xx:<6}")
    print("=" * 75 + "\n")
    return 0


def run_query_stats(args: argparse.Namespace) -> int:
    """Displays empirical Bing search queries."""
    client = BingWebmasterClient()
    if not client.is_authorized:
        print("[ERROR] BING_API_KEY not configured.")
        return 1

    queries = client.get_query_stats()
    print(f"\n🔎 Bing Empirical Search Queries ({len(queries)} query events recorded):")
    print("=" * 80)
    print(f"{'Query':<45} | {'Date':<10} | {'Imp':<5} | {'Clicks':<6} | {'Pos'}")
    print("-" * 80)
    for q in queries[:20]:
        print(f"{q.query[:43]:<45} | {q.date:<10} | {q.impressions:<5} | {q.clicks:<6} | #{q.avg_impression_position:.1f}")
    print("=" * 80 + "\n")
    return 0


def run_indexnow_queue(args: argparse.Namespace) -> int:
    """Inspects pending and historical IndexNow queue items."""
    queue_engine = IndexNowQueueEngine()
    queue = queue_engine.load_queue()
    print(f"\n📬 Durable IndexNow Submission Queue ({len(queue)} total tracked URLs):")
    print("=" * 75)
    print(f"{'URL':<50} | {'Reason':<15} | {'Status'}")
    print("-" * 75)
    for url, item in list(queue.items())[:20]:
        print(f"{url[:48]:<50} | {item.reason:<15} | {item.status}")
    print("=" * 75 + "\n")
    return 0


def run_submit_deltas(args: argparse.Namespace) -> int:
    """Detects updated/new URLs only and dispatches batch to IndexNow endpoints."""
    print("\n🚀 IndexNow Delta Submission Engine")
    print("=" * 65)

    queue_engine = IndexNowQueueEngine()
    print("--> STEP 1: Scanning repository for newly created or updated URLs...")
    deltas = queue_engine.detect_deltas()
    print(f"    Detected {len(deltas)} URL delta(s) requiring notification.")

    if not deltas and not args.force:
        print("    ✅ All repository URLs match previously submitted content hashes.")
        print("    Zero redundant IndexNow requests required (Quota preserved).\n")
        return 0

    print("--> STEP 2: Submitting delta batch across IndexNow endpoints...")
    dry_run = getattr(args, "dry_run", False)
    records = queue_engine.dispatch_pending(dry_run=dry_run, batch_limit=50)

    for r in records:
        status_sym = "✅ Accepted (HTTP 200/202)" if r.is_accepted else f"❌ Failed (HTTP {r.http_status})"
        print(f"    • {r.endpoint}: {status_sym} ({r.duration_ms}ms)")

    print("\nℹ️ Policy Confirmation:")
    print("   • Acceptance confirms notification was received by IndexNow engine for queuing.")
    print("   • Crawling and indexing proceed independently per search engine crawl budget.")
    print("   • Google does NOT participate in IndexNow (Google indexing tracked via GSC).\n")
    return 0


def run_audit(args: argparse.Namespace) -> int:
    """Runs full Bing Webmaster intelligence audit and exports reports."""
    print("\n🌐 Running AIToolGems Bing Webmaster Technical & Growth Audit...")
    client = BingWebmasterClient()
    if not client.is_authorized:
        print("[ERROR] BING_API_KEY not configured.")
        return 1

    analyzer = BingWebmasterAnalyzer(client=client)
    summary = analyzer.run_audit()

    print(f"    Site: {summary.site_url} (Verified: {summary.is_verified})")
    print(f"    In-Index: {summary.current_pages_in_index} pages | Quota: {summary.daily_quota}/day")
    print(f"    Tracked Queries: {summary.total_bing_queries} (Imp: {summary.total_bing_impressions}, Clicks: {summary.total_bing_clicks})")
    print(f"    Average Position: #{summary.average_bing_position:.1f}")

    print("\n🏆 Top Strategic Insights:")
    for i in summary.cross_engine_insights[:5]:
        print(f"    • [{i.opportunity_type}] '{i.query}' (Bing Pos #{i.bing_position:.1f}): {i.recommendation}")

    print("\n💡 Strategic Recommendations:")
    for r in summary.recommendations:
        print(f"    • {r}")
    print()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m bing_agent",
        description="Autonomous Bing Webmaster Intelligence & Durable IndexNow Queue for AIToolGems",
    )
    subparsers = parser.add_subparsers(dest="command", help="Operational commands")

    # status
    p_status = subparsers.add_parser("status", help="Check Bing API, site verification, quota, and key files")
    p_status.set_defaults(func=run_status)

    # crawl-stats
    p_crawl = subparsers.add_parser("crawl-stats", help="Inspect crawl statistics, errors, and in-index count")
    p_crawl.set_defaults(func=run_crawl_stats)

    # query-stats
    p_query = subparsers.add_parser("query-stats", help="Inspect real Bing queries, impressions, and rankings")
    p_query.set_defaults(func=run_query_stats)

    # indexnow-queue
    p_queue = subparsers.add_parser("indexnow-queue", help="View durable IndexNow submission queue")
    p_queue.set_defaults(func=run_indexnow_queue)

    # submit-deltas
    p_submit = subparsers.add_parser("submit-deltas", help="Detect modified/new URLs and dispatch to IndexNow")
    p_submit.add_argument("--dry-run", action="store_true", help="Simulate dispatch without sending HTTP requests")
    p_submit.add_argument("--force", action="store_true", help="Force submission even if no deltas detected")
    p_submit.set_defaults(func=run_submit_deltas)

    # audit
    p_audit = subparsers.add_parser("audit", help="Run full Bing Webmaster intelligence audit")
    p_audit.set_defaults(func=run_audit)

    args = parser.parse_args()
    if not args.command:
        sys.exit(run_status(args))
    else:
        sys.exit(args.func(args))


if __name__ == "__main__":
    main()
