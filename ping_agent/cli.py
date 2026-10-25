"""
CLI Interface for AIToolGems Instant Ping & Indexing Agent (PING-AGENT).
Provides commands: ping, verify, status, report.
"""

import argparse
import sys
import json
from ping_agent.dispatcher import dispatch_urls
from ping_agent.verifier import get_sitemap_urls, verify_key_setup
from ping_agent.history import record_dispatch, load_history

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def cmd_ping(args):
    """Executes a ping dispatch for sitemap URLs or specific targets."""
    if args.all:
        urls = get_sitemap_urls()
        if not urls:
            print("[PING-AGENT] Error: No URLs discovered in sitemap.xml")
            sys.exit(1)
    elif args.urls:
        urls = args.urls
    else:
        print("[PING-AGENT] Specify --all to ping all sitemap URLs, or pass specific URL arguments.")
        sys.exit(1)

    print("=" * 65)
    print(f"[PING-AGENT] Instant Search Engine Dispatcher")
    print(f" * Target URLs:     {len(urls)}")
    print(f" * Mode:            {'DRY RUN (Simulated)' if args.dry_run else 'LIVE SUBMISSION'}")
    print("=" * 65)

    result = dispatch_urls(urls, dry_run=args.dry_run)

    if not args.dry_run and result.get("status") in ("success", "partial_error"):
        record_dispatch(urls, result)

    print(json.dumps(result, indent=2))

    if result.get("status") in ("success", "dry_run"):
        print("[PING-AGENT] [SUCCESS] URLs successfully dispatched to IndexNow protocol.")
        sys.exit(0)
    else:
        print("[PING-AGENT] [WARN] Dispatch completed with partial or full errors.")
        sys.exit(1)


def cmd_verify(args):
    """Verifies local and remote IndexNow key infrastructure."""
    print("=" * 65)
    print("[PING-AGENT] Key & Infrastructure Verification")
    print("=" * 65)
    status = verify_key_setup(remote_check=args.remote)
    print(json.dumps(status, indent=2))

    if status.get("local_file_exists") and status.get("local_content_matches"):
        print("[PING-AGENT] [OK] Local IndexNow key file is valid.")
        if args.remote:
            if status.get("remote_accessible"):
                print("[PING-AGENT] [OK] Remote key URL is live on production!")
            else:
                print("[PING-AGENT] [WARN] Remote key file could not be verified on production.")
                sys.exit(1)
        sys.exit(0)
    else:
        print("[PING-AGENT] [ERROR] Local key file is missing or invalid.")
        sys.exit(1)


def cmd_status(args):
    """Displays recent ping history and metrics."""
    print("=" * 65)
    print("[PING-AGENT] Submissions & Indexing History")
    print("=" * 65)
    history = load_history()
    print(f" * Total Dispatches: {history.get('total_dispatches', 0)}")
    print(f" * Last Dispatch:    {history.get('last_dispatch', 'Never')}")
    print(f" * Tracked URLs:     {len(history.get('url_history', {}))}")
    print("\nRecent Dispatch Runs:")
    for run in history.get("recent_runs", [])[:5]:
        print(f"  - [{run.get('timestamp')}] {run.get('urls_count')} URLs -> Status: {run.get('status')}")


def main():
    parser = argparse.ArgumentParser(
        description="AIToolGems Instant Ping & Indexing Autonomous Agent"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ping command
    ping_parser = subparsers.add_parser("ping", help="Dispatch URLs to search engines via IndexNow")
    ping_parser.add_argument("--all", action="store_true", help="Ping all indexable URLs in sitemap.xml")
    ping_parser.add_argument("--dry-run", action="store_true", help="Simulate submission without network call")
    ping_parser.add_argument("urls", nargs="*", help="Specific URL(s) to ping")
    ping_parser.set_defaults(func=cmd_ping)

    # verify command
    verify_parser = subparsers.add_parser("verify", help="Verify IndexNow key file locally and remotely")
    verify_parser.add_argument("--remote", action="store_true", help="Perform live HTTP check against https://aitoolgems.tech")
    verify_parser.set_defaults(func=cmd_verify)

    # status command
    status_parser = subparsers.add_parser("status", help="View submission history and recent runs")
    status_parser.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
