#!/usr/bin/env python3
"""Fix remaining issues: preload, FAQ, Organization schema, google verification file"""
from pathlib import Path
import re

BASE = Path(r"D:/ai-tool-gems")
PRELOAD = '  <link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" as="style">\n'
FIXED = 0

def fix_remaining(filepath):
    global FIXED
    try:
        html = filepath.read_text(encoding="utf-8")
    except:
        return
    orig = html
    rel = str(filepath.relative_to(BASE))
    is_jp = '/jp/' in rel
    is_tool = '/tools/' in rel
    is_home = filepath.name == 'index.html' and not is_jp and 'jp' not in rel.split('/')
    is_jp_home = filepath.name == 'index.html' and is_jp
    is_guide = '/guides/' in rel and filepath.name == 'index.html'
    is_deal = 'deals' in rel and filepath.name == 'index.html'

    # 1. Preload directives - add if missing
    if 'rel="preload"' not in html:
        # Insert preload after preconnect or after charset
        if 'rel="preconnect"' in html:
            html = html.replace(
                'rel="preconnect"',
                'rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" as="style"\n  rel="preconnect"',
                1
            )
        else:
            html = html.replace('<head>', '<head>\n' + PRELOAD)

    # 2. FAQPage schema for homepages and guides
    if ('FAQPage' not in html) and (is_home or is_jp_home or is_guide or is_deal):
        faq = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "How does ordering work?", "acceptedAnswer": {"@type": "Answer", "text": "Add a product to your cart, then click WhatsApp for order confirmation."}},
    {"@type": "Question", "name": "What access type will I receive?", "acceptedAnswer": {"@type": "Answer", "text": "Access varies by product: Private, Shared, Invitation, or Official License Key."}},
    {"@type": "Question", "name": "Do you provide a warranty?", "acceptedAnswer": {"@type": "Answer", "text": "Yes! Every product specifies an explicit replacement warranty."}},
    {"@type": "Question", "name": "How fast is delivery?", "acceptedAnswer": {"@type": "Answer", "text": "Most products delivered within 15-60 minutes after payment confirmation."}},
    {"@type": "Question", "name": "Are you affiliated with these brands?", "acceptedAnswer": {"@type": "Answer", "text": "AI Tool Gems is an independent marketplace, not affiliated with third-party brands."}}
  ]
}
</script>'''
        html = html.replace('</head>', faq + '\n</head>')

    # 3. Organization/LocalBusiness schema for tool pages
    if is_tool and '"@type": "LocalBusiness"' not in html and '"@type": "Organization"' not in html:
        org = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://aitoolgems.tech/#localbusiness",
  "name": "AI Tool Gems",
  "description": "Independent AI tools marketplace",
  "url": "https://aitoolgems.tech/",
  "priceRange": "JPY 400-23000",
  "currenciesAccepted": "JPY",
  "paymentAccepted": "WhatsApp-assisted payment",
  "areaServed": "JP"
}
</script>'''
        html = html.replace('</head>', org + '\n</head>')

    # 4. google verification file - add minimal SEO
    if 'googleb36d12ee905644d9' in rel:
        html = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="robots" content="noindex, follow">
  <meta name="google-site-verification" content="b36d12ee905644d9">
  <title>AI Tool Gems - Site Verification</title>
</head>
<body>
  <h1>Site Verification</h1>
  <p>This file is used for Google Search Console verification.</p>
</body>
</html>'''
        filepath.write_text(html, encoding="utf-8")
        FIXED += 1
        return

    if html != orig:
        filepath.write_text(html, encoding="utf-8")
        FIXED += 1

# Run
html_files = sorted(BASE.rglob("*.html"))
print(f"Fixing remaining issues in {len(html_files)} files...\n")
for f in html_files:
    fix_remaining(f)
print(f"✅ Fixed {FIXED} files")
