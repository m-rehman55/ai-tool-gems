import glob
import os
import re
import xml.etree.ElementTree as ET

tree = ET.parse('sitemap.xml')
root = tree.getroot()
sitemap_urls = set()
for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
    loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text.strip()
    sitemap_urls.add(loc)

print(f"Total URLs in sitemap.xml: {len(sitemap_urls)}")

html_files = glob.glob('**/*.html', recursive=True)
indexable = []
noindex = []

for f in html_files:
    if 'googleb36' in f or '.seo-cache' in f:
        continue
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        content = fp.read()
    m_robots = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', content, re.I)
    robots = m_robots.group(1).lower() if m_robots else 'index, follow'
    m_canon = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content, re.I)
    if not m_canon:
        m_canon = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', content, re.I)
    canonical = m_canon.group(1) if m_canon else 'MISSING'
    
    if 'noindex' in robots:
        noindex.append((f, canonical, robots))
    else:
        indexable.append((f, canonical, robots))

print(f"Total indexable HTML pages: {len(indexable)}")
print(f"Total noindex HTML pages: {len(noindex)}")
print("Noindex pages:", [x[0] for x in noindex])

missing_from_sitemap = []
for f, canon, r in indexable:
    if canon != 'MISSING' and canon not in sitemap_urls:
        missing_from_sitemap.append((f, canon))

print(f"\nIndexable pages MISSING from sitemap.xml ({len(missing_from_sitemap)}):")
for f, c in missing_from_sitemap:
    print(f"  {f} -> {c}")
