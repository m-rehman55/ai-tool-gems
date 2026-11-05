"""Command-line interface for HERMES Competitor Intelligence Agent (AGENT-11)."""

from __future__ import annotations

import argparse
import json
import sys

from competitor_agent.competitors import get_top_10_competitors
from competitor_agent.pricing_radar import get_pricing_radar_report
from competitor_agent.serp_radar import compute_share_of_voice, get_serp_radar_snapshots
from competitor_agent.snapshots import CompetitorSnapshotManager

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="HERMES Competitor Intelligence & SERP Radar CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("audit", help="Audit Top 10 competitors and Share of Voice")
    subparsers.add_parser("pricing", help="Display comparative tool pricing radar")
    subparsers.add_parser("serp", help="Display SERP ranking radar and competitor overlap")
    subparsers.add_parser("diff", help="Diff current competitor state against previous snapshot")

    args = parser.parse_args()
    mgr = CompetitorSnapshotManager()

    if args.command == "pricing":
        pricing = get_pricing_radar_report()
        print("\n=== PAKISTAN COMPETITIVE PRICING RADAR ===")
        print(f"{'Tool':<26} {'AIToolGems':<12} {'Market Min':<12} {'Market Max':<12} {'Position'}")
        print("-" * 80)
        for p in pricing:
            print(f"{p.tool_name[:25]:<26} Rs. {p.aitoolgems_pkr:<8} Rs. {p.lowest_market_price:<8} Rs. {p.highest_market_price:<8} {p.price_position}")

    elif args.command == "serp":
        radar = get_serp_radar_snapshots()
        sov = compute_share_of_voice()
        print("\n=== PAKISTAN SERP RANKING RADAR ===")
        print(f"{'Query':<42} {'AITG':<6} {'Top Competitor':<20} {'Features'}")
        print("-" * 85)
        for s in radar:
            top_comp = f"{s.top_competitors_ranked[0]['domain']} (#{s.top_competitors_ranked[0]['rank']})" if s.top_competitors_ranked else "None"
            feats = ", ".join(s.serp_features_present)
            print(f"{s.query[:40]:<42} #{str(s.aitoolgems_rank):<5} {top_comp:<20} {feats}")

        print("\nShare of Voice (SOV):")
        for domain, pct in sov["share_of_voice_pct"].items():
            print(f" - {domain:<25} {pct:.1f}%")

    elif args.command == "audit" or not args.command:
        competitors = get_top_10_competitors()
        sov = compute_share_of_voice()
        pricing = get_pricing_radar_report()

        print("\n=== HERMES COMPETITOR RADAR AUDIT ===")
        print(f"Top Competitors Monitored: {len(competitors)}")
        print(f"SERP Market Leader:        {sov['market_leader']}")
        print(f"AIToolGems Share of Voice: {sov['share_of_voice_pct'].get('aitoolgems.tech', 0.0)}%")
        print(f"Price Leader Tools:        {sum(1 for p in pricing if p.price_position == 'PRICE_LEADER')} / {len(pricing)}")
        print("\nTop 5 Monitored Domains:")
        for c in competitors[:5]:
            print(f" • {c.domain:<24} [{c.primary_market}] - {c.access_model}")


if __name__ == "__main__":
    main()
