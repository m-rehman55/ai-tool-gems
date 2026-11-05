"""
conversion_agent.__main__ - CLI for Conversion Journey & Trust Architecture Agent.
"""

import sys
import argparse
import json
from pathlib import Path

from conversion_agent.journey_analyzer import CustomerJourneyAnalyzer


def main():
    parser = argparse.ArgumentParser(description="HERMES Agent 14 - Conversion Journey & Trust Architecture")
    subparsers = parser.add_subparsers(dest="command")

    # audit subcommand
    audit_parser = subparsers.add_parser("audit", help="Audit website catalog for conversion journey & trust signals")
    audit_parser.add_argument("--json", action="store_true", help="Output summary in JSON format")

    # page subcommand
    page_parser = subparsers.add_parser("page", help="Analyze specific page for trust & friction")
    page_parser.add_argument("path", help="Relative or absolute path to HTML page")

    args = parser.parse_args()
    analyzer = CustomerJourneyAnalyzer()

    if args.command == "audit":
        results = analyzer.audit_catalog()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("=================================================================")
            print("HERMES AGENT 14 — CONVERSION JOURNEY & TRUST AUDIT")
            print("=================================================================")
            print(f"Total Pages Audited: {results['total_pages_audited']}")
            print(f"Average Journey Score: {results['average_journey_score']}/100")
            print(f"High-Friction Pages: {len(results['high_friction_pages'])}")
            print("-----------------------------------------------------------------")
            for item in results["reports_summary"][:10]:
                print(f"  • {item['identifier']:<30} Overall: {item['overall_score']:<5} Trust: {item['trust_score']:<5} Friction: {item['friction_score']}")
            if len(results["reports_summary"]) > 10:
                print(f"  ... and {len(results['reports_summary']) - 10} more pages.")

    elif args.command == "page":
        file_path = Path(args.path)
        if not file_path.exists():
            print(f"Error: File '{args.path}' not found.")
            sys.exit(1)
        report = analyzer.analyze_file(file_path)
        print("=================================================================")
        print(f"HERMES AGENT 14 — CONVERSION AUDIT FOR: {args.path}")
        print("=================================================================")
        print(f"Overall Journey Readiness Score: {report.overall_readiness_score}/100")
        print(f"Trust Signals Score:             {report.trust_audit.trust_score}/100")
        print(f"Friction / Usability Score:      {report.friction_audit.friction_score}/100")
        print("\nJourney Stage Health:")
        for stage, status in report.journey_stages.items():
            print(f"  • {stage:<25}: {status}")
        print("\nFriction Issues Identified:")
        if not report.friction_audit.issues:
            print("  None. Clean checkout funnel!")
        else:
            for issue in report.friction_audit.issues:
                print(f"  [{issue.severity}] ({issue.category}) {issue.description}")
                print(f"       -> Fix: {issue.remediation}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

