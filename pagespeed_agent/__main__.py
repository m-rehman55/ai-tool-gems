"""Command-line interface for HERMES PageSpeed & Core Web Vitals Agent (AGENT-07)."""

from __future__ import annotations

import argparse
import json
import sys

from pagespeed_agent.client import PageSpeedClient
from pagespeed_agent.regression_detector import detect_regressions
from pagespeed_agent.representative_urls import REPRESENTATIVE_TEMPLATES

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="HERMES PageSpeed Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    audit_parser = subparsers.add_parser("audit", help="Audit specific URL performance")
    audit_parser.add_argument("--url", default="https://aitoolgems.tech/", help="Target URL to audit")
    audit_parser.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile", help="Audit strategy")

    subparsers.add_parser("benchmark", help="Benchmark all representative site templates")
    subparsers.add_parser("history", help="View historical audit runs")

    args = parser.parse_args()
    client = PageSpeedClient()

    if args.command == "benchmark":
        print("\n=== BENCHMARKING ALL REPRESENTATIVE TEMPLATES ===")
        print(f"{'Template':<18} {'Strategy':<8} {'Score':<6} {'LCP':<10} {'TBT':<8} {'CLS':<8} {'Source'}")
        print("-" * 80)
        for t in REPRESENTATIVE_TEMPLATES:
            for s in ["mobile", "desktop"]:
                res = client.audit_url(t["url"], strategy=s)
                lab = res.lab_data
                print(f"{t['template_id']:<18} {s:<8} {lab.performance_score:<6.0f} {lab.lcp_ms:<10.0f} {lab.tbt_ms:<8.0f} {lab.cls:<8.3f} {res.data_source[:18]}")

    elif args.command == "history":
        history = client._load_history()
        print(f"\n=== AUDIT HISTORY ({len(history)} records) ===")
        for h in history[-10:]:
            lab = h.get("lab_data", {})
            print(f"- {h.get('url')} [{h.get('strategy')}]: Score {lab.get('performance_score')} | LCP {lab.get('lcp_ms')}ms | Source: {h.get('data_source')}")

    elif args.command == "audit" or not args.command:
        url = getattr(args, "url", "https://aitoolgems.tech/")
        strategy = getattr(args, "strategy", "mobile")
        res = client.audit_url(url, strategy=strategy)
        lab = res.lab_data
        field_d = res.field_data
        evaluation = detect_regressions(res)

        print(f"\n=== PAGESPEED AUDIT REPORT ({strategy.upper()}) ===")
        print(f"URL:          {res.url}")
        print(f"Data Source:  {res.data_source}")
        print(f"Perf Score:   {lab.performance_score:.0f} / 100")
        print("\nCore Web Vitals (Lab):")
        print(f" - LCP:         {lab.lcp_ms:.0f} ms [{lab.lcp_rating.value}]")
        print(f" - TBT:         {lab.tbt_ms:.0f} ms [{lab.tbt_rating.value}]")
        print(f" - CLS:         {lab.cls:.3f} [{lab.cls_rating.value}]")
        print(f" - FCP:         {lab.fcp_ms:.0f} ms [{lab.fcp_rating.value}]")
        print(f" - Speed Index: {lab.speed_index_ms:.0f} ms [{lab.speed_index_rating.value}]")
        print(f" - TTFB:        {lab.ttfb_ms:.0f} ms [{lab.ttfb_rating.value}]")

        print("\nReal-User Field Data (CrUX):")
        if field_d.has_data:
            print(f" - Field LCP:   {field_d.lcp_ms} ms [{field_d.lcp_rating.value}]")
            print(f" - Field INP:   {field_d.inp_ms} ms [{field_d.inp_rating.value}]")
            print(f" - Field CLS:   {field_d.cls} [{field_d.cls_rating.value}]")
        else:
            print(" - Field data not yet available for this URL in CrUX 28-day aggregation.")

        print("\nAdvisory Recommendations:")
        for r in evaluation.recommendations:
            print(f" • {r}")


if __name__ == "__main__":
    main()

