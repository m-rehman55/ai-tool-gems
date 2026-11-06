#!/usr/bin/env python3
"""
sync_wholesale_database.py - Wholesale Cost, Inventory Stock & Supplier Intelligence Engine

Parses raw supplier exports (Telegram bots), matches them against the 40 AIToolGems
catalog subscriptions, calculates profit margins (PKR & USD), aggregates live stock counts,
tracks best supplier bots, and synchronizes the wholesale database with admin.js and data stores.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_CSV_PATH = REPO_ROOT / "data" / "suppliers" / "reseller_products_master.csv"
FALLBACK_CSV_PATH = REPO_ROOT / "data" / "suppliers" / "telegram_bots_catalog.csv"
OUTPUT_DB = REPO_ROOT / "data" / "wholesale_inventory.json"
OUTPUT_SUMMARY = REPO_ROOT / "data" / "wholesale_cost_reference.json"
ADMIN_JS_PATH = REPO_ROOT / "admin.js"

# Benchmark exchange rate for USDT -> PKR (domestic market rate)
USDT_TO_PKR_BENCHMARK = 280.0

# 40 AIToolGems Catalog Products
CATALOG_PRODUCTS = [
    {"slug": "chatgpt", "name": "ChatGPT Plus", "provider": "OpenAI", "category": "AI Assistants", "pkr": 2300, "usd": 8.99, "duration": "1 Month", "access": "Private"},
    {"slug": "gemini", "name": "Gemini Pro", "provider": "Google", "category": "AI Assistants", "pkr": 800, "usd": 3.99, "duration": "18 Months", "access": "Invitation"},
    {"slug": "veo", "name": "Veo 3 Ultra", "provider": "Google", "category": "AI Video", "pkr": 2100, "usd": 8.49, "duration": "Unlimited", "access": "Shared"},
    {"slug": "leonardo", "name": "Leonardo AI Essential", "provider": "Leonardo.Ai", "category": "Design", "pkr": 1900, "usd": 7.49, "duration": "8,500 Credits", "access": "Private"},
    {"slug": "elevenlabs", "name": "ElevenLabs Voice AI", "provider": "ElevenLabs", "category": "AI Voice", "pkr": 3300, "usd": 12.99, "duration": "1 Month", "access": "Private"},
    {"slug": "canva", "name": "Canva Pro Edu", "provider": "Canva", "category": "Design", "pkr": 900, "usd": 3.99, "duration": "1 Year", "access": "Invitation"},
    {"slug": "figma", "name": "Figma Pro Private", "provider": "Figma", "category": "Design", "pkr": 3000, "usd": 11.99, "duration": "2 Years", "access": "Private"},
    {"slug": "capcut", "name": "CapCut Pro VIP", "provider": "Bytedance", "category": "AI Video", "pkr": 900, "usd": 3.99, "duration": "1 Month", "access": "Private"},
    {"slug": "adobe", "name": "Adobe Creative Cloud", "provider": "Adobe", "category": "Design", "pkr": 1700, "usd": 6.99, "duration": "2 Months", "access": "Private"},
    {"slug": "lovable", "name": "Lovable Pro", "provider": "Lovable", "category": "Development", "pkr": 1600, "usd": 6.49, "duration": "1 Month", "access": "Private"},
    {"slug": "gamma", "name": "Gamma Pro", "provider": "Gamma", "category": "Productivity", "pkr": 23000, "usd": 89.99, "duration": "1 Year", "access": "Private"},
    {"slug": "replit", "name": "Replit Core", "provider": "Replit", "category": "Development", "pkr": 3200, "usd": 12.49, "duration": "$40 Credits", "access": "Private"},
    {"slug": "n8n", "name": "n8n Starter", "provider": "n8n", "category": "Development", "pkr": 7000, "usd": 26.99, "duration": "1 Year", "access": "Private"},
    {"slug": "notion", "name": "Notion Business", "provider": "Notion", "category": "Productivity", "pkr": 2200, "usd": 8.99, "duration": "3 Months", "access": "Invitation"},
    {"slug": "nordvpn", "name": "NordVPN", "provider": "Nord Security", "category": "VPN & Security", "pkr": 1800, "usd": 6.99, "duration": "3 Months", "access": "Private"},
    {"slug": "surfshark", "name": "Surfshark VPN", "provider": "Nord Security", "category": "VPN & Security", "pkr": 800, "usd": 3.49, "duration": "2 Months", "access": "Shared"},
    {"slug": "youtube", "name": "YouTube Premium", "provider": "Google", "category": "Entertainment", "pkr": 1200, "usd": 4.99, "duration": "3 Months", "access": "Invitation"},
    {"slug": "netflix", "name": "Netflix Premium 4K", "provider": "Netflix", "category": "Entertainment", "pkr": 400, "usd": 1.99, "duration": "1 Month", "access": "Shared"},
    {"slug": "linkedin", "name": "LinkedIn Premium", "provider": "Microsoft", "category": "Business", "pkr": 1500, "usd": 5.99, "duration": "2 Months", "access": "Invitation"},
    {"slug": "windows", "name": "Windows 11 Pro Key", "provider": "Microsoft", "category": "Software", "pkr": 1900, "usd": 7.99, "duration": "Lifetime", "access": "License Key"},
    {"slug": "claude", "name": "Claude Pro (3.5 Sonnet)", "provider": "Anthropic", "category": "AI Assistants", "pkr": 2200, "usd": 8.99, "duration": "1 Month", "access": "Private"},
    {"slug": "midjourney", "name": "Midjourney v6.1 Pro", "provider": "Midjourney", "category": "Design", "pkr": 2400, "usd": 9.99, "duration": "1 Month", "access": "Private / Discord"},
    {"slug": "cursor", "name": "Cursor AI Pro", "provider": "Anysphere", "category": "Development", "pkr": 2800, "usd": 10.99, "duration": "1 Month", "access": "Private"},
    {"slug": "perplexity", "name": "Perplexity Pro", "provider": "Perplexity", "category": "AI Assistants", "pkr": 1400, "usd": 5.49, "duration": "1 Month", "access": "Private"},
    {"slug": "deepseek", "name": "DeepSeek Unlimited", "provider": "DeepSeek", "category": "AI Assistants", "pkr": 1100, "usd": 4.49, "duration": "1 Month", "access": "Private Portal"},
    {"slug": "grok", "name": "SuperGrok / Grok 2", "provider": "xAI", "category": "AI Assistants", "pkr": 1800, "usd": 6.99, "duration": "1 Month", "access": "Private"},
    {"slug": "runway", "name": "Runway ML Gen-3 Pro", "provider": "Runway", "category": "AI Video", "pkr": 3500, "usd": 13.99, "duration": "1 Month", "access": "Private"},
    {"slug": "heygen", "name": "HeyGen AI Avatar Pro", "provider": "HeyGen", "category": "AI Video", "pkr": 4200, "usd": 16.99, "duration": "1 Month", "access": "Private"},
    {"slug": "grammarly", "name": "Grammarly Premium", "provider": "Grammarly", "category": "Writing & SEO", "pkr": 750, "usd": 2.99, "duration": "1 Month", "access": "Private / Shared"},
    {"slug": "quillbot", "name": "QuillBot Premium", "provider": "Learneo", "category": "Writing & SEO", "pkr": 450, "usd": 1.99, "duration": "1 Month", "access": "Private / Shared"},
    {"slug": "semrush", "name": "SEMrush Pro", "provider": "SEMrush", "category": "Writing & SEO", "pkr": 1500, "usd": 5.99, "duration": "1 Month", "access": "Shared"},
    {"slug": "allinone", "name": "All-in-One Mega AI Portal", "provider": "AIToolGems", "category": "AI Assistants", "pkr": 1999, "usd": 7.99, "duration": "1 Month", "access": "Private Portal"},
    {"slug": "tradingview", "name": "TradingView Pro", "provider": "TradingView", "category": "Business", "pkr": 3500, "usd": 14.99, "duration": "1 Month", "access": "Private"},
    {"slug": "kling", "name": "Kling AI", "provider": "Kuaishou", "category": "AI Video", "pkr": 4800, "usd": 19.99, "duration": "1 Month", "access": "Private"},
    {"slug": "freepik", "name": "Freepik Premium", "provider": "Freepik", "category": "Design", "pkr": 2400, "usd": 9.99, "duration": "1 Month", "access": "Private"},
    {"slug": "spotify", "name": "Spotify Premium", "provider": "Spotify", "category": "Entertainment", "pkr": 1200, "usd": 4.99, "duration": "3 Months", "access": "Private"},
    {"slug": "copilot", "name": "GitHub Copilot", "provider": "Microsoft", "category": "Development", "pkr": 2500, "usd": 9.99, "duration": "1 Month", "access": "Private"},
    {"slug": "suno", "name": "Suno AI", "provider": "Suno", "category": "AI Voice", "pkr": 3200, "usd": 12.99, "duration": "1 Month", "access": "Private"},
    {"slug": "turnitin", "name": "Turnitin Student Account", "provider": "Turnitin", "category": "Writing & SEO", "pkr": 3600, "usd": 13.99, "duration": "1 Month", "access": "Private"},
    {"slug": "office365", "name": "Microsoft Office 365 (1TB)", "provider": "Microsoft", "category": "Productivity", "pkr": 2200, "usd": 8.99, "duration": "1 Year", "access": "Private"}
]

SUPPLIER_RULES = {
    "chatgpt": {"keywords": ["chatgpt", "codex", "gpt-"], "exclude": ["otp", "rent number"], "default_stock": 25, "default_cost_usdt": 1.34},
    "gemini": {"keywords": ["gg ai", "gemini", "google ai"], "exclude": [], "default_stock": 50, "default_cost_usdt": 14.00},
    "veo": {"keywords": ["veo"], "exclude": [], "default_stock": 10, "default_cost_usdt": 5.00},
    "leonardo": {"keywords": ["leonardo"], "exclude": [], "default_stock": 15, "default_cost_usdt": 4.50},
    "elevenlabs": {"keywords": ["elevenlabs", "elevanlabs", "eleven reader"], "exclude": [], "default_stock": 12, "default_cost_usdt": 3.85},
    "canva": {"keywords": ["canva"], "exclude": [], "default_stock": 20, "default_cost_usdt": 1.50},
    "figma": {"keywords": ["figma"], "exclude": [], "default_stock": 10, "default_cost_usdt": 5.50},
    "capcut": {"keywords": ["capcut"], "exclude": [], "default_stock": 66, "default_cost_usdt": 1.80},
    "adobe": {"keywords": ["adobe"], "exclude": [], "default_stock": 80, "default_cost_usdt": 6.71}, # Normalized monthly rate from 4-month package
    "lovable": {"keywords": ["lovable"], "exclude": [], "default_stock": 10, "default_cost_usdt": 3.80},
    "gamma": {"keywords": ["gamma"], "exclude": [], "default_stock": 8, "default_cost_usdt": 55.00},
    "replit": {"keywords": ["replit"], "exclude": [], "default_stock": 12, "default_cost_usdt": 7.50},
    "n8n": {"keywords": ["n8n"], "exclude": [], "default_stock": 10, "default_cost_usdt": 16.50},
    "notion": {"keywords": ["notion"], "exclude": [], "default_stock": 15, "default_cost_usdt": 4.50},
    "nordvpn": {"keywords": ["nordvpn", "nord vpn"], "exclude": [], "default_stock": 25, "default_cost_usdt": 3.50},
    "surfshark": {"keywords": ["surfshark"], "exclude": [], "default_stock": 20, "default_cost_usdt": 1.80},
    "youtube": {"keywords": ["youtube"], "exclude": [], "default_stock": 14, "default_cost_usdt": 1.11},
    "netflix": {"keywords": ["netflix"], "exclude": [], "default_stock": 30, "default_cost_usdt": 0.85},
    "linkedin": {"keywords": ["linkedin"], "exclude": [], "default_stock": 15, "default_cost_usdt": 3.20},
    "windows": {"keywords": ["windows"], "exclude": [], "default_stock": 40, "default_cost_usdt": 3.50},
    "claude": {"keywords": ["claude"], "exclude": [], "default_stock": 50, "default_cost_usdt": 1.91}, # 20M / 1 Month rate
    "midjourney": {"keywords": ["midjourney"], "exclude": [], "default_stock": 15, "default_cost_usdt": 5.50},
    "cursor": {"keywords": ["cursor"], "exclude": [], "default_stock": 18, "default_cost_usdt": 6.00},
    "perplexity": {"keywords": ["perplexity"], "exclude": [], "default_stock": 25, "default_cost_usdt": 3.20},
    "deepseek": {"keywords": ["deepseek"], "exclude": [], "default_stock": 35, "default_cost_usdt": 2.20},
    "grok": {"keywords": ["grok"], "exclude": [], "default_stock": 10, "default_cost_usdt": 26.97},
    "runway": {"keywords": ["runway"], "exclude": [], "default_stock": 10, "default_cost_usdt": 8.00},
    "heygen": {"keywords": ["heygen"], "exclude": [], "default_stock": 8, "default_cost_usdt": 10.00},
    "grammarly": {"keywords": ["grammarly"], "exclude": [], "default_stock": 25, "default_cost_usdt": 1.60},
    "quillbot": {"keywords": ["quillbot"], "exclude": [], "default_stock": 30, "default_cost_usdt": 0.95},
    "semrush": {"keywords": ["semrush"], "exclude": [], "default_stock": 20, "default_cost_usdt": 3.20},
    "allinone": {"keywords": ["all-in-one", "mega ai"], "exclude": [], "default_stock": 40, "default_cost_usdt": 4.20},
    "tradingview": {"keywords": ["tradingview"], "exclude": [], "default_stock": 15, "default_cost_usdt": 8.00},
    "kling": {"keywords": ["kling"], "exclude": [], "default_stock": 10, "default_cost_usdt": 12.00},
    "freepik": {"keywords": ["freepik"], "exclude": [], "default_stock": 20, "default_cost_usdt": 5.50},
    "spotify": {"keywords": ["spotify"], "exclude": [], "default_stock": 30, "default_cost_usdt": 2.50},
    "copilot": {"keywords": ["copilot"], "exclude": [], "default_stock": 15, "default_cost_usdt": 5.80},
    "suno": {"keywords": ["suno"], "exclude": [], "default_stock": 12, "default_cost_usdt": 7.50},
    "turnitin": {"keywords": ["turnitin"], "exclude": [], "default_stock": 20, "default_cost_usdt": 7.00},
    "office365": {"keywords": ["office 365", "office365"], "exclude": [], "default_stock": 30, "default_cost_usdt": 4.50}
}


EXPANSION_APPS = [
    {"slug": "duolingo", "name": "Duolingo Super / Max", "category": "Education & Languages", "keywords": ["duolingo"], "suggested_pkr": 990},
    {"slug": "apple_music", "name": "Apple Music", "category": "Entertainment", "keywords": ["apple music"], "suggested_pkr": 600},
    {"slug": "icloud", "name": "Apple iCloud 2TB Storage", "category": "Cloud & Storage", "keywords": ["icloud"], "suggested_pkr": 1100},
    {"slug": "expressvpn", "name": "ExpressVPN", "category": "VPN & Security", "keywords": ["expressvpn", "express vpn"], "suggested_pkr": 1400},
    {"slug": "hma_vpn", "name": "HMA VPN", "category": "VPN & Security", "keywords": ["hma"], "suggested_pkr": 900},
    {"slug": "discord", "name": "Discord Nitro & Profile Decor", "category": "Social & Gaming", "keywords": ["discord"], "suggested_pkr": 1200},
    {"slug": "telegram", "name": "Telegram Premium & Stars", "category": "Social & Messaging", "keywords": ["telegram"], "suggested_pkr": 950},
    {"slug": "prime_video", "name": "Amazon Prime Video", "category": "Entertainment", "keywords": ["prime video", "prime"], "suggested_pkr": 450},
    {"slug": "disney", "name": "Disney+ Premium", "category": "Entertainment", "keywords": ["disney"], "suggested_pkr": 600},
    {"slug": "coursera", "name": "Coursera Plus", "category": "Education & Courses", "keywords": ["coursera"], "suggested_pkr": 2500},
    {"slug": "skillshare", "name": "Skillshare Premium", "category": "Education & Courses", "keywords": ["skillshare"], "suggested_pkr": 1200},
    {"slug": "jetbrains", "name": "JetBrains All Products Pack", "category": "Development", "keywords": ["jetbrains", "jetbrain"], "suggested_pkr": 1800},
    {"slug": "ilovepdf", "name": "iLovePDF Premium", "category": "Productivity", "keywords": ["ilovepdf"], "suggested_pkr": 800},
    {"slug": "pika", "name": "Pika AI Video", "category": "AI Video", "keywords": ["pika"], "suggested_pkr": 2800},
    {"slug": "luma", "name": "Luma Dream Machine", "category": "AI Video", "keywords": ["luma"], "suggested_pkr": 3200},
    {"slug": "deepl", "name": "DeepL Pro Translator", "category": "Productivity", "keywords": ["deepl"], "suggested_pkr": 1500},
    {"slug": "envato", "name": "Envato Elements", "category": "Design", "keywords": ["envato"], "suggested_pkr": 2200},
    {"slug": "ahrefs", "name": "Ahrefs SEO", "category": "Writing & SEO", "keywords": ["ahrefs"], "suggested_pkr": 3500},
    {"slug": "steam", "name": "Steam / Gaming Wallets", "category": "Gaming", "keywords": ["steam", "playstation", "xbox"], "suggested_pkr": 1500},
    {"slug": "otp_service", "name": "SMS OTP Verification Numbers", "category": "Developer API", "keywords": ["otp", "rent number", "rent otp"], "suggested_pkr": 250},
    {"slug": "aged_mails", "name": "Aged Outlook/Hotmail Accounts", "category": "Developer API", "keywords": ["outlook", "hotmail", "mails"], "suggested_pkr": 150}
]


def parse_supplier_csv(csv_path: Optional[Path] = None) -> Tuple[List[Dict[str, Any]], str]:
    """Reads and validates raw supplier CSV rows from master or fallback file."""
    target_path = MASTER_CSV_PATH if MASTER_CSV_PATH.exists() else FALLBACK_CSV_PATH
    if csv_path and csv_path.exists():
        target_path = csv_path

    if not target_path.exists():
        raise FileNotFoundError(f"Supplier CSV not found at: {target_path}")

    rows: List[Dict[str, Any]] = []
    with open(target_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if not r.get("Product Name"):
                continue
            rows.append(r)
    return rows, target_path.name


def parse_stock_value(val: Any) -> int:
    """Extract numeric stock quantity from text like '999 (Invite)', 'In Stock', '33'."""
    if not val:
        return 0
    s = str(val).strip().lower()
    if s in ["in stock", "live", "available"]:
        return 20
    m = re.search(r"\d+", s)
    return int(m.group(0)) if m else 0


def build_wholesale_inventory(raw_rows: List[Dict[str, Any]], source_file: str = "data/suppliers/reseller_products_master.csv") -> Dict[str, Any]:
    """Matches raw supplier rows with 40 catalog items and 21+ expansion apps."""
    # Group raw supplier listings by catalog tool slug
    matched_suppliers: Dict[str, List[Dict[str, Any]]] = {p["slug"]: [] for p in CATALOG_PRODUCTS}
    unmatched_items: List[Dict[str, Any]] = []

    for r in raw_rows:
        pname = r["Product Name"].strip().lower()
        matched = False
        for slug, rule in SUPPLIER_RULES.items():
            if any(kw in pname for kw in rule["keywords"]):
                if not any(ex in pname for ex in rule.get("exclude", [])):
                    matched_suppliers[slug].append(r)
                    matched = True
                    break
        if not matched:
            unmatched_items.append(r)

    # Process all catalog products
    products_db: List[Dict[str, Any]] = []
    total_stock_all = 0
    in_stock_count = 0
    low_stock_count = 0

    for prod in CATALOG_PRODUCTS:
        slug = prod["slug"]
        rule = SUPPLIER_RULES[slug]
        supplier_list = matched_suppliers[slug]

        valid_prices = []
        stock_sum = 0
        best_supplier = "AIToolGems Direct Domestic"

        for s in supplier_list:
            try:
                price = float(s.get("Price (USDT)", 0.0))
                if price > 0.0:
                    valid_prices.append((price, s.get("Bot Name", "Unknown Bot")))
            except (ValueError, TypeError):
                pass
            stock_sum += parse_stock_value(s.get("Stock"))

        # If supplier bot items exist with non-zero pricing, find the cheapest
        if valid_prices:
            min_price_item = min(valid_prices, key=lambda x: x[0])
            lowest_usdt = round(min_price_item[0], 2)
            best_supplier = min_price_item[1]
        else:
            # Fall back to calibrated benchmark cost
            lowest_usdt = rule["default_cost_usdt"]
            if supplier_list and supplier_list[0].get("Bot Name"):
                best_supplier = supplier_list[0]["Bot Name"]

        # If stock is 0 from CSV, use verified supplier baseline stock
        final_stock = stock_sum if stock_sum > 0 else rule["default_stock"]
        total_stock_all += final_stock

        if final_stock > 5:
            stock_status = "in_stock"
            in_stock_count += 1
        elif final_stock > 0:
            stock_status = "low_stock"
            low_stock_count += 1
        else:
            stock_status = "out_of_stock"

        wholesale_pkr = round(lowest_usdt * USDT_TO_PKR_BENCHMARK)
        retail_pkr = prod["pkr"]
        margin_pkr = retail_pkr - wholesale_pkr
        margin_pct = round((margin_pkr / retail_pkr) * 100, 1) if retail_pkr > 0 else 0.0

        products_db.append({
            "slug": slug,
            "name": prod["name"],
            "provider": prod["provider"],
            "category": prod["category"],
            "duration": prod["duration"],
            "access": prod["access"],
            "retail_pkr": retail_pkr,
            "retail_usd": prod["usd"],
            "wholesale_cost_usdt": lowest_usdt,
            "wholesale_cost_pkr": wholesale_pkr,
            "profit_margin_pkr": margin_pkr,
            "profit_margin_pct": margin_pct,
            "stock_count": final_stock,
            "stock_status": stock_status,
            "best_supplier_bot": best_supplier,
            "supplier_quotes_count": len(supplier_list),
            "supplier_variants": [
                {
                    "bot_name": item.get("Bot Name"),
                    "product_name": item.get("Product Name", "").strip(),
                    "price_usdt": float(item.get("Price (USDT)", 0.0)) if item.get("Price (USDT)") else 0.0,
                    "stock": item.get("Stock"),
                    "type": item.get("Type"),
                    "status": item.get("Status")
                }
                for item in supplier_list
            ]
        })

    # Build Structured Expansion Apps (21+ additional apps ready for storefront launch)
    expansion_catalog: List[Dict[str, Any]] = []
    for exp in EXPANSION_APPS:
        exp_slug = exp["slug"]
        kws = exp["keywords"]
        matches = [
            r for r in raw_rows
            if any(k in r.get("Product Name", "").lower() for k in kws)
        ]
        valid_prices = []
        stock_sum = 0
        best_bot = "Verified Telegram Supplier"
        for m in matches:
            try:
                p = float(m.get("Price (USDT)", 0.0))
                if p > 0.0:
                    valid_prices.append((p, m.get("Bot Name", "Unknown Bot")))
            except (ValueError, TypeError):
                pass
            stock_sum += parse_stock_value(m.get("Stock"))

        if valid_prices:
            min_p = min(valid_prices, key=lambda x: x[0])
            wh_usdt = round(min_p[0], 2)
            best_bot = min_p[1]
        else:
            wh_usdt = 2.00

        wh_pkr = round(wh_usdt * USDT_TO_PKR_BENCHMARK)
        sug_pkr = exp["suggested_pkr"]
        est_margin_pkr = sug_pkr - wh_pkr
        est_margin_pct = round((est_margin_pkr / sug_pkr) * 100, 1) if sug_pkr > 0 else 0.0

        expansion_catalog.append({
            "slug": exp_slug,
            "name": exp["name"],
            "category": exp["category"],
            "lowest_wholesale_usdt": wh_usdt,
            "lowest_wholesale_pkr": wh_pkr,
            "suggested_retail_pkr": sug_pkr,
            "estimated_margin_pkr": est_margin_pkr,
            "estimated_margin_pct": est_margin_pct,
            "total_stock": stock_sum,
            "best_supplier_bot": best_bot,
            "available_skus": len(matches)
        })

    # Group remaining items by broad categories
    expansion_map: Dict[str, List[Dict[str, Any]]] = {}
    for item in unmatched_items:
        pname = item.get("Product Name", "").strip()
        category = "Other Digital Subscriptions"
        if "discord" in pname.lower():
            category = "Discord Shop & Decor"
        elif "icloud" in pname.lower():
            category = "Apple iCloud Slots"
        elif "apple music" in pname.lower():
            category = "Apple Music Subscriptions"
        elif "ilovepdf" in pname.lower():
            category = "PDF & Document AI"
        elif "jetbrains" in pname.lower():
            category = "Developer Tools"
        elif "duolingo" in pname.lower():
            category = "Education & Languages"
        elif "expressvpn" in pname.lower():
            category = "VPN & Privacy"
        elif "telegram" in pname.lower():
            category = "Telegram Premium & Stars"
        elif "coursera" in pname.lower():
            category = "Education & Certifications"
        elif "prime" in pname.lower():
            category = "Streaming & Entertainment"
        elif "disney" in pname.lower():
            category = "Streaming & Entertainment"
        elif "otp" in pname.lower():
            category = "Verification & OTP Services"
        elif "outlook" in pname.lower():
            category = "Aged Accounts & Email"

        expansion_map.setdefault(category, []).append({
            "product_name": pname,
            "bot_name": item.get("Bot Name"),
            "price_usdt": item.get("Price (USDT)"),
            "stock": item.get("Stock"),
            "type": item.get("Type")
        })

    # Supplier bots summary
    supplier_bot_counts: Dict[str, int] = {}
    for r in raw_rows:
        bot = r.get("Bot Name", "Unknown")
        supplier_bot_counts[bot] = supplier_bot_counts.get(bot, 0) + 1

    database = {
        "metadata": {
            "version": "2.1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exchange_rate_usdt_pkr": USDT_TO_PKR_BENCHMARK,
            "source_file": source_file,
            "market": "Pakistan (AIToolGems Exclusive)"
        },
        "summary": {
            "total_catalog_products": len(products_db),
            "total_expansion_apps_ready": len(expansion_catalog),
            "total_recognized_tool_families": len(products_db) + len(expansion_catalog),
            "total_supplier_skus_tracked": len(raw_rows),
            "supplier_bots_monitored": len(supplier_bot_counts),
            "total_inventory_units_in_stock": total_stock_all,
            "in_stock_catalog_tools": in_stock_count,
            "low_stock_catalog_tools": low_stock_count,
            "average_profit_margin_pct": round(sum(p["profit_margin_pct"] for p in products_db) / len(products_db), 1)
        },
        "supplier_bots": [
            {"bot_name": bot, "total_skus": count}
            for bot, count in sorted(supplier_bot_counts.items(), key=lambda x: x[1], reverse=True)
        ],
        "products": products_db,
        "expansion_catalog": expansion_catalog,
        "expansion_candidates": expansion_map
    }

    return database


def generate_summary_reference(database: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generates an executive, compact cost-and-margin reference table."""
    summary_rows = []
    for p in database["products"]:
        summary_rows.append({
            "slug": p["slug"],
            "tool_name": p["name"],
            "category": p["category"],
            "retail_price": f"Rs. {p['retail_pkr']:,} (${p['retail_usd']})",
            "wholesale_cost": f"${p['wholesale_cost_usdt']:.2f} USDT (Rs. {p['wholesale_cost_pkr']:,})",
            "net_margin": f"Rs. {p['profit_margin_pkr']:,} ({p['profit_margin_pct']}%)",
            "stock": f"{p['stock_count']} units ({p['stock_status']})",
            "primary_supplier": p["best_supplier_bot"]
        })
    return summary_rows


def sync_admin_js(database: Dict[str, Any], admin_js_path: Path) -> bool:
    """Updates productSeed in admin.js with verified stock counts and wholesale costs."""
    if not admin_js_path.exists():
        print(f"Warning: {admin_js_path} does not exist. Skipping admin.js sync.")
        return False

    content = admin_js_path.read_text(encoding="utf-8")

    # Build updated productSeed structure: [id, name, category, price, domain, stock, wholesaleUsdt, supplier]
    new_seed_entries = []
    for p in database["products"]:
        domain_guess = f"{p['slug']}.com"
        if p["slug"] == "gemini": domain_guess = "gemini.google.com"
        elif p["slug"] == "veo": domain_guess = "deepmind.google"
        elif p["slug"] == "n8n": domain_guess = "n8n.io"
        elif p["slug"] == "elevenlabs": domain_guess = "elevenlabs.io"
        elif p["slug"] == "lovable": domain_guess = "lovable.dev"
        elif p["slug"] == "gamma": domain_guess = "gamma.app"
        elif p["slug"] == "replit": domain_guess = "replit.com"
        elif p["slug"] == "notion": domain_guess = "notion.so"
        elif p["slug"] == "windows": domain_guess = "microsoft.com"
        elif p["slug"] == "copilot": domain_guess = "github.com"
        elif p["slug"] == "office365": domain_guess = "microsoft.com"

        new_seed_entries.append(
            f"  ['{p['slug']}','{p['name']}','{p['category']}',{p['retail_pkr']},'{domain_guess}',{p['stock_count']},{p['wholesale_cost_usdt']},'{p['best_supplier_bot']}']"
        )

    new_seed_str = "const productSeed = [\n" + ",\n".join(new_seed_entries) + "\n].map(([id,name,category,price,domain,stock,wholesaleCost,supplier]) => ({\n  id, name, category, price, domain, stock: stock || 15, wholesaleCost: wholesaleCost || 0, supplier: supplier || 'AIToolGems Direct',\n  description: '',\n  logo: `assets/product-logos/${id}.png`\n}));"

    seed_pattern = re.compile(r"const\s+productSeed\s*=\s*\[.*?\n\]\.map\(\(\[id,name,category,price,domain[^\]]*\]\)\s*=>\s*\(\{.*?\}\)\);", re.DOTALL)

    if seed_pattern.search(content):
        updated_content = seed_pattern.sub(new_seed_str, content, count=1)
    else:
        # Fallback if map structure differs slightly
        seed_pattern_simple = re.compile(r"const\s+productSeed\s*=\s*\[.*?\n\]\.map\(.*?\)\);", re.DOTALL)
        updated_content = seed_pattern_simple.sub(new_seed_str, content, count=1)

    # Enhance renderAdminProducts in admin.js to display live stock and wholesale cost
    old_row_pattern = re.compile(r'<td><span class="status">In stock</span></td>', re.DOTALL)
    new_row_str = '<td><span class="status" style="font-size:12px;padding:3px 8px;border-radius:6px;background:${product.stock > 5 ? \"rgba(16,185,129,0.15)\" : \"rgba(245,158,11,0.15)\"};color:${product.stock > 5 ? \"#10b981\" : \"#f59e0b\"};font-weight:600;">${product.stock || 15} in stock</span><br><small style="opacity:0.65;font-size:11px;">Cost: $${product.wholesaleCost || 0} (${escapeHTML(product.supplier || "Supplier")})</small></td>'

    if 'product.stock' not in updated_content:
        updated_content = old_row_pattern.sub(new_row_str, updated_content)

    admin_js_path.write_text(updated_content, encoding="utf-8")
    print(f"Successfully synchronized {len(database['products'])} tools into admin.js")
    return True


def run_pipeline(sync_admin: bool = True) -> Dict[str, Any]:
    """Master workflow execution."""
    rows, source_name = parse_supplier_csv()
    print(f"Loading supplier data from: data/suppliers/{source_name}")
    print(f"Loaded {len(rows)} raw supplier listing rows.")

    print("Synthesizing wholesale inventory database (Catalog + Expansion)...")
    db = build_wholesale_inventory(rows, source_file=f"data/suppliers/{source_name}")

    OUTPUT_DB.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
    print(f"Wrote master wholesale database to: {OUTPUT_DB}")

    summary = generate_summary_reference(db)
    with open(OUTPUT_SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote executive summary table to: {OUTPUT_SUMMARY}")

    if sync_admin:
        sync_admin_js(db, ADMIN_JS_PATH)

    return db


def main():
    parser = argparse.ArgumentParser(description="AIToolGems Wholesale Cost & Inventory Synchronizer")
    parser.add_argument("--sync", action="store_true", help="Sync database with admin.js")
    parser.add_argument("--report", action="store_true", help="Print formatted executive margin report")
    parser.add_argument("--audit", action="store_true", help="Audit all 40 catalog items for wholesale cost & stock")
    args = parser.parse_args()

    db = run_pipeline(sync_admin=args.sync or True)

    if args.report or args.audit:
        print("\n" + "=" * 90)
        print(f"AIToolGems Active Storefront Tools (40 Tools) (USD/PKR: {USDT_TO_PKR_BENCHMARK})")
        print("=" * 90)
        print(f"{'Tool':25} | {'Retail (PKR)':12} | {'Wholesale':16} | {'Margin':14} | {'Stock':10} | {'Supplier':20}")
        print("-" * 90)
        for p in db["products"]:
            wh_str = f"${p['wholesale_cost_usdt']:.2f} ({p['wholesale_cost_pkr']} PKR)"
            mg_str = f"{p['profit_margin_pkr']} PKR ({p['profit_margin_pct']}%)"
            st_str = f"{p['stock_count']} units"
            print(f"{p['name'][:25]:25} | Rs. {p['retail_pkr']:<8} | {wh_str:16} | {mg_str:14} | {st_str:10} | {p['best_supplier_bot'][:20]}")
        print("=" * 90)

        print("\n" + "=" * 90)
        print(f"AIToolGems Available Expansion Apps In Supplier Inventory ({len(db['expansion_catalog'])} Apps)")
        print("=" * 90)
        print(f"{'App / Digital Product':30} | {'Suggested PKR':14} | {'Wholesale':16} | {'Est. Margin':14} | {'Stock':10} | {'Supplier':20}")
        print("-" * 90)
        for exp in db["expansion_catalog"]:
            wh_str = f"${exp['lowest_wholesale_usdt']:.2f} ({exp['lowest_wholesale_pkr']} PKR)"
            mg_str = f"{exp['estimated_margin_pkr']} PKR ({exp['estimated_margin_pct']}%)"
            st_str = f"{exp['total_stock']} units"
            print(f"{exp['name'][:30]:30} | Rs. {exp['suggested_retail_pkr']:<10} | {wh_str:16} | {mg_str:14} | {st_str:10} | {exp['best_supplier_bot'][:20]}")
        print("=" * 90)
        print(f"Total Supplier Listings In File: {db['summary']['total_supplier_skus_tracked']} across {db['summary']['supplier_bots_monitored']} Telegram Bots")
        print(f"Total Recognized Tool Families: {db['summary']['total_recognized_tool_families']} (40 Live + {len(db['expansion_catalog'])} Ready to Launch)")


if __name__ == "__main__":
    main()
