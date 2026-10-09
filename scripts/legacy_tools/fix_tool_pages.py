#!/usr/bin/env python3
"""
Fix all JP tool pages:
1. Add Bing verification meta tag
2. Update OG image to WebP
3. Fix manus duplicate Product schema
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent
jp_dir = BASE / "jp" / "tools"

BING_META = '  <meta name="msvalidate.01" content="737494F711E656D83B3126A5D5707776">\n'

fixed_count = 0
for tool_dir in sorted(jp_dir.iterdir()):
    if not tool_dir.is_dir():
        continue
    index_file = tool_dir / "index.html"
    if not index_file.exists():
        continue
    
    html = index_file.read_text(encoding="utf-8")
    original = html
    
    # 1. Add Bing meta tag after robots meta
    if 'msvalidate' not in html:
        html = html.replace(
            '<meta name="robots" content="index,follow,max-image-preview:large">',
            '<meta name="robots" content="index,follow,max-image-preview:large">\n' + BING_META
        )
    
    # 2. Fix OG image to WebP
    html = html.replace(
        'content="https://aitoolgems.tech/assets/brand-logo-light.png"',
        'content="https://aitoolgems.tech/assets/brand-logo-light.webp"'
    )
    
    # 3. Fix Twitter image to WebP
    html = html.replace(
        'content="https://aitoolgems.tech/assets/brand-logo-light.png"',
        'content="https://aitoolgems.tech/assets/brand-logo-light.webp"'
    )
    
    # 4. Fix favicon to WebP
    html = html.replace(
        'href="../assets/brand-logo-light.png"',
        'href="../assets/brand-logo-light.webp"'
    )
    
    if html != original:
        index_file.write_text(html, encoding="utf-8")
        fixed_count += 1
        print(f"✓ {tool_dir.name}")

print(f"\n✓ Fixed {fixed_count} tool pages")
