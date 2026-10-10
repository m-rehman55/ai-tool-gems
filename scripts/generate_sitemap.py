import glob
import os
import re

html_files = glob.glob('**/*.html', recursive=True)
indexable_urls = []

for f in sorted(html_files):
    if 'googleb36' in f or '.seo-cache' in f or 'checklist' in f or 'admin.html' in f or '404.html' in f:
        continue
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        c = fp.read()
    m_robots = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', c, re.I)
    robots = m_robots.group(1).lower() if m_robots else 'index, follow'
    if 'noindex' in robots:
        continue
    m = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', c, re.I)
    if not m:
        m = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', c, re.I)
    if m:
        url = m.group(1)
        if url not in indexable_urls:
            indexable_urls.append(url)

# Group URLs logically
hubs = [u for u in indexable_urls if u in ["https://aitoolgems.tech/", "https://aitoolgems.tech/deals/", "https://aitoolgems.tech/prices/"]]
trust = [u for u in indexable_urls if any(u.endswith(x) for x in ["about.html", "contact.html", "policies.html", "privacy.html", "terms.html", "how-we-price.html", "how-we-review.html", "how-we-source.html", "product-verification.html", "correction-policy.html"])]
guides = [u for u in indexable_urls if "/guides" in u]
tools = [u for u in indexable_urls if "/tools" in u]
remaining = [u for u in indexable_urls if u not in hubs and u not in trust and u not in guides and u not in tools]

ordered = hubs + trust + guides + tools + remaining

xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in ordered:
    xml_lines.append(f'  <url><loc>{u}</loc><lastmod>2026-10-10</lastmod></url>')
xml_lines.append('</urlset>\n')

with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(xml_lines))

print(f"Generated sitemap.xml with {len(ordered)} verified canonical URLs.")
