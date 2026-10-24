#!/usr/bin/env python3
"""
Synchronizes prices/index.html and deals/index.html with all 40 verified products,
including dual PKR and USD pricing, duration, access type, and updated ItemList schema.
"""

from pathlib import Path
import json
import re

BASE = Path(__file__).resolve().parent.parent

PRODUCTS = [
    {"slug": "chatgpt", "name": "ChatGPT Plus", "provider": "OpenAI", "category": "AI Assistants", "pkr": 2300, "usd": "8.99", "duration": "1 Month", "access": "Private"},
    {"slug": "gemini", "name": "Gemini Pro", "provider": "Google", "category": "AI Assistants", "pkr": 800, "usd": "3.99", "duration": "18 Months", "access": "Invitation"},
    {"slug": "veo", "name": "Veo 3 Ultra", "provider": "Google", "category": "AI Video", "pkr": 2100, "usd": "8.49", "duration": "Unlimited", "access": "Shared"},
    {"slug": "leonardo", "name": "Leonardo AI Essential", "provider": "Leonardo.Ai", "category": "Design", "pkr": 1900, "usd": "7.49", "duration": "8,500 Credits", "access": "Private"},
    {"slug": "elevenlabs", "name": "ElevenLabs Voice AI", "provider": "ElevenLabs", "category": "AI Voice", "pkr": 3300, "usd": "12.99", "duration": "1 Month", "access": "Private"},
    {"slug": "canva", "name": "Canva Pro Edu", "provider": "Canva", "category": "Design", "pkr": 900, "usd": "3.99", "duration": "1 Year", "access": "Invitation"},
    {"slug": "figma", "name": "Figma Pro Private", "provider": "Figma", "category": "Design", "pkr": 3000, "usd": "11.99", "duration": "2 Years", "access": "Private"},
    {"slug": "capcut", "name": "CapCut Pro VIP", "provider": "Bytedance", "category": "AI Video", "pkr": 900, "usd": "3.99", "duration": "1 Month", "access": "Private"},
    {"slug": "adobe", "name": "Adobe Creative Cloud", "provider": "Adobe", "category": "Design", "pkr": 1700, "usd": "6.99", "duration": "2 Months", "access": "Private"},
    {"slug": "lovable", "name": "Lovable Pro", "provider": "Lovable", "category": "Development", "pkr": 1600, "usd": "6.49", "duration": "1 Month", "access": "Private"},
    {"slug": "gamma", "name": "Gamma Pro", "provider": "Gamma", "category": "Productivity", "pkr": 23000, "usd": "89.99", "duration": "1 Year", "access": "Private"},
    {"slug": "replit", "name": "Replit Core", "provider": "Replit", "category": "Development", "pkr": 3200, "usd": "12.49", "duration": "$40 Credits", "access": "Private"},
    {"slug": "n8n", "name": "n8n Starter", "provider": "n8n", "category": "Development", "pkr": 7000, "usd": "26.99", "duration": "1 Year", "access": "Private"},
    {"slug": "notion", "name": "Notion Business", "provider": "Notion", "category": "Productivity", "pkr": 2200, "usd": "8.99", "duration": "3 Months", "access": "Invitation"},
    {"slug": "nordvpn", "name": "NordVPN", "provider": "Nord Security", "category": "VPN & Security", "pkr": 1800, "usd": "6.99", "duration": "3 Months", "access": "Private"},
    {"slug": "surfshark", "name": "Surfshark VPN", "provider": "Nord Security", "category": "VPN & Security", "pkr": 800, "usd": "3.49", "duration": "2 Months", "access": "Shared"},
    {"slug": "youtube", "name": "YouTube Premium", "provider": "Google", "category": "Entertainment", "pkr": 1200, "usd": "4.99", "duration": "3 Months", "access": "Invitation"},
    {"slug": "netflix", "name": "Netflix Premium 4K", "provider": "Netflix", "category": "Entertainment", "pkr": 400, "usd": "1.99", "duration": "1 Month", "access": "Shared"},
    {"slug": "linkedin", "name": "LinkedIn Premium", "provider": "Microsoft", "category": "Business", "pkr": 1500, "usd": "5.99", "duration": "2 Months", "access": "Invitation"},
    {"slug": "windows", "name": "Windows 11 Pro Key", "provider": "Microsoft", "category": "Software", "pkr": 1900, "usd": "7.99", "duration": "Lifetime", "access": "License Key"},
    {"slug": "claude", "name": "Claude Pro (3.5 Sonnet)", "provider": "Anthropic", "category": "AI Assistants", "pkr": 2200, "usd": "8.99", "duration": "1 Month", "access": "Private"},
    {"slug": "midjourney", "name": "Midjourney v6.1 Pro", "provider": "Midjourney", "category": "Design", "pkr": 2400, "usd": "9.99", "duration": "1 Month", "access": "Private / Discord"},
    {"slug": "cursor", "name": "Cursor AI Pro", "provider": "Anysphere", "category": "Development", "pkr": 2800, "usd": "10.99", "duration": "1 Month", "access": "Private"},
    {"slug": "perplexity", "name": "Perplexity Pro", "provider": "Perplexity", "category": "AI Assistants", "pkr": 1400, "usd": "5.49", "duration": "1 Month", "access": "Private"},
    {"slug": "deepseek", "name": "DeepSeek Unlimited", "provider": "DeepSeek", "category": "AI Assistants", "pkr": 1100, "usd": "4.49", "duration": "1 Month", "access": "Private Portal"},
    {"slug": "grok", "name": "SuperGrok / Grok 2", "provider": "xAI", "category": "AI Assistants", "pkr": 1800, "usd": "6.99", "duration": "1 Month", "access": "Private"},
    {"slug": "runway", "name": "Runway ML Gen-3 Pro", "provider": "Runway", "category": "AI Video", "pkr": 3500, "usd": "13.99", "duration": "1 Month", "access": "Private"},
    {"slug": "heygen", "name": "HeyGen AI Avatar Pro", "provider": "HeyGen", "category": "AI Video", "pkr": 4200, "usd": "16.99", "duration": "1 Month", "access": "Private"},
    {"slug": "grammarly", "name": "Grammarly Premium", "provider": "Grammarly", "category": "Writing & SEO", "pkr": 750, "usd": "2.99", "duration": "1 Month", "access": "Private / Shared"},
    {"slug": "quillbot", "name": "QuillBot Premium", "provider": "Learneo", "category": "Writing & SEO", "pkr": 450, "usd": "1.99", "duration": "1 Month", "access": "Private / Shared"},
    {"slug": "semrush", "name": "SEMrush Pro", "provider": "SEMrush", "category": "Writing & SEO", "pkr": 1500, "usd": "5.99", "duration": "1 Month", "access": "Shared"},
    {"slug": "allinone", "name": "All-in-One Mega AI Portal", "provider": "AIToolGems", "category": "AI Assistants", "pkr": 1999, "usd": "7.99", "duration": "1 Month", "access": "Private Portal"},
    {"slug": "tradingview", "name": "TradingView Pro", "provider": "TradingView", "category": "Business", "pkr": 3500, "usd": "14.99", "duration": "1 Month", "access": "Private"},
    {"slug": "kling", "name": "Kling AI", "provider": "Kuaishou", "category": "AI Video", "pkr": 4800, "usd": "19.99", "duration": "1 Month", "access": "Private"},
    {"slug": "freepik", "name": "Freepik Premium", "provider": "Freepik", "category": "Design", "pkr": 2400, "usd": "9.99", "duration": "1 Month", "access": "Private"},
    {"slug": "spotify", "name": "Spotify Premium", "provider": "Spotify", "category": "Entertainment", "pkr": 1200, "usd": "4.99", "duration": "3 Months", "access": "Private"},
    {"slug": "copilot", "name": "GitHub Copilot", "provider": "Microsoft", "category": "Development", "pkr": 2500, "usd": "9.99", "duration": "1 Month", "access": "Private"},
    {"slug": "suno", "name": "Suno AI", "provider": "Suno", "category": "AI Voice", "pkr": 3200, "usd": "12.99", "duration": "1 Month", "access": "Private"},
    {"slug": "turnitin", "name": "Turnitin Student Account", "provider": "Turnitin", "category": "Writing & SEO", "pkr": 3600, "usd": "13.99", "duration": "1 Month", "access": "Private"},
    {"slug": "office365", "name": "Microsoft Office 365 (1TB)", "provider": "Microsoft", "category": "Productivity", "pkr": 2200, "usd": "8.99", "duration": "1 Year", "access": "Private"}
]

def update_prices():
    prices_path = BASE / "prices" / "index.html"
    content = prices_path.read_text(encoding="utf-8")

    # Build new table body
    rows = []
    for p in PRODUCTS:
        rows.append(f"""        <tr>
          <td><a href="../tools/{p['slug']}/">{p['name']}</a></td>
          <td>{p['provider']}</td>
          <td><strong>Rs. {p['pkr']:,}</strong> <small>(${p['usd']} USD)</small></td>
          <td>{p['duration']}</td>
          <td>{p['access']}</td>
          <td>Available</td>
          <td>2026-10-24</td>
        </tr>""")

    new_tbody = "\n".join(rows)
    table_pattern = re.compile(r'<tbody>(.*?)</tbody>', re.DOTALL)
    content = table_pattern.sub(f"<tbody>\n{new_tbody}\n      </tbody>", content, count=1)

    # Update description text
    content = content.replace("for 20 AI tools and digital subscriptions", f"for {len(PRODUCTS)} AI tools and digital subscriptions")
    content = content.replace("All prices verified as of 2026-10-10. Prices shown in PKR unless otherwise noted.", f"All prices verified as of 2026-10-24. Dual pricing shown in Pakistani Rupees (PKR) and US Dollars (USD).")
    
    # Update table headers if needed
    content = content.replace("<th>Marketplace Price (PKR)</th>", "<th>Price (PKR &amp; USD)</th>")
    content = content.replace("<th>Price Change</th>", "<th>Status</th>")

    prices_path.write_text(content, encoding="utf-8")
    print(f"Updated prices/index.html with {len(PRODUCTS)} products.")

def update_deals():
    deals_path = BASE / "deals" / "index.html"
    content = deals_path.read_text(encoding="utf-8")

    # 1. Update ItemList schema in deals/index.html
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
        "name": "Current AI Tool Gems listings",
        "numberOfItems": len(PRODUCTS),
        "itemListElement": elements
    }, indent=4)

    itemlist_pattern = re.compile(r'\{\s*"@type":\s*"ItemList",\s*"name":\s*"Current AI Tool Gems listings",\s*"numberOfItems":\s*\d+,\s*"itemListElement":\s*\[\s*\{.*?\}\s*\]\s*\}', re.DOTALL)
    content = itemlist_pattern.sub(new_item_list_json, content, count=1)

    # 2. Build new table body
    rows = []
    for p in PRODUCTS:
        rows.append(f"""        <tr><th><a href="../tools/{p['slug']}/">{p['name']}</a></th><td>{p['category']}</td><td>{p['duration']}</td><td>{p['access']}</td><td><strong>Rs. {p['pkr']:,}</strong> <small>(${p['usd']} USD)</small></td></tr>""")

    new_tbody = "\n".join(rows)
    table_pattern = re.compile(r'<tbody>(.*?)</tbody>', re.DOTALL)
    content = table_pattern.sub(f"<tbody>\n{new_tbody}\n      </tbody>", content, count=1)

    # Update summary text
    content = content.replace("the directory currently contains 20 listings from Rs. 400", f"the directory currently contains {len(PRODUCTS)} verified listings from Rs. 400 ($1.99 USD)")
    content = content.replace("caption>PKR marketplace directory — checked 12 September 2026", f"caption>Worldwide &amp; Pakistan marketplace directory — checked 24 October 2026")
    content = content.replace("directory of 20 marketplace listings", f"directory of {len(PRODUCTS)} marketplace listings")

    deals_path.write_text(content, encoding="utf-8")
    print(f"Updated deals/index.html with {len(PRODUCTS)} products.")

if __name__ == "__main__":
    update_prices()
    update_deals()
