#!/usr/bin/env python3
"""Clean up duplicate schemas and add proper Product schemas to PK homepage"""
from pathlib import Path
import json, re

html = Path('D:/ai-tool-gems/index.html').read_text(encoding='utf-8')

# Remove ALL existing JSON-LD schemas
html = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', html, flags=re.DOTALL)

# Products
products = [
    {"name": "ChatGPT Plus", "category": "AI Assistants", "price": "2300", "duration": "1 Month", "access": "Private Plan"},
    {"name": "Gemini Pro", "category": "AI Assistants", "price": "800", "duration": "18 Months", "access": "Invitation Plan"},
    {"name": "Veo 3 Ultra", "category": "AI Video", "price": "2100", "duration": "Unlimited", "access": "Shared Plan"},
    {"name": "Leonardo AI Essential", "category": "Design", "price": "1900", "duration": "8,500 Credits", "access": "Private Plan"},
    {"name": "ElevenLabs", "category": "AI Voice", "price": "3300", "duration": "1 Month", "access": "Private Plan"},
    {"name": "Canva Pro Edu", "category": "Design", "price": "900", "duration": "1 Year", "access": "Invitation Plan"},
    {"name": "Figma Pro Private", "category": "Design", "price": "3000", "duration": "2 Years", "access": "Private Plan"},
    {"name": "CapCut Pro", "category": "AI Video", "price": "900", "duration": "1 Month", "access": "Private Plan"},
    {"name": "Adobe Creative Cloud", "category": "Design", "price": "1700", "duration": "2 Months", "access": "Private Plan"},
    {"name": "Lovable Pro", "category": "Development", "price": "1600", "duration": "1 Month", "access": "Private Plan"},
    {"name": "Gamma Pro", "category": "Productivity", "price": "23000", "duration": "1 Year", "access": "Private Plan"},
    {"name": "Replit Core", "category": "Development", "price": "3200", "duration": "$40 Credits", "access": "Private Plan"},
    {"name": "n8n Starter", "category": "Development", "price": "7000", "duration": "1 Year", "access": "Private Plan"},
    {"name": "Notion Business", "category": "Productivity", "price": "2200", "duration": "3 Months", "access": "Invitation Plan"},
    {"name": "NordVPN", "category": "VPN & Security", "price": "1800", "duration": "3 Months", "access": "Private Plan"},
    {"name": "Surfshark VPN", "category": "VPN & Security", "price": "800", "duration": "2 Months", "access": "Shared Plan"},
    {"name": "YouTube Premium", "category": "Entertainment", "price": "1200", "duration": "3 Months", "access": "Invitation Plan"},
    {"name": "Netflix Premium 4K", "category": "Entertainment", "price": "400", "duration": "1 Month", "access": "Shared Plan"},
    {"name": "LinkedIn Premium", "category": "Business", "price": "1500", "duration": "2 Months", "access": "Invitation Plan"},
    {"name": "Windows 11 Pro Key", "category": "Software", "price": "1900", "duration": "Lifetime", "access": "License Key Plan"},
]

product_schemas = []
for p in products:
    product_schemas.append({
        "@type": "Product",
        "name": p["name"],
        "category": p["category"],
        "offers": {
            "@type": "Offer",
            "price": p["price"],
            "priceCurrency": "PKR",
            "name": f"{p['duration']} — {p['access']}"
        }
    })

faq_schema = {
    "@type": "FAQPage",
    "mainEntity": [
        {"@type": "Question", "name": "How does ordering work?", "acceptedAnswer": {"@type": "Answer", "text": "Add a product to your cart, then click WhatsApp for order confirmation."}},
        {"@type": "Question", "name": "What access type will I receive?", "acceptedAnswer": {"@type": "Answer", "text": "Access varies by product: Private, Shared, Invitation, or Official License Key."}},
        {"@type": "Question", "name": "Do you provide a warranty?", "acceptedAnswer": {"@type": "Answer", "text": "Yes! Every product specifies an explicit replacement warranty."}},
        {"@type": "Question", "name": "How fast is delivery?", "acceptedAnswer": {"@type": "Answer", "text": "Delivery begins promptly after payment confirmation. Exact timing is confirmed via WhatsApp depending on account verification."}},
        {"@type": "Question", "name": "Are you affiliated with these brands?", "acceptedAnswer": {"@type": "Answer", "text": "AI Tool Gems is an independent marketplace, not affiliated with third-party brands."}}
    ]
}

org_schema = {"@type": "Organization", "name": "AI Tool Gems", "url": "https://aitoolgems.tech/", "logo": "https://aitoolgems.tech/assets/brand-logo-light.webp"}
website_schema = {"@type": "WebSite", "name": "AI Tool Gems", "url": "https://aitoolgems.tech/", "potentialAction": {"@type": "SearchAction", "target": "https://aitoolgems.tech/?q={search_term_string}", "query-input": "required name=search_term_string"}}
webpage_schema = {"@type": "WebPage", "name": "Premium AI tools in Pakistan", "url": "https://aitoolgems.tech/"}
itemlist_schema = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i+1, "item": {"@id": "https://aitoolgems.tech/tools/" + p["name"].lower().replace(" ", "-").replace("+", "").replace("core", "").replace("starter", "").replace("edu", "").replace("business", "").replace("key", "").replace("premium", "").replace("essential", "").replace("creative cloud", "").replace("vpn", "").replace("assistant", "").replace("video", "").replace("design", "").replace("development", "").replace("productivity", "").replace("entertainment", "").replace("security", "").replace("software", "").replace("voice", "").replace("dubbing", "").replace("audio", "").replace("music", "").replace("movies", "").replace("series", "").replace("4k", "").replace("jobs", "").replace("learning", "").replace("sales", "").replace("photo", "").replace("file", "").replace("edit", "").replace("web", "").replace("apps", "").replace("mvp", "").replace("briefs", "").replace("outlines", "").replace("presentations", "").replace("decks", "").replace("docs", "").replace("workspace", "").replace("knowledge", "").replace("project", "").replace("boards", "").replace("summaries", "").replace("privacy", "").replace("travel", "").replace("streaming", "").replace("unlimited", "").replace("shared", "").replace("private", "").replace("invitation", "").replace("license", "").replace("1 month", "").replace("3 months", "").replace("2 months", "").replace("1 year", "").replace("2 years", "").replace("18 months", "").replace("lifetime", "").replace("credits", "").replace("40", "").replace("8,500", "").replace("3,000", "").replace("2,300", "").replace("2,100", "").replace("1,900", "").replace("3,300", "").replace("900", "").replace("1,700", "").replace("1,600", "").replace("23,000", "").replace("3,200", "").replace("7,000", "").replace("2,200", "").replace("1,800", "").replace("800", "").replace("1,200", "").replace("400", "").replace("1,500", "").replace("2,800", ""), "name": p["name"]}} for i, p in enumerate(products)]}

# Single combined schema
combined = {"@context": "https://schema.org", "@graph": [org_schema, website_schema, webpage_schema, faq_schema, itemlist_schema] + product_schemas}

new_schema = f'<script type="application/ld+json">\n{json.dumps(combined, indent=2, ensure_ascii=False)}\n</script>\n'

# Insert before </head>
html = html.replace('</head>', new_schema + '</head>')

Path('D:/ai-tool-gems/index.html').write_text(html, encoding='utf-8')
print("✅ Cleaned up duplicates, single combined schema with 20 Products")
