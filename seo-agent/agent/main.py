#!/usr/bin/env python3
"""
CLI Entry Point for AIToolGems Autonomous SEO Growth Agent
-----------------------------------------------------------
Usage:
  python -m seo-agent.agent.main --mode audit
  python -m seo-agent.agent.main --mode propose
  python -m seo-agent.agent.main --mode pr --live
"""

from __future__ import annotations
import sys
import argparse
import json
from pathlib import Path

# Ensure seo-agent directory is on Python path
CURRENT_DIR = Path(__file__).resolve().parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from agent.orchestrator import GrowthOrchestrator

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AIToolGems Autonomous SEO & AI Search Growth Agent (HERMES)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["audit", "propose", "pr"],
        default="audit",
        help="Operational mode: audit (read-only), propose (local branch patch), pr (create pull request proposal)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom settings.yml configuration file",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Perform live HTTP crawl against https://aitoolgems.tech instead of local repository files",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON summary to stdout",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print the generated Markdown report directly to stdout",
    )
    return parser

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = build_parser()
    args = parser.parse_args()

    orchestrator = GrowthOrchestrator(
        config_path=args.config,
        mode=args.mode,
        live_crawl=args.live,
    )

    result = orchestrator.execute_workflow()

    if args.json:
        print("\n=== JSON SUMMARY ===")
        print(json.dumps(result, indent=2))

    if args.report and result.get("report_path"):
        report_file = Path(result["report_path"])
        if report_file.exists():
            print("\n" + "=" * 60)
            print(report_file.read_text(encoding="utf-8"))
            print("=" * 60 + "\n")

    if result.get("status") == "ABORTED":
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
