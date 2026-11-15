"""CLI entrypoint for AI Tool Gems Backlink Agent."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .facts import get_verified_facts
from .reports import generate_pipeline_report
from .tracker import (
    DEFAULT_CSV_PATH,
    execute_verification,
    summarize_tracker,
    validate_tracker_data,
)


def _load_env_if_present() -> None:
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main():
    _load_env_if_present()
    parser = argparse.ArgumentParser(description="AI Tool Gems Autonomous Backlink Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Validate / Audit command
    sub_audit = subparsers.add_parser("audit", help="Validate tracker CSV and sameAs entity hygiene")
    sub_audit.add_argument("--csv", default=str(DEFAULT_CSV_PATH))

    # Verify command
    sub_verify = subparsers.add_parser("verify", help="Run strict HTML anchor verifier over source pages")
    sub_verify.add_argument("--csv", default=str(DEFAULT_CSV_PATH))
    sub_verify.add_argument("--write", action="store_true", help="Write verified classifications back to CSV")

    # Report command
    sub_report = subparsers.add_parser("report", help="Generate executive pipeline markdown & JSON report")
    sub_report.add_argument("--csv", default=str(DEFAULT_CSV_PATH))
    sub_report.add_argument("--telegram", action="store_true", help="Dispatch report to owner Telegram")

    # Facts command
    sub_facts = subparsers.add_parser("facts", help="Display verified commercial facts or check copy")
    sub_facts.add_argument("--check-copy", help="Check proposed outreach copy for disallowed claims")

    # WP13 Autonomous Intelligence Pipeline
    sub_daily = subparsers.add_parser("run-daily-intelligence", help="Run full Discovery -> Scoring -> Drafting -> Telegram pipeline")
    sub_daily.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without external network calls")
    sub_daily.add_argument("--no-telegram", action="store_true", help="Enqueue to outbox but do not flush Telegram")
    sub_daily.add_argument("--no-reports", action="store_true", help="Skip writing markdown and JSON report files")

    # WP14 Outbox Leases Recovery Command
    sub_recover = subparsers.add_parser("recover-leases", help="Recover stale outbox worker leases stuck in sending state")
    sub_recover.add_argument("--timeout", type=int, default=300, help="Lease age in seconds to consider stale (default 300)")

    # WP15 Acquisition Lifecycle Report Command
    sub_acq = subparsers.add_parser("acquisition-report", help="Generate earned backlink acquisition and conversion report")
    sub_acq.add_argument("--db", default=None, help="Path to lifecycle SQLite DB")
    sub_acq.add_argument("--output-dir", default="reports/acquisition", help="Directory to export report files")
    sub_acq.add_argument("--no-export", action="store_true", help="Print to console only without saving files")

    # WP15 Advanced Live Anchor Verification Command
    sub_adv_verify = subparsers.add_parser("verify-advanced", help="Run deep multi-hop SSRF & indexability anchor verification on a URL")
    sub_adv_verify.add_argument("source_url", help="URL of external source page containing backlink")
    sub_adv_verify.add_argument("target_url", help="Target URL that should be linked to (e.g. https://aitoolgems.tech/)")
    sub_adv_verify.add_argument("--expected-anchor", default=None, help="Optional substring anchor text expected")
    sub_adv_verify.add_argument("--timeout", type=float, default=15.0, help="HTTP request timeout in seconds")

    args = parser.parse_args()

    if not args.command or args.command == "audit":
        csv_path = Path(getattr(args, "csv", DEFAULT_CSV_PATH))
        rows, errs = validate_tracker_data(csv_path)
        if errs:
            print(f"❌ VALIDATION FAILED with {len(errs)} error(s):")
            for e in errs:
                print(f"  • {e}")
            sys.exit(1)
        print(f"✅ PASS: {len(rows)} tracker rows valid. Schema, status, and sameAs hygiene 100% compliant.")

    elif args.command == "verify":
        csv_path = Path(args.csv)
        rows, errs = validate_tracker_data(csv_path)
        if errs:
            print(f"❌ Cannot verify: tracker has errors: {errs}")
            sys.exit(1)
        print(f"Probing {len(rows)} rows for verified backlinks (strict HTML anchor parsing)...")
        results = execute_verification(rows, write_back=args.write, csv_path=csv_path)
        for r in results:
            print(
                f"{r.source_page} -> classification={r.classification} "
                f"status={r.status_code} target_found={r.target_found} rel={r.rel_tokens}"
            )

    elif args.command == "report":
        csv_path = Path(args.csv)
        rows, errs = validate_tracker_data(csv_path)
        if errs:
            print(f"❌ Cannot report: tracker has errors: {errs}")
            sys.exit(1)
        md_report, json_data = generate_pipeline_report(rows)
        print(md_report)

        if args.telegram:
            from seo_agent.agent.telegram_notifier import TelegramNotifier  # type: ignore
            notifier = TelegramNotifier()
            if notifier.is_configured():
                res = notifier.send_message(md_report)
                if res.success:
                    print(f"✅ Report delivered to Telegram (sent {res.chunks_sent} chunk(s))")
                else:
                    print(f"⚠️ Telegram delivery failed: {res.error}")
            else:
                print("ℹ️ Telegram not configured; skipping dispatch.")

    elif args.command == "facts":
        facts = get_verified_facts()
        if args.check_copy:
            violations = facts.validate_copy(args.check_copy)
            if violations:
                print(f"❌ Copy contains {len(violations)} disallowed claim(s):")
                for v in violations:
                    print(f"  • {v}")
                sys.exit(1)
            else:
                print("✅ Copy passed verified facts truth check.")
        else:
            print(json.dumps(facts.as_dict(), indent=2))

    elif args.command == "run-daily-intelligence":
        from .pipeline import BacklinkIntelligencePipeline
        from .telegram_delivery import TelegramOutboxManager

        outbox = TelegramOutboxManager(dry_run=args.dry_run)
        pipeline = BacklinkIntelligencePipeline(outbox_manager=outbox)

        print("🚀 Executing Autonomous Backlink Intelligence Pipeline...")
        summary = pipeline.run_daily_intelligence(
            dispatch_telegram=not args.no_telegram,
            export_reports=not args.no_reports,
        )

        print("\n🏆 Daily Cycle Summary:")
        print(f"  • Duration: {summary['duration_seconds']}s")
        print(f"  • Discovered: {summary['discovered_count']} prospects")
        print(f"  • Scored: {summary['scored_count']} opportunities")
        print(f"  • High Priority (>= 75): {summary['tiers']['high_priority']}")
        print(f"  • Investigate (55-74): {summary['tiers']['investigate']}")
        print(f"  • Quarantined (< 55): {summary['tiers']['quarantine']}")
        print(f"  • Draft Packages Ready: {summary['drafts_generated_count']}")
        print(f"  • Telegram Outbox: {summary['outbox_flush']}")
        if summary.get("report_files"):
            print(f"  • Markdown Report: {summary['report_files'].get('markdown')}")
            print(f"  • JSON Report: {summary['report_files'].get('json')}")

    elif args.command == "recover-leases":
        from .telegram_delivery import LocalSQLiteOutboxStore

        store = LocalSQLiteOutboxStore()
        recovered = store.recover_stale_leases(lease_timeout_seconds=args.timeout)
        print(f"✅ Recovered {recovered} stale outbox worker lease(s) (timeout: {args.timeout}s).")

    elif args.command == "acquisition-report":
        from .lifecycle.store import LocalSQLiteLifecycleStore
        from .reporting.acquisition_reporter import AcquisitionReporter

        db_path = Path(args.db) if args.db else None
        store = LocalSQLiteLifecycleStore(db_path=db_path)
        output_dir = Path(args.output_dir) if args.output_dir else Path("reports/acquisition")
        reporter = AcquisitionReporter(lifecycle_store=store, reports_dir=output_dir)

        report = reporter.generate_acquisition_report()
        print(report.get("markdown_report", ""))

        if not args.no_export:
            files = report.get("report_files", {})
            print(f"\n📁 Exported acquisition reports:")
            print(f"  • Markdown: {files.get('markdown')}")
            print(f"  • JSON: {files.get('json')}")

    elif args.command == "verify-advanced":
        from .advanced_verifier.verifier import AdvancedBacklinkVerifier

        verifier = AdvancedBacklinkVerifier(timeout=args.timeout)
        print(f"🔍 Probing source page: {args.source_url}")
        print(f"🎯 Target expected: {args.target_url}")

        res = verifier.verify_url(
            source_page_url=args.source_url,
            target_asset_url=args.target_url,
        )

        print("\n📊 Verification Outcome:")
        print(f"  • Qualification: {res.qualification.upper()}")
        print(f"  • Live Backlink Earned: {'✅ YES' if res.is_live_backlink else '❌ NO'}")
        print(f"  • HTTP Status: {res.http_status}")
        print(f"  • Anchor Found: {res.anchor_found}")
        print(f"  • Exact Anchor Text: {res.actual_anchor_text}")
        print(f"  • Actual Href: {res.actual_href}")
        print(f"  • Rel Tokens: {res.rel_tokens}")
        print(f"  • Indexable: {res.is_indexable} (Noindex: {res.noindex_source})")
        print(f"  • Canonical: {res.canonical_url}")
        print(f"  • Redirect Hops: {len(res.redirect_chain)}")
        print(f"  • Content Hash: {res.content_hash[:16]}..." if res.content_hash else "  • Content Hash: None")
        if res.error_message:
            print(f"  • Error Details: {res.error_message}")


if __name__ == "__main__":
    main()
