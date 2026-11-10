#!/usr/bin/env python3
"""
Generate Meta Commerce Catalog CSV feed for WhatsApp Business & Facebook Commerce Manager.
Complies with Meta Catalog Feed Specifications (E-commerce / Products).
"""

import csv
import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.sync_prices_and_deals import PRODUCTS
from scripts.directory_tools_data import DIRECTORY_TOOLS

def build_catalog_csv():
    output_files = [
        BASE_DIR / "meta_whatsapp_catalog.csv",
        BASE_DIR / "data" / "merchant" / "meta_whatsapp_catalog.csv"
    ]
    
    rows = []
    
    # Track slugs to prevent duplicates
    seen_slugs = set()
    
    # 1. Process 40 Core Commercial Products
    for p in PRODUCTS:
        slug = p["slug"]
        seen_slugs.add(slug)
        
        name = p["name"]
        provider = p["provider"]
        category = p["category"]
        pkr = p["pkr"]
        usd = p.get("usd", "")
        duration = p.get("duration", "1 Month")
        access = p.get("access", "Private")
        
        # Determine image - using GitHub raw URL from catalog-feed branch for instant CDN access
        png_path = BASE_DIR / "assets" / "product-logos" / f"{slug}.png"
        if png_path.exists():
            image_url = f"https://raw.githubusercontent.com/m-rehman55/ai-tool-gems/catalog-feed/assets/product-logos/{slug}.png"
        else:
            image_url = f"https://aitoolgems.tech/assets/product-logos/{slug}.png"
            
        link = f"https://aitoolgems.tech/tools/{slug}/"
        
        # Build WhatsApp friendly description
        desc = (
            f"{name} ({duration} - {access} Access). "
            f"Official {provider} subscription service in Pakistan. "
            f"Instant activation within 10-15 minutes. "
            f"Features: Premium tools, full access, priority support. "
            f"Price: Rs. {pkr:,} PKR. "
            f"Payment rails: EasyPaisa, JazzCash, SadaPay, Bank Transfer (IBFT), USDT Crypto. "
            f"Verified by AIToolGems (aitoolgems.tech)."
        )
        
        title = f"{name} ({duration} - {access})"
        
        row = {
            "id": f"aitoolgems-{slug}",
            "title": title[:100],  # Meta max 150 chars
            "description": desc[:5000],
            "availability": "in stock",
            "condition": "new",
            "price": f"{pkr} PKR",
            "link": link,
            "image_link": image_url,
            "brand": provider,
            "google_product_category": "Software > Computer Software > Digital Goods & Software",
            "fb_product_category": "electronics > audio > audio players & recorders",  # generic or omit
            "custom_label_0": category,
            "custom_label_1": access,
            "custom_label_2": "Instant Delivery"
        }
        rows.append(row)

    # 2. Process Directory Tools (if not in core products)
    for slug, d in DIRECTORY_TOOLS.items():
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        
        name = d.get("name", slug.title())
        provider = d.get("developer", "AI Provider")
        category = d.get("category", "Software")
        summary = d.get("quick_summary", "")
        
        # Look for price
        pkr_price = "999"
        if "pricing_table" in d and len(d["pricing_table"]) > 1:
            for tier in d["pricing_table"]:
                p_m = re.search(r'Rs\.?\s*([\d,]+)', tier[2])
                if p_m:
                    pkr_price = p_m.group(1).replace(",", "")
                    break
                    
        png_path = BASE_DIR / "assets" / "product-logos" / f"{slug}.png"
        if png_path.exists():
            image_url = f"https://raw.githubusercontent.com/m-rehman55/ai-tool-gems/catalog-feed/assets/product-logos/{slug}.png"
        else:
            image_url = f"https://aitoolgems.tech/assets/product-logos/{slug}.png"
            
        link = f"https://aitoolgems.tech/tools/{slug}/"
        
        desc = (
            f"{name} official software plan in Pakistan. "
            f"{summary} "
            f"Verified features & instant activation. "
            f"Payments: EasyPaisa, JazzCash, SadaPay, Bank Transfer, USDT. "
            f"Order via WhatsApp or website: aitoolgems.tech."
        )
        
        row = {
            "id": f"aitoolgems-{slug}",
            "title": f"{name} Plan in Pakistan"[:100],
            "description": desc[:5000],
            "availability": "in stock",
            "condition": "new",
            "price": f"{pkr_price} PKR",
            "link": link,
            "image_link": image_url,
            "brand": provider.split("(")[0].strip(),
            "google_product_category": "Software > Computer Software > Digital Goods & Software",
            "fb_product_category": "",
            "custom_label_0": category,
            "custom_label_1": "Standard",
            "custom_label_2": "Instant Delivery"
        }
        rows.append(row)

    # CSV headers
    fieldnames = [
        "id", "title", "description", "availability", "condition",
        "price", "link", "image_link", "brand", "google_product_category",
        "custom_label_0", "custom_label_1", "custom_label_2"
    ]
    
    for out_path in output_files:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
                
    print(f"Successfully generated Meta Catalog with {len(rows)} products.")
    for out_path in output_files:
        print(f" -> {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    build_catalog_csv()
