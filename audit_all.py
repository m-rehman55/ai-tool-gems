#!/usr/bin/env python3
"""
Comprehensive SEO Audit - ALL pages per Bing Webmaster Guidelines
Checks every HTML file for all required elements
"""
from pathlib import Path
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent
issues = []

def check_file(filepath, rel_path):
    """Check a single HTML file for all SEO requirements."""
    try:
        html = filepath.read_text(encoding="utf-8")
    except:
        issues.append(f"❌ CANNOT READ: {rel_path}")
        return
    
    name = rel_path.replace("\\", "/")
    
    # 1. Bing verification meta
    if 'msvalidate' not in html:
        issues.append(f"❌ {name}: Missing Bing verification meta")
    
    # 2. OG tags
    if 'og:title' not in html:
        issues.append(f"❌ {name}: Missing og:title")
    if 'og:description' not in html:
        issues.append(f"❌ {name}: Missing og:description")
    if 'og:url' not in html:
        issues.append(f"❌ {name}: Missing og:url")
    if 'og:image' not in html:
        issues.append(f"❌ {name}: Missing og:image")
    
    # 3. OG image WebP
    if 'og:image' in html:
        og_match = re.search(r'og:image"[^"]*"([^"]*)"', html)
        if og_match and '.png' in og_match.group(1):
            issues.append(f"⚠️  {name}: OG image is PNG, not WebP")
    
    # 4. Twitter cards
    if 'twitter:card' not in html:
        issues.append(f"❌ {name}: Missing twitter:card")
    
    # 5. Canonical
    if 'rel="canonical"' not in html:
        issues.append(f"❌ {name}: Missing canonical")
    
    # 6. Hreflang
    if 'hreflang' not in html:
        issues.append(f"❌ {name}: Missing hreflang")
    
    # 7. Meta description
    if 'name="description"' not in html:
        issues.append(f"❌ {name}: Missing meta description")
    
    # 8. Robots meta
    if 'name="robots"' not in html:
        issues.append(f"❌ {name}: Missing robots meta")
    
    # 9. Viewport
    if 'name="viewport"' not in html:
        issues.append(f"❌ {name}: Missing viewport")
    
    # 10. Charset
    if 'charset' not in html:
        issues.append(f"❌ {name}: Missing charset")
    
    # 11. JSON-LD schema
    if 'application/ld+json' not in html:
        issues.append(f"❌ {name}: Missing JSON-LD schema")
    
    # 12. Product schema (for tool pages)
    if '/tools/' in name and '"@type": "Product"' not in html:
        issues.append(f"❌ {name}: Missing Product schema (tool page)")
    
    # 13. H1 tag
    if '<h1' not in html:
        issues.append(f"❌ {name}: Missing H1 tag")
    
    # 14. Images with alt text
    imgs = re.findall(r'<img[^>]*>', html)
    for img in imgs:
        if 'alt=' not in img:
            issues.append(f"⚠️  {name}: Image without alt: {img[:80]}")
    
    # 15. Preload directives
    if 'rel="preload"' not in html:
        issues.append(f"⚠️  {name}: No preload directives")
    
    # 16. No duplicate meta tags
    meta_desc_count = len(re.findall(r'name="description"', html))
    if meta_desc_count > 1:
        issues.append(f"⚠️  {name}: Duplicate meta description ({meta_desc_count})")
    
    # 17. Structured data - check for Organization/LocalBusiness
    if '"@type": "Organization"' not in html and '"@type": "LocalBusiness"' not in html:
        if '/tools/' in name:
            issues.append(f"⚠️  {name}: No Organization/LocalBusiness schema")
    
    # 18. Check for FAQ schema on homepage
    if name == 'index.html' or name.endswith('/index.html'):
        if '"@type": "FAQPage"' not in html:
            issues.append(f"⚠️  {name}: No FAQPage schema")

# Check all HTML files (excluding hidden directories)
html_files = sorted([f for f in BASE.rglob("*.html") if not any(part.startswith(".") for part in f.parts)])
print(f"Auditing {len(html_files)} HTML files...\n")

for f in html_files:
    rel = str(f.relative_to(BASE))
    check_file(f, rel)

# Print results
print(f"=== AUDIT RESULTS ===")
print(f"Total files checked: {len(html_files)}")
print(f"Total issues found: {len(issues)}\n")

errors = [i for i in issues if i.startswith("❌")]
warnings = [i for i in issues if i.startswith("⚠️")]

print(f"❌ ERRORS ({len(errors)}):")
for e in errors:
    print(f"  {e}")

print(f"\n⚠️  WARNINGS ({len(warnings)}):")
for w in warnings:
    print(f"  {w}")

print(f"\n✅ CLEAN FILES: {len(html_files) - len(set(issues))}")
