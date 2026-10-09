#!/usr/bin/env python3
"""Master SEO Fix - Pro-level per Bing Webmaster Guidelines"""
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
FIXED = 0
BING_META = '<meta name="msvalidate.01" content="737494F711E656D83B3126A5D5707776">\n'

def fix_page(filepath):
    global FIXED
    try:
        html = filepath.read_text(encoding="utf-8")
    except:
        return
    orig = html
    rel = str(filepath.relative_to(BASE))
    is_jp = '/jp/' in rel
    is_tool = '/tools/' in rel

    # 1. Bing meta
    if 'msvalidate' not in html:
        html = html.replace('<meta name="robots"', BING_META + '  <meta name="robots"')
        if 'msvalidate' not in html:
            html = html.replace('<head>', '<head>\n' + BING_META)

    # 2. OG tags
    if 'og:title' not in html:
        t = re.search(r'<title>([^<]*)</title>', html)
        t = t.group(1) if t else "AI Tool Gems"
        html = html.replace('</head>', f'  <meta property="og:title" content="{t}">\n</head>')
    if 'og:description' not in html:
        d = re.search(r'<meta name="description" content="([^"]*)"', html)
        d = d.group(1) if d else "AI tools marketplace"
        html = html.replace('</head>', f'  <meta property="og:description" content="{d}">\n</head>')
    if 'og:url' not in html:
        rp = rel.replace("\\", "/")
        url = "https://aitoolgems.tech/" + rp.replace(".html", "").replace("index.html", "").rstrip('/')
        if not url.endswith('/'): url += '/'
        html = html.replace('</head>', f'  <meta property="og:url" content="{url}">\n</head>')
    if 'og:image' not in html:
        html = html.replace('</head>', '  <meta property="og:image" content="https://aitoolgems.tech/assets/brand-logo-light.webp">\n</head>')
    if 'twitter:card' not in html:
        html = html.replace('</head>', '  <meta name="twitter:card" content="summary_large_image">\n</head>')
    if 'twitter:title' not in html:
        t = re.search(r'<title>([^<]*)</title>', html)
        t = t.group(1) if t else "AI Tool Gems"
        html = html.replace('</head>', f'  <meta name="twitter:title" content="{t}">\n</head>')
    if 'twitter:description' not in html:
        d = re.search(r'<meta name="description" content="([^"]*)"', html)
        d = d.group(1) if d else "AI tools marketplace"
        html = html.replace('</head>', f'  <meta name="twitter:description" content="{d}">\n</head>')
    if 'twitter:image' not in html:
        html = html.replace('</head>', '  <meta name="twitter:image" content="https://aitoolgems.tech/assets/brand-logo-light.webp">\n</head>')

    # 3. OG image PNG -> WebP
    html = html.replace('content="https://aitoolgems.tech/assets/brand-logo-light.png"', 'content="https://aitoolgems.tech/assets/brand-logo-light.webp"')

    # 4. Canonical
    if 'rel="canonical"' not in html:
        rp = rel.replace("\\", "/")
        url = "https://aitoolgems.tech/" + rp.replace(".html", "").replace("index.html", "").rstrip('/')
        if not url.endswith('/'): url += '/'
        html = html.replace('<head>', f'<head>\n  <link rel="canonical" href="{url}">\n')

    # 5. Hreflang
    if 'hreflang' not in html:
        rp = rel.replace("\\", "/")
        if is_jp:
            jp_url = "https://aitoolgems.tech/" + rp
            pk_url = jp_url.replace('/jp/', '/')
        else:
            pk_url = "https://aitoolgems.tech/" + rp
            jp_url = pk_url.replace('/index.html', '/jp/').replace('.html', '/jp/')
        hl = f'  <link rel="alternate" hreflang="ja-JP" href="{jp_url}">\n  <link rel="alternate" hreflang="en-PK" href="{pk_url}">\n  <link rel="alternate" hreflang="x-default" href="{pk_url}">\n'
        html = html.replace('<head>', '<head>\n' + hl)

    # 6. Meta description
    if 'name="description"' not in html:
        desc = "Japan AI tools marketplace - JPY pricing, WhatsApp support" if is_jp else "AI tools and digital subscriptions marketplace"
        html = html.replace('<head>', f'<head>\n  <meta name="description" content="{desc}">\n')

    # 7. Robots meta
    if 'name="robots"' not in html:
        html = html.replace('<head>', '<head>\n  <meta name="robots" content="index, follow">\n')

    # 8. Viewport
    if 'name="viewport"' not in html:
        html = html.replace('<head>', '<head>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')

    # 9. Charset
    if 'charset' not in html:
        html = html.replace('<head>', '<head>\n  <meta charset="UTF-8">\n')

    # 10. Preload
    if 'rel="preload"' not in html and 'rel="preconnect"' not in html:
        pre = '  <link rel="preconnect" href="https://www.google.com" crossorigin>\n  <link rel="preconnect" href="https://t0.gstatic.com" crossorigin>\n  <link rel="preconnect" href="https://t1.gstatic.com" crossorigin>\n  <link rel="preconnect" href="https://t3.gstatic.com" crossorigin>\n'
        html = html.replace('<head>', '<head>\n' + pre)

    # 11. Favicon -> WebP
    html = html.replace('href="../assets/brand-logo-light.png"', 'href="../assets/brand-logo-light.webp"')
    html = html.replace('href="../../assets/brand-logo-light.png"', 'href="../../assets/brand-logo-light.webp"')

    # 12. JSON-LD schema
    if 'application/ld+json' not in html:
        schema = make_schema(rel)
        html = html.replace('</head>', schema + '\n</head>')

    # 13. Product schema for PK tool pages
    if is_tool and '"@type": "Product"' not in html:
        ps = make_product_schema(rel)
        html = html.replace('</head>', ps + '\n</head>')

    # 14. H1 if missing
    if '<h1' not in html:
        html = html.replace('<body>', '<body>\n  <h1>AI Tool Gems</h1>')

    if html != orig:
        filepath.write_text(html, encoding="utf-8")
        FIXED += 1

def make_schema(rel):
    is_jp = '/jp/' in rel
    lang = "ja-JP" if is_jp else "en-PK"
    rp = rel.replace("\\", "/")
    url = "https://aitoolgems.tech/" + rp.replace(".html", "").replace("index.html", "").rstrip('/')
    if not url.endswith('/'): url += '/'
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "@id": "{url}#webpage",
  "url": "{url}/",
  "name": "AI Tool Gems",
  "description": "AI tools marketplace",
  "inLanguage": "{lang}",
  "publisher": {{ "@id": "https://aitoolgems.tech/#organization" }}
}}
</script>'''

def make_product_schema(rel):
    match = re.search(r'/tools/([^/]+)/', rel)
    tool = match.group(1).title() if match else "Tool"
    rp = rel.replace("\\", "/")
    url = "https://aitoolgems.tech/" + rp
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{tool}",
  "brand": {{ "@type": "Brand", "name": "AI Tool Gems" }},
  "url": "{url}",
  "image": "https://aitoolgems.tech/assets/brand-logo-light.webp",
  "offers": {{ "@type": "Offer", "priceCurrency": "JPY", "price": "0" }}
}}
</script>'''

# Run
html_files = sorted(BASE.rglob("*.html"))
print(f"Fixing {len(html_files)} files...\n")
for f in html_files:
    fix_page(f)
print(f"✅ Fixed {FIXED} files")
