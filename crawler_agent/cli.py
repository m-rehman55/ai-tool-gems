"""
CLI Interface for AIToolGems Technical SEO & Web Crawling Agent (Agent 2).
Provides commands: crawl, diff, audit, status.
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from crawler_agent.engine import CrawlerEngine
from crawler_agent.analyzer import TechnicalSEOAnalyzer
from crawler_agent.inventory import URLInventoryDatabase

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def cmd_crawl(args):
    """Executes live or local site crawl."""
    engine = CrawlerEngine(max_pages=args.max_pages)
    inventory = URLInventoryDatabase()

    print("=" * 65)
    print(f"🕷️ HERMES Technical SEO Crawler — Mode: {'LIVE PRODUCTION' if args.live else 'LOCAL REPOSITORY'}")
    print("=" * 65)

    if args.live:
        records = engine.crawl_live_production()
    else:
        records = engine.crawl_local_repository()

    for r in records:
        inventory.upsert_crawl_record(r)

    print(f"\n✅ Crawled {len(records)} URLs successfully.")
    print(f"📁 Updated URL Inventory Database at: data/seo/url_inventory_db.json")


def cmd_audit(args):
    """Runs deep 30+ point technical SEO audit across site crawl."""
    engine = CrawlerEngine(max_pages=args.max_pages)
    analyzer = TechnicalSEOAnalyzer()
    inventory = URLInventoryDatabase()

    print("=" * 65)
    print(f"📊 HERMES Technical SEO Health Audit")
    print("=" * 65)

    if args.live:
        records = engine.crawl_live_production()
        mode_str = "LIVE_PRODUCTION"
    else:
        records = engine.crawl_local_repository()
        mode_str = "LOCAL_REPOSITORY"

    for r in records:
        inventory.upsert_crawl_record(r)

    summary = analyzer.audit_crawl_dataset(records, crawl_mode=mode_str)

    # Update individual URL analysis in inventory
    for r in records:
        issues = []
        if r.headings.missing_h1:
            issues.append("Missing H1 heading tag")
        elif not r.headings.hierarchy_valid:
            issues.extend(r.headings.issues)
        if not r.has_trailing_slash:
            issues.append("Inconsistent trailing slash")
        if r.has_mixed_content:
            issues.append("Mixed content detected")
        if not r.canonical:
            issues.append("Missing canonical tag")
        inventory.update_analysis_outcome(r.url, issues)

    print(f"\n🏆 Technical Health Score: {summary.technical_health_score}/100")
    print(f"  • Total URLs Scanned:             {summary.total_urls_scanned}")
    print(f"  • Broken Links (4xx/5xx):         {summary.broken_links_count}")
    print(f"  • Orphan Pages Detected:          {summary.orphan_pages_count}")
    print(f"  • Duplicate Title Tags:           {summary.duplicate_titles_count}")
    print(f"  • Duplicate Meta Descriptions:    {summary.duplicate_metas_count}")
    print(f"  • Missing H1 Headings:            {summary.missing_h1_count}")
    print(f"  • Heading Hierarchy Violations:   {summary.heading_hierarchy_violations}")
    print(f"  • Images Missing Alt Text:        {summary.images_missing_alt_count}")
    print(f"  • Mixed Content Violations:       {summary.mixed_content_violations}")
    print(f"  • Crawl Budget Waste Items:       {summary.crawl_budget_waste_count}")
    print(f"  • Average Fetch Time:             {summary.average_fetch_time_ms}ms")

    if summary.critical_issues:
        print("\n⚠️ Critical Issues:")
        for ci in summary.critical_issues:
            print(f"  [{ci['severity']}] {ci['type']}: {ci['count']} occurrence(s)")


def cmd_diff(args):
    """Compares live production HTML vs local repository content."""
    engine = CrawlerEngine()
    diff_report = engine.compare_live_vs_local()
    print("=" * 65)
    print("🔄 Live Production vs Local Repository Diff Report")
    print(f" * URLs Sampled:     {diff_report['total_urls_compared']}")
    print(f" * Discrepancies:    {diff_report['discrepancies_count']}")
    print("=" * 65)

    if diff_report["discrepancies"]:
        for d in diff_report["discrepancies"]:
            print(f"\nTarget: {d['url']}")
            for m in d.get("mismatches", [d.get("issue")]):
                print(f"  - {m}")
    else:
        print("✅ 100% Parity: Zero discrepancies detected between live production and local repository.")


def build_parser():
    parser = argparse.ArgumentParser(description="HERMES Technical SEO Crawler Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # crawl
    p_crawl = subparsers.add_parser("crawl", help="Execute website crawl")
    p_crawl.add_argument("--live", action="store_true", help="Crawl live production website")
    p_crawl.add_argument("--max-pages", type=int, default=150, help="Maximum pages to crawl (default: 150)")
    p_crawl.set_defaults(func=cmd_crawl)

    # audit
    p_audit = subparsers.add_parser("audit", help="Run comprehensive technical SEO health audit")
    p_audit.add_argument("--live", action="store_true", help="Audit live production website")
    p_audit.add_argument("--max-pages", type=int, default=150, help="Maximum pages to crawl")
    p_audit.set_defaults(func=cmd_audit)

    # diff
    p_diff = subparsers.add_parser("diff", help="Compare live production vs local repository")
    p_diff.set_defaults(func=cmd_diff)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

