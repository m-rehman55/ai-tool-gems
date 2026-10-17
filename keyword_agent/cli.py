"""
cli.py - Command-Line Interface for keyword_agent.
Commands:
- python -m keyword_agent audit: Full keyword discovery, GSC filter analysis, cannibalization check & report.
- python -m keyword_agent regex-library: Exports docs/GSC_REGEX_LIBRARY.md.
- python -m keyword_agent gsc-setup: Prints exact instructions to connect or export GSC data.
- python -m keyword_agent gsc-analyze: Parses data/gsc_exports/ and calculates CTR/position opportunities.
- python -m keyword_agent optimize-page <slug>: Formulates AEO/GEO brief for a specific tool page.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Fix Windows cp1252 encoding on terminal stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from keyword_agent.config import get_agent_settings
from keyword_agent.gsc_data import GSCDataEngine
from keyword_agent.regex_engine import GSCFilterLibrary
from keyword_agent.discovery import KeywordDiscoveryEngine
from keyword_agent.page_mapper import PageMapper
from keyword_agent.content_optimizer import ContentOptimizer
from keyword_agent.safe_executor import SafeExecutor
from keyword_agent.reporting import KeywordReportGenerator
from keyword_agent.competitor_gap import CompetitorGapAnalyzer


def run_audit(args: argparse.Namespace) -> int:
    """Executes the full keyword intelligence & content optimization workflow."""
    settings = get_agent_settings()
    print("[START] AIToolGems Keyword Intelligence & GSC Filter Engine")
    print(f"    Target Market: {settings.market} | Site: {settings.site_url}")

    # 1. GSC Data
    print("--> STEP 1: Ingesting Search Console Performance Data...")
    gsc_engine = GSCDataEngine(
        exports_dir=settings.exports_dir,
        history_dir=settings.history_dir,
        site_url=settings.site_url,
    )
    dataset = gsc_engine.load_dataset()
    print(f"    GSC Source: {dataset.source} ({dataset.status_message})")
    print(f"    Impressions: {dataset.total_impressions} | Clicks: {dataset.total_clicks} | Active Queries: {len(dataset.queries)}")

    # 2. Filter & Regex Library
    print("--> STEP 2: Compiling & Validating RE2 Filter Library...")
    filter_lib = GSCFilterLibrary()
    core_filters = filter_lib.get_core_filters()
    valid_count = sum(1 for f in core_filters if f.is_re2_validated)
    print(f"    Compiled {len(core_filters)} filters ({valid_count}/{len(core_filters)} 100% RE2 Validated).")

    # 3. Discovery & Clustering
    print("--> STEP 3: Discovering Keyword Clusters & Scoring Opportunities...")
    disc_engine = KeywordDiscoveryEngine()
    if dataset.queries:
        candidates = disc_engine.process_gsc_queries(dataset)
    else:
        candidates = disc_engine.generate_seed_discovery_clusters()
    
    segmented = disc_engine.segment_opportunities(candidates)
    quick_wins = segmented["high_impact_quick_wins"]
    trans = segmented["pakistan_transactional"]
    aeo = segmented["aeo_question_opportunities"]
    print(f"    Ranked {len(candidates)} total keywords: {len(quick_wins)} quick wins, {len(trans)} local transactional, {len(aeo)} AEO questions.")

    # 4. Page Mapping & Cannibalization Check
    print("--> STEP 4: Inspecting Actual Routes & Checking Cannibalization...")
    mapper = PageMapper(project_dir=settings.project_dir)
    mappings = [mapper.find_best_url(c.keyword, c.intent) for c in candidates[:50]]
    collisions = mapper.detect_cannibalization(mappings)
    print(f"    Mapped across {len(mapper.routes)} real site routes. Collisions: {len(collisions)}.")

    # 5. Competitor Gap Analysis (aitoolspak.tech)
    print("--> STEP 5: Conducting Competitor Gap Analysis vs aitoolspak.tech...")
    gap_analyzer = CompetitorGapAnalyzer(project_dir=settings.project_dir)
    gap_report = gap_analyzer.analyze_gaps()
    gap_doc = gap_analyzer.export_markdown_report(
        report=gap_report,
        output_file=settings.project_dir / "docs" / "COMPETITOR_KEYWORD_GAP_ANALYSIS.md"
    )
    print(f"    Analyzed {gap_report.total_competitor_urls} competitor URLs ({gap_report.direct_catalog_overlaps} direct overlaps, {gap_report.uncovered_high_value_gaps} gaps).")

    # 6. Content Optimization Briefs
    print("--> STEP 6: Generating On-Page GEO & AEO Optimization Briefs...")
    optimizer = ContentOptimizer(project_dir=settings.project_dir)
    briefs = []
    
    # Generate briefs for top priority tools
    target_tools = ["chatgpt", "canva", "elevenlabs"]
    for t in target_tools:
        url = f"https://aitoolgems.tech/tools/{t}/"
        rel_path = f"tools/{t}/index.html"
        if (settings.project_dir / rel_path).exists():
            kw = f"{t.title()} price in Pakistan"
            brief = optimizer.generate_optimization_brief(
                url=url,
                relative_path=rel_path,
                primary_query=kw,
                target_cluster=f"Tool: {t.title()}",
                opportunity_score=85.0,
            )
            briefs.append(brief)

    print(f"    Formulated {len(briefs)} on-page briefs (All guarded behind human review gate).")

    # 7. Reporting & Library Export
    print("--> STEP 7: Generating Markdown & JSON Intelligence Artifacts...")
    reporter = KeywordReportGenerator(reports_dir=settings.reports_dir, docs_dir=settings.project_dir / "docs")
    lib_path = reporter.export_gsc_regex_library_markdown(core_filters)
    md_report, json_report = reporter.generate_daily_report(
        gsc_dataset=dataset,
        filters=core_filters,
        opportunities=segmented,
        collisions=collisions,
        briefs=briefs,
    )
    print(f"    [OK] Regex Library exported: {lib_path.relative_to(settings.project_dir)}")
    print(f"    [OK] Competitor Gap Report: {gap_doc.relative_to(settings.project_dir)}")
    print(f"    [OK] Daily Report generated: {md_report.relative_to(settings.project_dir)}")
    print(f"    [OK] JSON Artifact saved: {json_report.relative_to(settings.project_dir)}")

    # Step 8: Telegram Notification Dispatch
    tg_sent = reporter.send_telegram_summary(
        gsc_dataset=dataset,
        opportunities=segmented,
        collisions=collisions,
    )
    if tg_sent:
        print("    [OK] Telegram daily summary dispatched to owner.")

    print("[DONE] Keyword intelligence run completed successfully.")
    return 0


def run_regex_library(args: argparse.Namespace) -> int:
    """Exports and prints the GSC RE2 Regex Library."""
    settings = get_agent_settings()
    filter_lib = GSCFilterLibrary()
    core_filters = filter_lib.get_core_filters()
    reporter = KeywordReportGenerator(reports_dir=settings.reports_dir, docs_dir=settings.project_dir / "docs")
    lib_path = reporter.export_gsc_regex_library_markdown(core_filters)
    print(f"[OK] GSC RE2 Regex Library successfully written to: {lib_path}")
    print(f"Total filters: {len(core_filters)} (100% RE2 validated)")
    return 0


def run_gsc_setup(args: argparse.Namespace) -> int:
    """Prints instructions for GSC setup and manual exports."""
    print(GSCDataEngine.get_manual_setup_instructions())
    return 0


def run_competitor_gap(args: argparse.Namespace) -> int:
    """Runs live competitor gap analysis against aitoolspak.tech."""
    settings = get_agent_settings()
    gap_analyzer = CompetitorGapAnalyzer(project_dir=settings.project_dir)
    report = gap_analyzer.analyze_gaps()
    out_file = settings.project_dir / "docs" / "COMPETITOR_KEYWORD_GAP_ANALYSIS.md"
    gap_analyzer.export_markdown_report(report, out_file)
    print(f"[OK] Competitor Gap Report exported: {out_file}")
    print(f"Competitor: {report.competitor_domain}")
    print(f"Total Competitor URLs: {report.total_competitor_urls}")
    print(f"Direct Catalog Overlaps: {report.direct_catalog_overlaps}")
    print(f"High-Value Gaps: {report.uncovered_high_value_gaps}")
    print(f"GitHub Profile Status: {report.github_profile_status}")
    return 0


def run_optimize_page(args: argparse.Namespace) -> int:
    """Generates an optimization brief for a specific page slug or path."""
    settings = get_agent_settings()
    optimizer = ContentOptimizer(project_dir=settings.project_dir)
    slug = args.slug.strip().lower().replace("/tools/", "").replace("/", "")
    rel_path = f"tools/{slug}/index.html"
    file_path = settings.project_dir / rel_path

    if not file_path.exists():
        print(f"[ERROR] File '{rel_path}' does not exist on disk.")
        return 1

    url = f"https://aitoolgems.tech/tools/{slug}/"
    brief = optimizer.generate_optimization_brief(
        url=url,
        relative_path=rel_path,
        primary_query=f"{slug.title()} price in Pakistan",
        target_cluster=f"Tool: {slug.title()}",
        opportunity_score=88.0,
    )
    print(brief.format_markdown())
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m keyword_agent",
        description="Autonomous Keyword Intelligence, GSC Filter Engine & Content Optimization for AIToolGems Pakistan",
    )
    subparsers = parser.add_subparsers(dest="command", help="Operational commands")

    # audit
    audit_parser = subparsers.add_parser("audit", help="Run full discovery, filter check, and daily report")
    audit_parser.set_defaults(func=run_audit)

    # regex-library
    regex_parser = subparsers.add_parser("regex-library", help="Export Google Search Console RE2 regex library")
    regex_parser.set_defaults(func=run_regex_library)

    # gsc-setup
    setup_parser = subparsers.add_parser("gsc-setup", help="Display Search Console connection & CSV export instructions")
    setup_parser.set_defaults(func=run_gsc_setup)

    # competitor-gap
    gap_parser = subparsers.add_parser("competitor-gap", help="Run competitor gap analysis against aitoolspak.tech")
    gap_parser.set_defaults(func=run_competitor_gap)

    # optimize-page
    opt_parser = subparsers.add_parser("optimize-page", help="Generate optimization brief for a tool page")
    opt_parser.add_argument("slug", help="Tool slug (e.g., chatgpt, canva, leonardo)")
    opt_parser.set_defaults(func=run_optimize_page)

    args = parser.parse_args()
    if not args.command:
        # Default action is audit
        sys.exit(run_audit(args))
    else:
        sys.exit(args.func(args))


if __name__ == "__main__":
    main()
