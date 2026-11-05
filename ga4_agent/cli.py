"""
cli.py - Command-Line Interface for ga4_agent.

Commands:
- python -m ga4_agent status: Check GA4 property, authorization, measurement ID, and order counts.
- python -m ga4_agent performance: Display Pakistan traffic, channel grouping, and landing pages.
- python -m ga4_agent funnel: View ecommerce conversion funnel (view_item -> begin_checkout -> purchase).
- python -m ga4_agent record-order: Record an offline verified WhatsApp order.
- python -m ga4_agent import-conversions: Dispatch verified purchase conversions to GA4 Measurement Protocol.
- python -m ga4_agent audit: Run full GA4 conversion intelligence audit & export report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Fix Windows cp1252 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from ga4_agent.client import GA4DataClient
from ga4_agent.conversion_importer import ConversionImporter, MEASUREMENT_ID
from ga4_agent.analyzer import GA4Analyzer


def run_status(args: argparse.Namespace) -> int:
    """Checks GA4 configuration and verified order storage."""
    client = GA4DataClient()
    importer = ConversionImporter()
    orders = importer.load_orders()
    pending = sum(1 for o in orders if not o.is_imported_to_ga4)

    print("\n📊 AIToolGems GA4 Analytics & Conversion Intelligence Status")
    print("=" * 65)
    print(f"🆔 Measurement ID:      {MEASUREMENT_ID}")
    print(f"🏢 GA4 Property ID:      {client.property_id or 'Not Set'}")
    print(f"🔑 Live API Authorized:  {'Yes ✅' if client.is_authorized else 'Offline / Baseline 📁'}")
    print(f"📦 Total Verified Orders: {len(orders)} ({pending} pending GA4 import)")
    print(f"💰 Total Verified Revenue:{sum(o.pkr_amount for o in orders):,.0f} PKR")
    print("=" * 65 + "\n")
    return 0


def run_funnel(args: argparse.Namespace) -> int:
    """Displays the ecommerce conversion funnel."""
    analyzer = GA4Analyzer()
    summary = analyzer.run_audit()
    f = summary.funnel

    print("\n🛒 Ecommerce Conversion Funnel (Currency: PKR):")
    print("=" * 65)
    print(f"1. Product Views (view_item):         {f.product_views:>6}")
    print(f"2. Product Selections (select_item):  {f.product_selections:>6}")
    print(f"3. Order Initiations (begin_checkout):{f.order_initiations:>6}")
    print(f"4. Verified Purchases (purchase):      {f.verified_purchases:>6}")
    print("-" * 65)
    print(f"📉 Checkout Drop-Off:                 {f.checkout_dropoff_pct:>5.1f}%")
    print(f"📈 Overall Conversion Rate:           {f.overall_conversion_rate_pct:>5.2f}%")
    print(f"💵 Verified Revenue:             {f.total_revenue_pkr:>10,.0f} PKR")
    print("=" * 65)
    print("ℹ️ Non-Fabrication Rule: Purchases are strictly recorded from verified domestic payments.\n")
    return 0


def run_record_order(args: argparse.Namespace) -> int:
    """Records an offline verified order with domestic payment proof."""
    importer = ConversionImporter()
    ok, msg = importer.record_verified_payment(
        transaction_id=args.tid,
        tool_slug=args.tool,
        tool_name=args.tool.title(),
        pkr_amount=args.amount,
        payment_rail=args.rail,
        raw_phone=args.phone,
    )
    if ok:
        print(f"\n✅ {msg}\n")
        return 0
    else:
        print(f"\n❌ Error: {msg}\n")
        return 1


def run_import_conversions(args: argparse.Namespace) -> int:
    """Dispatches verified purchases to GA4 Measurement Protocol."""
    importer = ConversionImporter()
    res = importer.dispatch_offline_conversions(dry_run=args.dry_run)
    print("\n🚀 GA4 Offline Conversion Dispatch:")
    print("=" * 60)
    print(f"Status:            {res.get('status')}")
    print(f"Imported Count:    {res.get('imported_count')}")
    print(f"Pending Remaining: {res.get('pending_remaining')}")
    print("=" * 60 + "\n")
    return 0


def run_audit(args: argparse.Namespace) -> int:
    """Runs full GA4 conversion intelligence audit."""
    analyzer = GA4Analyzer()
    summary = analyzer.run_audit()

    print("\n📊 Running GA4 Conversion & Ecommerce Audit...")
    print(f"    Property: {summary.property_id} | Pakistan Sessions: {summary.pakistan_sessions}")
    print(f"    Product Views: {summary.funnel.product_views} | Order Initiations: {summary.funnel.order_initiations}")
    print(f"    Verified Purchases: {summary.funnel.verified_purchases} ({summary.funnel.total_revenue_pkr:,.0f} PKR)")
    print(f"    Drop-Off Rate: {summary.funnel.checkout_dropoff_pct}%")

    print("\n💡 Conversion Recommendations:")
    for r in summary.recommendations:
        print(f"    • {r}")
    print()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m ga4_agent",
        description="Autonomous GA4 Analytics & Conversion Intelligence for AIToolGems",
    )
    subparsers = parser.add_subparsers(dest="command", help="Operational commands")

    # status
    p_status = subparsers.add_parser("status", help="Check GA4 setup, authorization, and order counts")
    p_status.set_defaults(func=run_status)

    # funnel
    p_funnel = subparsers.add_parser("funnel", help="View ecommerce conversion funnel")
    p_funnel.set_defaults(func=run_funnel)

    # record-order
    p_record = subparsers.add_parser("record-order", help="Record an offline verified WhatsApp order")
    p_record.add_argument("--tid", required=True, help="Unique Transaction ID (e.g., ATG-20261105-001)")
    p_record.add_argument("--tool", required=True, help="Tool slug (e.g., chatgpt, canva)")
    p_record.add_argument("--amount", type=float, required=True, help="Amount paid in PKR")
    p_record.add_argument("--rail", required=True, help="Payment rail (EasyPaisa, JazzCash, SadaPay, Bank IBFT)")
    p_record.add_argument("--phone", required=True, help="Customer phone number (will be SHA-256 masked)")
    p_record.set_defaults(func=run_record_order)

    # import-conversions
    p_import = subparsers.add_parser("import-conversions", help="Dispatch verified purchases to GA4")
    p_import.add_argument("--dry-run", action="store_true", help="Simulate dispatch without sending HTTP requests")
    p_import.set_defaults(func=run_import_conversions)

    # audit
    p_audit = subparsers.add_parser("audit", help="Run full GA4 conversion intelligence audit")
    p_audit.set_defaults(func=run_audit)

    args = parser.parse_args()
    if not args.command:
        sys.exit(run_status(args))
    else:
        sys.exit(args.func(args))


if __name__ == "__main__":
    main()

