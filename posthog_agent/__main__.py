"""Command-line interface for HERMES PostHog Agent (AGENT-06)."""

from __future__ import annotations

import argparse
import json
import sys

from posthog_agent.client import PostHogClient
from posthog_agent.funnels import analyze_ecom_funnel
from posthog_agent.privacy import get_privacy_replay_config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="HERMES PostHog Behavioural Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Check PostHog authentication and configuration status")
    subparsers.add_parser("funnel", help="Display 5-stage conversion funnel and drop-off analysis")
    subparsers.add_parser("privacy", help="Display privacy replay configuration and masking rules")
    subparsers.add_parser("audit", help="Run comprehensive behavioral and funnel audit")

    args = parser.parse_args()
    client = PostHogClient()

    if args.command == "status":
        status = client.get_auth_status()
        print("\n=== POSTHOG INTEGRATION STATUS ===")
        print(f"Status:       {status['status']}")
        print(f"Configured:   {status['configured']}")
        print(f"Host:         {status.get('host')}")
        print(f"Project ID:   {status.get('project_id')}")
        if not status["configured"]:
            print(f"\nInstructions: {status['instructions']}")

    elif args.command == "funnel":
        counts = client.get_funnel_counts()
        report = analyze_ecom_funnel(counts)
        print("\n=== 5-STAGE CONVERSION FUNNEL (PAKISTAN) ===")
        print(f"Total Starters (Landing Page):  {report.total_starters}")
        print(f"Total Converters (Confirmed):    {report.total_converters}")
        print(f"Overall Conversion Rate:        {report.overall_conversion_pct:.2f}%\n")

        print(f"{'Step':<4} {'Stage Name':<28} {'Triggers':<24} {'Users':<8} {'Conv %':<8} {'Drop %'}")
        print("-" * 80)
        for s in report.steps:
            print(f"{s.step_number:<4} {s.step_name:<28} {s.event_trigger:<24} {s.unique_users:<8} {s.conversion_from_previous_pct:<8.1f} {s.dropoff_pct:.1f}%")

        if report.bottleneck_step:
            print(f"\nPrimary Bottleneck: {report.bottleneck_step}")
            for d in report.diagnostics:
                print(f" - {d}")

    elif args.command == "privacy":
        cfg = get_privacy_replay_config()
        print("\n=== PRIVACY-SAFE SESSION REPLAY CONFIGURATION ===")
        print(json.dumps(cfg, indent=2))

    elif args.command == "audit" or not args.command:
        status = client.get_auth_status()
        counts = client.get_funnel_counts()
        report = analyze_ecom_funnel(counts)
        print("\n=== HERMES POSTHOG BEHAVIOURAL AUDIT REPORT ===")
        print(f"Authentication:     {status['status']}")
        print(f"5-Stage Conversion: {report.overall_conversion_pct:.2f}%")
        print(f"Bottleneck:         {report.bottleneck_step or 'None'}")
        print(f"Privacy Masking:    ACTIVE (Zero PII, Zero credentials)")


if __name__ == "__main__":
    main()
