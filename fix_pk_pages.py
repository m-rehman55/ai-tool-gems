#!/usr/bin/env python3
"""Fix all PK tool pages: Bing meta + WebP OG + WebP favicon"""
from pathlib import Path

BASE = Path(__file__).resolve().parent
tools_dir = BASE / "tools"

BING_META = '  <meta name="msvalidate.01" content="737494F711E656D83B3126A5D5707776">\n'

fixed = 0
for tool_dir in sorted(tools_dir.iterdir()):
    if not tool_dir.is_dir():
        continue
    index = tool_dir / "index.html"
    if not index.exists():
        continue
    
    html = index.read_text(encoding="utf-8")
    orig = html
    
    # Add Bing meta
    if 'msvalidate' not in html:
        html = html.replace(
            '<meta name="robots" content="index,follow,max-image-preview:large">',
            '<meta name="robots" content="index,follow,max-image-preview:large">\n' + BING_META
        )
    
    # OG image to WebP
    html = html.replace(
        'content="https://aitoolgems.tech/assets/brand-logo-light.png"',
        'content="https://aitoolgems.tech/assets/brand-logo-light.webp"'
    )
    
    # Favicon to WebP
    html = html.replace(
        'href="../assets/brand-logo-light.png"',
        'href="../assets/brand-logo-light.webp"'
    )
    
    if html != orig:
        index.write_text(html, encoding="utf-8")
        fixed += 1
        print(f"✓ {tool_dir.name}")

print(f"\n✓ Fixed {fixed} PK tool pages")
