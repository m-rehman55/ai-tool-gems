#!/usr/bin/env python3
"""
Synchronizes index.html and tools/index.html ItemList schemas
to include all 40 verified tools in exact order.
"""

from pathlib import Path
import json
import re

BASE = Path(__file__).resolve().parent.parent

# The 40 products with their slug and exact name
PRODUCTS = [
    {"slug": "chatgpt", "name": "ChatGPT Plus"},
    {"slug": "gemini", "name": "Gemini Pro"},
    {"slug": "veo", "name": "Veo 3 Ultra"},
    {"slug": "leonardo", "name": "Leonardo AI Essential"},
    {"slug": "elevenlabs", "name": "ElevenLabs Voice AI"},
    {"slug": "canva", "name": "Canva Pro Edu"},
    {"slug": "figma", "name": "Figma Pro Private"},
    {"slug": "capcut", "name": "CapCut Pro VIP"},
    {"slug": "adobe", "name": "Adobe Creative Cloud"},
    {"slug": "lovable", "name": "Lovable Pro"},
    {"slug": "gamma", "name": "Gamma Pro"},
    {"slug": "replit", "name": "Replit Core"},
    {"slug": "n8n", "name": "n8n Starter"},
    {"slug": "notion", "name": "Notion Business"},
    {"slug": "nordvpn", "name": "NordVPN"},
    {"slug": "surfshark", "name": "Surfshark VPN"},
    {"slug": "youtube", "name": "YouTube Premium"},
    {"slug": "netflix", "name": "Netflix Premium 4K"},
    {"slug": "linkedin", "name": "LinkedIn Premium"},
    {"slug": "windows", "name": "Windows 11 Pro Key"},
    {"slug": "claude", "name": "Claude Pro (3.5 Sonnet)"},
    {"slug": "midjourney", "name": "Midjourney v6.1 Pro"},
    {"slug": "cursor", "name": "Cursor AI Pro"},
    {"slug": "perplexity", "name": "Perplexity Pro"},
    {"slug": "deepseek", "name": "DeepSeek Unlimited"},
    {"slug": "grok", "name": "SuperGrok / Grok 2"},
    {"slug": "runway", "name": "Runway ML Gen-3 Pro"},
    {"slug": "heygen", "name": "HeyGen AI Avatar Pro"},
    {"slug": "grammarly", "name": "Grammarly Premium"},
    {"slug": "quillbot", "name": "QuillBot Premium"},
    {"slug": "semrush", "name": "SEMrush Pro"},
    {"slug": "allinone", "name": "All-in-One Mega AI Portal"},
    {"slug": "tradingview", "name": "TradingView Pro"},
    {"slug": "kling", "name": "Kling AI"},
    {"slug": "freepik", "name": "Freepik Premium"},
    {"slug": "spotify", "name": "Spotify Premium"},
    {"slug": "copilot", "name": "GitHub Copilot"},
    {"slug": "suno", "name": "Suno AI"},
    {"slug": "turnitin", "name": "Turnitin Student Account"},
    {"slug": "office365", "name": "Microsoft Office 365 (1TB)"}
]

def update_index_html():
    file_path = BASE / "index.html"
    content = file_path.read_text(encoding="utf-8")

    # Build new ItemList elements
    elements = []
    for pos, p in enumerate(PRODUCTS, start=1):
        elements.append({
            "@type": "ListItem",
            "position": pos,
            "item": {
                "@id": f"https://aitoolgems.tech/tools/{p['slug']}/",
                "name": p["name"]
            }
        })

    new_item_list_json = json.dumps({"@type": "ItemList", "itemListElement": elements}, indent=6)

    # Replace the existing ItemList in index.html
    pattern = re.compile(r'\{\s*"@type":\s*"ItemList",\s*"itemListElement":\s*\[\s*\{.*?\}\s*\]\s*\}', re.DOTALL)
    if not pattern.search(content):
        print("Error: Could not locate ItemList in index.html")
        return

    updated_content = pattern.sub(new_item_list_json, content, count=1)
    file_path.write_text(updated_content, encoding="utf-8")
    print("index.html ItemList updated to 40 products.")

def update_tools_index_html():
    file_path = BASE / "tools" / "index.html"
    content = file_path.read_text(encoding="utf-8")

    # Build new ItemList elements
    elements = []
    for pos, p in enumerate(PRODUCTS, start=1):
        elements.append({
            "@type": "ListItem",
            "position": pos,
            "url": f"https://aitoolgems.tech/tools/{p['slug']}/",
            "name": p["name"]
        })

    new_item_list_json = json.dumps({
        "@type": "ItemList",
        "name": "Verified AI Tools in Pakistan & Worldwide",
        "numberOfItems": len(PRODUCTS),
        "itemListElement": elements
    }, indent=6)

    pattern = re.compile(r'\{\s*"@type":\s*"ItemList",\s*"name":\s*"Verified AI Tools in Pakistan",\s*"numberOfItems":\s*\d+,\s*"itemListElement":\s*\[\s*\{.*?\}\s*\]\s*\}', re.DOTALL)
    if not pattern.search(content):
        print("Error: Could not locate ItemList in tools/index.html")
        return

    updated_content = pattern.sub(new_item_list_json, content, count=1)
    # Also update any "20 verified" or "28 verified" text claims in tools/index.html
    updated_content = updated_content.replace("Compare all 20 verified software tools", "Compare all 40 verified software tools")
    updated_content = updated_content.replace("All 20 digital tools are active", "All 40 digital tools are active")
    updated_content = updated_content.replace("20 Verified Tools — Checked", "40 Verified Tools — Checked")

    file_path.write_text(updated_content, encoding="utf-8")
    print("tools/index.html ItemList updated to 40 products.")

if __name__ == "__main__":
    update_index_html()
    update_tools_index_html()
