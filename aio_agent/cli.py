"""
cli.py - Command Line Interface for AIO Agent.
Executes Google AI Overviews grounding audits, query fan-out checks, and llms.txt synchronization.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aio_agent.extractability import ExtractabilityAuditor
from aio_agent.query_fanout import QueryFanOutAnalyzer
from aio_agent.grounding_scorer import GroundingScorer
from aio_agent.llms_sync import LLMsSyncEngine
from aio_agent.ai_visibility import AIVisibilityTracker
from aio_agent.answer_readiness import AnswerReadinessEvaluator


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m aio_agent",
        description="AIO Agent - Google AI Overviews & Generative Search Grounding Engine",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Audit
    audit_parser = subparsers.add_parser("audit", help="Run site-wide AIO grounding and fan-out audit")
    audit_parser.add_argument("--json", action="store_true", help="Output raw JSON format")

    # 2. Score
    score_parser = subparsers.add_parser("score", help="Score a single page for AI Overviews readiness")
    score_parser.add_argument("path", help="Relative or absolute path to HTML file")

    # 3. Sync LLMs
    subparsers.add_parser("sync-llms", help="Synchronize llms.txt and llms-full.txt with live routes")

    # 4. Fan-out
    fanout_parser = subparsers.add_parser("fan-out", help="Check Query Fan-Out intent coverage for a page")
    fanout_parser.add_argument("path", help="Relative or absolute path to HTML file")

    # 5. AI Search Visibility
    subparsers.add_parser("visibility", help="Track verified search visibility and citations across AI platforms")

    # 6. Answer Readiness (11 GEO Criteria)
    readiness_parser = subparsers.add_parser("readiness", help="Evaluate 11 on-page direct answer readiness criteria")
    readiness_parser.add_argument("path", help="Relative or absolute path to HTML file")

    parsed = parser.parse_args(args)
    project_dir = Path.cwd()

    if parsed.command == "audit":
        scorer = GroundingScorer(project_dir)
        res = scorer.audit_entire_site()
        if parsed.json:
            print(json.dumps(res, indent=2))
        else:
            print("=" * 65)
            print("[AIO AGENT] Google AI Overviews & Grounding Audit")
            print("=" * 65)
            print(f"Total Pages Audited:    {res['total_pages_audited']}")
            print(f"Average AIO Score:      {res['average_aio_score']} / 100")
            print(f"Elite AIO Ready (>=90): {res['elite_aio_ready']}")
            print(f"AIO Compliant (75-89):  {res['aio_compliant']}")
            print(f"Needs Optimization:     {res['needs_optimization']}")
            print("-" * 65)
            if res["needs_optimization"] == 0:
                print("[OK] 100% of site is fully compliant for Google AI Overviews citation.")
            else:
                print(f"[WARN] {res['needs_optimization']} pages need quick answer or fan-out optimization.")
            print("=" * 65)
        return 0

    elif parsed.command == "score":
        target = Path(parsed.path)
        if not target.is_absolute():
            target = project_dir / target
        if not target.exists():
            print(f"Error: File not found at {target}", file=sys.stderr)
            return 1

        scorer = GroundingScorer(project_dir)
        score_res = scorer.score_page(target)
        print("=" * 65)
        print(f"Page: {score_res.url_slug}")
        print("=" * 65)
        print(f"* Total AIO Score:        {score_res.total_aio_score} / 100 ({score_res.tier})")
        print(f"* Extractability (35%):   {score_res.extractability_score}")
        print(f"* Query Fan-Out (35%):    {score_res.fanout_score}")
        print(f"* Schema Markup (15%):    {score_res.schema_score}")
        print(f"* Information Gain (15%): {score_res.information_gain_score}")
        if score_res.recommendations:
            print("-" * 65)
            print("Actionable Recommendations:")
            for r in score_res.recommendations:
                print(f"  * {r}")
        print("=" * 65)
        return 0

    elif parsed.command == "sync-llms":
        engine = LLMsSyncEngine(project_dir)
        sync_res = engine.sync()
        print("=" * 65)
        print("[AIO] Knowledge Base Synchronizer")
        print("=" * 65)
        print(f"* Tools Discovered:       {sync_res.tools_synced}")
        print(f"* Guides Discovered:      {sync_res.guides_synced}")
        print(f"* llms.txt Updated:       {sync_res.llms_txt_updated}")
        print(f"* llms-full.txt Updated:  {sync_res.llms_full_txt_updated}")
        print(f"* Result:                 {sync_res.message}")
        print("=" * 65)
        return 0

    elif parsed.command == "fan-out":
        target = Path(parsed.path)
        if not target.is_absolute():
            target = project_dir / target
        if not target.exists():
            print(f"Error: File not found at {target}", file=sys.stderr)
            return 1

        analyzer = QueryFanOutAnalyzer()
        res = analyzer.analyze_file(target)
        print("=" * 65)
        print(f"Query Fan-Out Coverage: {res.url_slug} ({res.coverage_percentage}%)")
        print("=" * 65)
        for name, branch in res.branches.items():
            status = "[PASS] SATISFIED" if branch.is_satisfied else "[FAIL] MISSING"
            print(f"* {branch.description}: {status}")
            if branch.matched_snippet:
                print(f"  Snippet: \"{branch.matched_snippet}\"")
        print("=" * 65)
        return 0

    elif parsed.command == "visibility":
        tracker = AIVisibilityTracker()
        summary = tracker.compute_visibility_summary()
        status = tracker.get_provider_status()
        print("=" * 65)
        print("[AIO AGENT] AI Search Platform Visibility and Citations")
        print("=" * 65)
        print(f"Provider Status:           {status['status']}")
        print(f"Evidence Registry:         {summary.evidence_status}")
        print(f"Total Queries Audited:     {summary.total_queries_audited}")
        print(f"Brand Mention Rate:        {summary.brand_mention_rate_pct}%")
        print(f"Citation Frequency:        {summary.citation_frequency_pct}%")
        print(f"Pakistan Visibility Score: {summary.pakistan_visibility_score} / 100")
        print("-" * 65)
        print("Top Cited URLs:")
        for u in summary.top_cited_urls:
            print(f"  * {u['url']} ({u['citations']} citations)")
        print("=" * 65)
        return 0

    elif parsed.command == "readiness":
        target = Path(parsed.path)
        if not target.is_absolute():
            target = project_dir / target
        if not target.exists():
            print(f"Error: File not found at {target}", file=sys.stderr)
            return 1
        evaluator = AnswerReadinessEvaluator()
        rep = evaluator.evaluate_file(target)
        print("=" * 65)
        print(f"AEO/GEO Answer Readiness: {rep.url_slug} ({rep.total_score:.1f}/100 [{rep.grade}])")
        print("=" * 65)
        for c in rep.criteria:
            res_str = "[PASS]" if c.passed else "[FAIL]"
            print(f"{res_str} {c.name:<28} ({c.score:.1f}/{c.weight:.1f} pts)")
            print(f"     Evidence: {c.evidence}")
        if rep.recommendations:
            print("-" * 65)
            print("Advisory Recommendations:")
            for r in rep.recommendations:
                print(f"  • {r}")
        print("=" * 65)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
