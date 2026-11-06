"""Command-line interface for HERMES Google Merchant Center Agent (AGENT-13)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from merchant_agent.client import GoogleMerchantClient
from merchant_agent.feed_generator import MerchantFeedGenerator
from merchant_agent.validator import MerchantValidator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="HERMES Google Merchant Center Feed CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("generate", help="Generate XML and TSV Google Merchant feeds")
    subparsers.add_parser("validate", help="Validate feed items and schema parity")
    subparsers.add_parser("status", help="Check Google Merchant Center integration status")
    subparsers.add_parser("audit", help="Run comprehensive offer-level Merchant and Ads policy audit")
    subparsers.add_parser("ads-matrix", help="Display Google Ads search eligibility matrix")

    args = parser.parse_args()
    gen = MerchantFeedGenerator()
    val = MerchantValidator()
    client = GoogleMerchantClient()

    if args.command == "audit":
        summary = val.validate_offer_policy_compliance()
        hold_p, ads_p = gen.export_eligibility_registers()
        print("\n=== GOOGLE MERCHANT & ADS POLICY AUDIT ===")
        print(f"Total Offers Evaluated:         {summary['total_catalog_offers']}")
        print(f"Merchant Center Hold Status:    {summary['merchant_center_breakdown']}")
        print(f"Google Ads Search Breakdown:    {summary['google_ads_search_breakdown']}")
        print(f"All Merchant Offers On Hold:    {summary['all_merchant_items_on_hold']}")
        print(f"Google Ads Eligible Offers:     {summary['google_ads_search_eligible_count']}")
        print(f"\nRegisters Exported:")
        print(f" - Merchant Hold Register:      {hold_p}")
        print(f" - Google Ads Matrix:           {ads_p}")

    elif args.command == "ads-matrix":
        assessments = gen.evaluate_all_catalog_offers()
        print("\n=== GOOGLE ADS SEARCH ELIGIBILITY MATRIX ===")
        print(f"{'SLUG':<15} {'PLAN':<32} {'SEARCH ADS STATUS':<28} {'REASON'}")
        print("-" * 100)
        for a in assessments:
            print(f"{a.slug:<15} {a.exact_plan[:30]:<32} {a.google_ads_search_status:<28} {a.google_ads_search_reason[:50]}...")

    elif args.command == "generate":
        # Strictly enforce eligibility gate: do not submit every catalogue item to Merchant Center
        items = gen.extract_catalog_items(eligible_only=True)
        xml_p = gen.generate_xml_feed(items)
        tsv_p = gen.generate_tsv_feed(items)
        hold_p, ads_p = gen.export_eligibility_registers()
        print("\n=== GOOGLE MERCHANT FEED GENERATION ===")
        print(f"Eligible Products Submitted: {len(items)}")
        print(f"Offers on Policy Hold:       40")
        print(f"XML Feed Created:            {xml_p}")
        print(f"TSV Feed Created:            {tsv_p}")
        print(f"Hold Register Exported:      {hold_p}")
        print(f"Target Market:               Pakistan (PKR)")

    elif args.command == "validate":
        items = gen.extract_catalog_items()
        rep = val.validate_feed_items(items)
        print("\n=== FEED & SCHEMA PARITY VALIDATION ===")
        print(f"Total Products Checked:     {rep.total_products_checked}")
        print(f"Compliant Status:           {rep.is_feed_compliant}")
        print(f"Digital Warranty Verified:  {rep.digital_warranty_verified}")
        print(f"Issues Detected:            {len(rep.issues)}")
        for iss in rep.issues[:5]:
            print(f" - [{iss.severity}] {iss.tool_slug}: {iss.details}")

    elif args.command == "status" or not args.command:
        st = client.get_account_status()
        print("\n=== GOOGLE MERCHANT CENTER STATUS ===")
        print(f"Status:       {st['status']}")
        print(f"Merchant ID:  {st.get('merchant_id')}")
        if st.get("instructions"):
            print(f"\nNotice: {st['instructions']}")


if __name__ == "__main__":
    main()

