#!/usr/bin/env python3
"""
Fix JP homepage schema per Bing Webmaster Guidelines:
1. Add Product schema for all 22 tools
2. Fix ItemList count to match actual items
3. Ensure accurate structured data
"""
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

# Tool data for Product schema
TOOLS = [
    {"name": "ChatGPT Plus", "brand": "OpenAI", "category": "AI Assistants", "price": "2036", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/chatgpt/"},
    {"name": "Gemini Pro", "brand": "Google", "category": "AI Assistants", "price": "849", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/gemini/"},
    {"name": "Veo 3 Ultra", "brand": "Google DeepMind", "category": "AI Video", "price": "1415", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/veo/"},
    {"name": "Leonardo AI Essential", "brand": "Leonardo AI", "category": "Design", "price": "1358", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/leonardo/"},
    {"name": "ElevenLabs", "brand": "ElevenLabs", "category": "AI Voice", "price": "2150", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/elevenlabs/"},
    {"name": "Canva Pro Edu", "brand": "Canva", "category": "Design", "price": "679", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/canva/"},
    {"name": "Figma Pro Private", "brand": "Figma", "category": "Design", "price": "2207", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/figma/"},
    {"name": "CapCut Pro", "brand": "CapCut", "category": "AI Video", "price": "679", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/capcut/"},
    {"name": "Adobe Creative", "brand": "Adobe", "category": "Design", "price": "1075", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/adobe/"},
    {"name": "Lovable Pro", "brand": "Lovable", "category": "Development", "price": "1075", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/lovable/"},
    {"name": "Gamma Pro", "brand": "Gamma", "category": "Productivity", "price": "14711", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/gamma/"},
    {"name": "Replit Core", "brand": "Replit", "category": "Development", "price": "2150", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/replit/"},
    {"name": "n8n Starter", "brand": "n8n", "category": "Development", "price": "4526", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/n8n/"},
    {"name": "Manus AI Pro", "brand": "Manus", "category": "AI Assistants", "price": "8487", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/manus/"},
    {"name": "Notion Business", "brand": "Notion", "category": "Productivity", "price": "1415", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/notion/"},
    {"name": "NordVPN", "brand": "Nord Security", "category": "VPN & Security", "price": "6846", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/nordvpn/"},
    {"name": "Surfshark VPN", "brand": "Nord Security", "category": "VPN & Security", "price": "679", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/surfshark/"},
    {"name": "YouTube Premium", "brand": "Google", "category": "Entertainment", "price": "1018", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/youtube/"},
    {"name": "Netflix Premium 4K", "brand": "Netflix", "category": "Entertainment", "price": "453", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/netflix/"},
    {"name": "LinkedIn Premium", "brand": "Microsoft", "category": "Business", "price": "1075", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/linkedin/"},
    {"name": "Windows 11 Pro Key", "brand": "Microsoft", "category": "Software", "price": "1900", "currency": "JPY", "url": "https://aitoolgems.tech/jp/tools/windows/"},
]

def generate_product_schema(tool):
    """Generate Product JSON-LD for a tool."""
    return f'''{{
      "@type": "Product",
      "name": "{tool['name']}",
      "brand": {{
        "@type": "Brand",
        "name": "{tool['brand']}"
      }},
      "description": "{tool['name']} — {tool['category']} listing in Japan",
      "url": "{tool['url']}",
      "image": "https://aitoolgems.tech/assets/brand-logo-light.webp",
      "category": "{tool['category']}",
      "offers": {{
        "@type": "Offer",
        "priceCurrency": "{tool['currency']}",
        "price": "{tool['price']}",
        "availability": "https://schema.org/LimitedAvailability",
        "url": "{tool['url']}"
      }}
    }}'''

def main():
    path = BASE / "jp" / "index.html"
    html = path.read_text(encoding="utf-8")
    
    # Check if Product schema already exists
    if '"@type": "Product"' in html:
        print("✓ Product schema already exists")
        return
    
    # Generate all Product schemas
    products = "\n,\n".join(generate_product_schema(t) for t in TOOLS)
    
    # Create the Product schema block
    product_schema = f'''    <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "@id": "https://aitoolgems.tech/jp/#product-catalog",
  "name": "AI Tools Japan — Product Catalog",
  "numberOfItems": {len(TOOLS)},
  "itemListElement": [
{products}
  ]
}}
</script>'''
    
    # Insert before closing </head>
    html = html.replace("</head>", product_schema + "\n</head>")
    
    # Fix ItemList numberOfItems to match actual count
    html = html.replace('"numberOfItems": 22', f'"numberOfItems": {len(TOOLS)}')
    
    path.write_text(html, encoding="utf-8")
    print(f"✓ Added {len(TOOLS)} Product schemas to JP homepage")
    print(f"✓ Fixed ItemList count to {len(TOOLS)}")

if __name__ == "__main__":
    main()
