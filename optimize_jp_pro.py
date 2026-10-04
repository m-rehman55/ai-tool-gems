#!/usr/bin/env python3
"""
Pro-level JP Homepage Optimization per Bing Webmaster Guidelines:
1. Fix JSON-LD formatting
2. Add preload directives
3. Update OG image to WebP
4. Add WebP favicon
5. Optimize meta tags
6. Add FAQ schema properly
7. Improve structured data
8. Fix HTML structure
"""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
path = BASE / "jp" / "index.html"
html = path.read_text(encoding="utf-8")

# =============================================
# 1. FIX JSON-LD FORMATTING (proper indentation)
# =============================================
# The Product schema block has inconsistent indentation
# Let's find and fix the JSON-LD blocks

# Find all JSON-LD blocks
jsonld_pattern = r'<script type="application/ld\+json">\s*\n(.*?)\n\s*</script>'
matches = re.findall(jsonld_pattern, html, re.DOTALL)

# Fix the ItemList/Product schema - reformat with proper indentation
old_product_block = html[html.find('<script type="application/ld+json">\n{\n  "@type": "ItemList"'):html.find('</script>', html.find('"@type": "Product"')) + len('</script>')]

if old_product_block:
    # Rebuild the Product schema with proper formatting
    tools = [
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

    products_json = ",\n".join(
        f'      {{\n        "@type": "Product",\n        "name": "{t["name"]}",\n        "brand": {{\n          "@type": "Brand",\n          "name": "{t["brand"]}"\n        }},\n        "description": "{t["name"]} — {t["category"]} listing in Japan",\n        "url": "{t["url"]}",\n        "image": "https://aitoolgems.tech/assets/brand-logo-light.webp",\n        "category": "{t["category"]}",\n        "offers": {{\n          "@type": "Offer",\n          "priceCurrency": "{t["currency"]}",\n          "price": "{t["price"]}",\n          "availability": "https://schema.org/LimitedAvailability",\n          "url": "{t["url"]}"\n        }}\n      }}'
        for t in tools
    )

    new_product_schema = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "@id": "https://aitoolgems.tech/jp/#product-catalog",
  "name": "AI Tools Japan — Product Catalog",
  "numberOfItems": {len(tools)},
  "itemListElement": [
{products_json}
  ]
}}
</script>'''

    # Replace the old product schema block
    start = html.find('<script type="application/ld+json">\n{\n  "@type": "ItemList"')
    end = html.find('</script>', start) + len('</script>')
    html = html[:start] + new_product_schema + html[end:]

# =============================================
# 2. ADD PRELOAD DIRECTIVES
# =============================================
preload_tags = '''  <link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" as="style">
  <link rel="preload" href="https://www.google.com/s2/favicons" as="image" type="image/png">
  <link rel="dns-prefetch" href="https://www.google.com">
  <link rel="dns-prefetch" href="https://t0.gstatic.com">
  <link rel="dns-prefetch" href="https://t1.gstatic.com">
  <link rel="dns-prefetch" href="https://t3.gstatic.com">
'''

# Insert preload tags after the preconnect tags
preconnect_end = html.find('</head>')
html = html[:preconnect_end] + preload_tags + html[preconnect_end:]

# =============================================
# 3. UPDATE OG IMAGE TO WEBP
# =============================================
html = html.replace(
    'content="https://aitoolgems.tech/assets/brand-logo-light.png"',
    'content="https://aitoolgems.tech/assets/brand-logo-light.webp"'
)

# =============================================
# 4. ADD WEB FAVICON
# =============================================
html = html.replace(
    '<link rel="icon" type="image/png" href="../assets/brand-logo-light.png">',
    '<link rel="icon" type="image/webp" href="../assets/brand-logo-light.webp">'
)
html = html.replace(
    '<link rel="apple-touch-icon" href="../assets/brand-logo-light.png">',
    '<link rel="apple-touch-icon" href="../assets/brand-logo-light.webp">'
)

# =============================================
# 5. OPTIMIZE META TAGS
# =============================================
# Fix Twitter description to match actual count (21 tools, not 20)
html = html.replace(
    'content="比較 20 verified AI tools with clear JPY pricing and direct WhatsApp ordering."',
    'content="比較 21 AI tools and digital subscriptions in JPY, with transparent pricing and WhatsApp support."'
)

# Add more specific OG description
html = html.replace(
    'content="Discover, compare and order verified AI tools with transparent JPY pricing and direct WhatsAppサポート."',
    'content="Japan AI tools marketplace — 21 premium AI tools & digital subscriptions with JPY pricing, 1-on-1 WhatsApp support, and instant delivery."'
)

# Add article:modified_time for freshness signal
html = html.replace(
    '<meta property="og:url" content="https://aitoolgems.tech/jp/">',
    '<meta property="og:url" content="https://aitoolgems.tech/jp/">\n  <meta property="article:modified_time" content="2026-09-28">'
)

# =============================================
# 6. ADD FAQ SCHEMA (properly structured)
# =============================================
faq_schema = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How does ordering work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Add a product to your cart, then click WhatsAppで注文. We receive the prepared order details and confirm current availability, the accepted payment route and delivery estimate before payment."
      }
    },
    {
      "@type": "Question",
      "name": "What access type will I receive?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Access varies by product and is clearly shown on every card: Private (your own account/credentials), Shared, Invitation (team workspace invite), or Official License Key."
      }
    },
    {
      "@type": "Question",
      "name": "Do you provide a warranty?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes! Every product specifies an explicit replacement warranty (e.g. 7 Days, 30 Days) verified before and after purchase."
      }
    },
    {
      "@type": "Question",
      "name": "How fast is delivery?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Most products are delivered within 15–60 minutes after payment confirmation; selected professional plans may take 1–2 hours. The exact estimate appears on each product."
      }
    },
    {
      "@type": "Question",
      "name": "What is the refund and replacement policy?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "If we cannot deliver the confirmed plan, you can request a full refund. After activation, replacement coverage follows the warranty period shown on that product."
      }
    },
    {
      "@type": "Question",
      "name": "Are you affiliated with these brands?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI Tool Gems is an independent digital marketplace and is not affiliated with or endorsed by third-party brands unless explicitly stated."
      }
    }
  ]
}
</script>'''

# Insert FAQ schema before </head>
html = html.replace('</head>', faq_schema + '\n</head>')

# =============================================
# 7. ADD LASTMOD FOR FRESHNESS
# =============================================
# Update WebPage schema with current date
html = html.replace('"dateModified": "2026-09-24"', '"dateModified": "2026-09-28"')

# =============================================
# 8. SAVE
# =============================================
path.write_text(html, encoding="utf-8")
print("✓ All pro-level optimizations applied to JP homepage")
print(f"✓ File size: {len(html):,} bytes")
print("✓ Changes:")
print("  - JSON-LD reformatted with proper indentation")
print("  - Preload directives added")
print("  - OG image updated to WebP")
print("  - Favicon updated to WebP")
print("  - Meta tags optimized")
print("  - FAQ schema added")
print("  - dateModified updated to 2026-09-28")
