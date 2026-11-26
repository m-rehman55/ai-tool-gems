#!/usr/bin/env python3
"""
Enrich all tool pages and homepage with Merchant Listings and Product Snippets schemas:
1. hasMerchantReturnPolicy (7-day replacement warranty in PK)
2. shippingDetails (0 PKR digital delivery in PK)
3. aggregateRating (4.9 / 5.0 with 128 reviews)
4. review (Verified Pakistani Buyer)
5. Storewide hasMerchantReturnPolicy on Organization
"""

import glob
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

WARRANTY_POLICY_PATH = BASE / "config" / "business" / "warranty-policy.json"
if WARRANTY_POLICY_PATH.exists():
    _wp = json.loads(WARRANTY_POLICY_PATH.read_text(encoding="utf-8"))
    SKU_WARRANTY_DAYS = _wp.get("sku_warranty_days", {})
    DEFAULT_WARRANTY_DAYS = _wp.get("default_warranty_days", 7)
else:
    SKU_WARRANTY_DAYS = {}
    DEFAULT_WARRANTY_DAYS = 7


def build_return_policy(days: int) -> dict:
    return {
        "@type": "MerchantReturnPolicy",
        "applicableCountry": "PK",
        "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
        "merchantReturnDays": days,
        "returnMethod": "https://schema.org/ReturnByMail",
        "returnFees": "https://schema.org/FreeReturn"
    }

SHIPPING_DETAILS = {
    "@type": "OfferShippingDetails",
    "shippingRate": {
        "@type": "MonetaryAmount",
        "value": "0",
        "currency": "PKR"
    },
    "shippingDestination": {
        "@type": "DefinedRegion",
        "addressCountry": "PK"
    },
    "deliveryTime": {
        "@type": "ShippingDeliveryTime",
        "handlingTime": {
            "@type": "QuantitativeValue",
            "minValue": 0,
            "maxValue": 1,
            "unitCode": "DAY"
        },
        "transitTime": {
            "@type": "QuantitativeValue",
            "minValue": 0,
            "maxValue": 1,
            "unitCode": "DAY"
        }
    }
}

def enrich_product_node(node: dict, slug: str = ""):
    days = SKU_WARRANTY_DAYS.get(slug, DEFAULT_WARRANTY_DAYS)
    return_policy = build_return_policy(days)

    # Remove synthetic/templated aggregateRating & Review (Google Structured Data Spam Policy)
    agg = node.get("aggregateRating")
    if isinstance(agg, dict) and str(agg.get("reviewCount")) == "128" and str(agg.get("ratingValue")) == "4.9":
        node.pop("aggregateRating", None)

    rev = node.get("review")
    if isinstance(rev, dict) and isinstance(rev.get("author"), dict) and rev["author"].get("name") == "Verified Pakistani Buyer":
        node.pop("review", None)

    offers = node.get("offers")
    if isinstance(offers, dict):
        offers["hasMerchantReturnPolicy"] = return_policy
        if "shippingDetails" not in offers:
            offers["shippingDetails"] = SHIPPING_DETAILS
    elif isinstance(offers, list):
        for off in offers:
            if isinstance(off, dict):
                off["hasMerchantReturnPolicy"] = return_policy
                if "shippingDetails" not in off:
                    off["shippingDetails"] = SHIPPING_DETAILS


def enrich_organization_node(node: dict):
    if "hasMerchantReturnPolicy" not in node:
        node["hasMerchantReturnPolicy"] = build_return_policy(DEFAULT_WARRANTY_DAYS)
    if "paymentAccepted" in node and isinstance(node["paymentAccepted"], str):
        node["paymentAccepted"] = "EasyPaisa, JazzCash, SadaPay, NayaPay, Raast, Bank Transfer, Wise, SWIFT"

def process_file(file_path: Path) -> bool:
    html = file_path.read_text(encoding="utf-8")
    
    # Match JSON-LD block
    m = re.search(r'(<script\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)', html, re.DOTALL)
    if not m:
        return False
        
    prefix, json_str, suffix = m.group(1), m.group(2).strip(), m.group(3)
    try:
        data = json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON in {file_path}: {e}")
        return False
        
    slug = file_path.parent.name if file_path.parent.name != BASE.name else ""
    modified = False
    if isinstance(data, dict):
        if data.get("@type") == "Product":
            enrich_product_node(data, slug)
            modified = True
        elif data.get("@type") == "Organization" or (isinstance(data.get("@type"), list) and "Organization" in data.get("@type")):
            enrich_organization_node(data)
            modified = True
            
        if "@graph" in data and isinstance(data["@graph"], list):
            for node in data["@graph"]:
                if isinstance(node, dict):
                    t = node.get("@type")
                    if t == "Product":
                        enrich_product_node(node, slug)
                        modified = True
                    elif t == "Organization" or (isinstance(t, list) and "Organization" in t):
                        enrich_organization_node(node)
                        modified = True
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                t = item.get("@type")
                if t == "Product":
                    enrich_product_node(item, slug)
                    modified = True
                elif t == "Organization" or (isinstance(t, list) and "Organization" in t):
                    enrich_organization_node(item)
                    modified = True
                
    if modified:
        new_json_str = json.dumps(data, indent=2, ensure_ascii=False)
        new_html = html[:m.start()] + prefix + "\n" + new_json_str + "\n" + suffix + html[m.end():]
        file_path.write_text(new_html, encoding="utf-8")
        return True
    return False

def main():
    # Process all tool pages
    tool_files = sorted(BASE.glob("tools/*/index.html"))
    print(f"Found {len(tool_files)} tool pages.")
    updated_count = 0
    for tf in tool_files:
        if process_file(tf):
            updated_count += 1
            
    # Process index.html
    index_file = BASE / "index.html"
    if index_file.exists():
        if process_file(index_file):
            print("Successfully enriched index.html (homepage).")
            updated_count += 1
            
    print(f"Successfully enriched {updated_count} files with Merchant Listings and Product Snippets schema.")

if __name__ == "__main__":
    main()
