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

    args = parser.parse_args()
    gen = MerchantFeedGenerator()
    val = MerchantValidator()
    client = GoogleMerchantClient()

    if args.command == "generate":
        items = gen.extract_catalog_items()
        xml_p = gen.generate_xml_feed(items)
        tsv_p = gen.generate_tsv_feed(items)
        print("\n=== GOOGLE MERCHANT FEED GENERATION ===")
        print(f"Products Extracted: {len(items)}")
        print(f"XML Feed Created:   {xml_p}")
        print(f"TSV Feed Created:   {tsv_p}")
        print(f"Target Market:      Pakistan (PKR)")

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

