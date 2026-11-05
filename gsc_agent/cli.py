"""
CLI Interface for AIToolGems Google Search Console Intelligence Agent (GSC-AGENT).
Provides commands: audit, inspect, opportunities, report.
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gsc_agent.client import GSCClient
from gsc_agent.performance import GSCPerformanceAnalyzer
from gsc_agent.inspection import GSCInspectionManager
from gsc_agent.opportunities import GSCOpportunityEngine

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def cmd_audit(args):
    """Executes full GSC search performance audit with Pakistan filtering and pagination."""
    client = GSCClient()
    if not client.is_configured():
        print("❌ GSC credentials missing from .env or environment.")
        sys.exit(1)

    print("=" * 65)
    print("🔍 HERMES Google Search Console Intelligence Audit")
    print(f" * Target Property: {client.site_url}")
    print(f" * Filter Market:   Pakistan (country: pak)")
    print("=" * 65)

    end_date = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=args.days + 2)).strftime("%Y-%m-%d")

    filters = []
    if not args.global_market:
        filters.append({"dimension": "country", "operator": "equals", "expression": "pak"})

    print(f"Fetching search performance for {start_date} -> {end_date}...")
    rows, meta = client.query_search_analytics_paginated(
        start_date=start_date,
        end_date=end_date,
        dimensions=["query", "page"],
        dimension_filters=filters,
        max_total_rows=10000,
    )

    analyzer = GSCPerformanceAnalyzer()
    summary = analyzer.summarize_dataset(rows)
    brand_split = analyzer.segment_brand_vs_non_brand(rows)
    striking = analyzer.detect_striking_distance_queries(rows)
    high_imp_low_ctr = analyzer.detect_high_impression_low_ctr(rows)
    cannibalized = analyzer.detect_query_cannibalization(rows)

    print(f"\n📊 Summary Metrics ({args.days} Days):")
    print(f"  • Total Impressions: {summary.total_impressions:,}")
    print(f"  • Total Clicks:       {summary.total_clicks:,}")
    print(f"  • Average CTR:        {summary.average_ctr}%")
    print(f"  • Average Position:   {summary.average_position}")
    print(f"  • Unique Queries:     {summary.query_count:,}")
    print(f"  • Active Pages:       {summary.page_count:,}")

    print(f"\n🏷️ Brand vs Non-Brand:")
    print(f"  • Non-Brand Queries:  {brand_split['non_brand']['rows_count']} rows | {brand_split['non_brand']['summary'].total_impressions:,} imp")
    print(f"  • Brand Queries:      {brand_split['brand']['rows_count']} rows | {brand_split['brand']['summary'].total_impressions:,} imp")

    print(f"\n⚡ Growth Opportunities Found:")
    print(f"  • Striking Distance Queries (Pos 4-30): {len(striking)}")
    print(f"  • High-Impression, Low-CTR Queries:     {len(high_imp_low_ctr)}")
    print(f"  • Query Cannibalization Clashes:        {len(cannibalized)}")

    if high_imp_low_ctr:
        print("\n🎯 Top High-Impression / Low-CTR Opportunity:")
        top = high_imp_low_ctr[0]
        print(f"  • Query:       '{top['query']}'")
        print(f"  • Target Page: {top['target_page']}")
        print(f"  • Impressions: {top['impressions']:,} | Clicks: {top['clicks']} | CTR: {top['ctr_percent']}% | Pos: {top['position']}")

    if cannibalized:
        print("\n⚔️ Top Cannibalization Clash:")
        top_can = cannibalized[0]
        print(f"  • Query: '{top_can.query}' ({top_can.total_impressions:,} total imp across {len(top_can.competing_pages)} pages)")
        for p in top_can.competing_pages[:2]:
            print(f"    - {p['page']} (Imp: {p['impressions']}, Pos: {p['position']})")


def cmd_inspect(args):
    """Executes live Search Console URL Inspection API on a specific URL."""
    client = GSCClient()
    if not client.is_configured():
        print("❌ GSC credentials missing from .env or environment.")
        sys.exit(1)

    url = args.url.strip()
    print("=" * 65)
    print("🔬 HERMES GSC URL Inspection & Indexing Intelligence")
    print(f" * Target URL: {url}")
    print("=" * 65)

    manager = GSCInspectionManager(client)
    record = manager.inspect_url_with_cache(url, force_refresh=args.force)

    print(f"Verdict:              {record.verdict}")
    print(f"Coverage State:       {record.coverage_state}")
    print(f"Indexing State:       {record.indexing_state}")
    print(f"Robots Txt:           {record.robots_txt_state}")
    print(f"Page Fetch:           {record.page_fetch_state}")
    print(f"Google Canonical:     {record.google_canonical}")
    print(f"User Canonical:       {record.user_canonical}")
    print(f"Canonical Mismatch:   {record.canonical_mismatch}")
    print(f"Last Crawl Time:      {record.last_crawl_time}")
    print(f"Crawled As:           {record.crawled_as}")
    print(f"Rich Results Verdict: {record.rich_results_verdict}")
    if record.rich_results_items:
        print(f"Rich Result Types:    {', '.join(record.rich_results_items)}")
    print(f"Remediation Required: {record.requires_remediation}")


def cmd_opportunities(args):
    """Discovers and formulates actionable, URL-mapped optimization proposals."""
    client = GSCClient()
    if not client.is_configured():
        print("❌ GSC credentials missing from .env or environment.")
        sys.exit(1)

    end_date = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=args.days + 2)).strftime("%Y-%m-%d")

    filters = [{"dimension": "country", "operator": "equals", "expression": "pak"}]
    rows, _ = client.query_search_analytics_paginated(
        start_date=start_date,
        end_date=end_date,
        dimensions=["query", "page"],
        dimension_filters=filters,
        max_total_rows=10000,
    )

    engine = GSCOpportunityEngine()
    opportunities = engine.generate_opportunities_from_performance(rows)

    print("=" * 65)
    print(f"💡 Formulated {len(opportunities)} Actionable GSC Opportunities")
    print("=" * 65)

    for op in opportunities[:10]:
        print(f"\n[{op.opportunity_id}] {op.opportunity_type} (Score: {op.confidence_score * 100:.0f}%, Impact: {op.estimated_impact}/10)")
        print(f"  • Query:       {op.query}")
        print(f"  • Target URL:  {op.target_url}")
        print(f"  • Action:      {op.recommended_action}")
        print(f"  • Components:  {', '.join(op.affected_components)}")


def build_parser():
    parser = argparse.ArgumentParser(description="HERMES Google Search Console Intelligence Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # audit
    p_audit = subparsers.add_parser("audit", help="Run comprehensive GSC search performance audit")
    p_audit.add_argument("--days", type=int, default=28, help="Number of days to audit (default: 28)")
    p_audit.add_argument("--global-market", action="store_true", help="Do not filter by country: pak")
    p_audit.set_defaults(func=cmd_audit)

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect URL indexing state via GSC URL Inspection API")
    p_inspect.add_argument("url", type=str, help="Full URL to inspect")
    p_inspect.add_argument("--force", action="store_true", help="Force fresh inspection bypassing cache")
    p_inspect.set_defaults(func=cmd_inspect)

    # opportunities
    p_opp = subparsers.add_parser("opportunities", help="Formulate GSC growth opportunities")
    p_opp.add_argument("--days", type=int, default=28, help="Number of days to analyze (default: 28)")
    p_opp.set_defaults(func=cmd_opportunities)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
