#!/usr/bin/env python3
"""
Add hreflang tags to PK static pages that are missing them.
Also ensure sitemap has proper hreflang alternates.
"""
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

# PK static pages missing hreflang
PK_STATIC = [
    "about.html",
    "how-we-review.html",
    "policies.html",
    "privacy.html",
    "terms.html",
    "contact.html",
]

# JP static pages
JP_STATIC = [
    "jp/about.html",
    "jp/how-we-review.html",
    "jp/policies.html",
    "jp/privacy.html",
    "jp/terms.html",
    "jp/contact.html",
]

def add_hreflang_to_static(page_path: Path, is_jp: bool = False) -> dict:
    """Add hreflang tags to a static page."""
    try:
        html = page_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"path": str(page_path), "status": "ERROR", "detail": str(e)}
    
    # Check if hreflang already exists
    if "hreflang" in html:
        return {"path": str(page_path), "status": "✓ Already has hreflang"}
    
    # Determine the other version URL
    if is_jp:
        pk_url = "https://aitoolgems.tech/" + page_path.name
        jp_url = "https://aitoolgems.tech/" + str(page_path)
    else:
        pk_url = "https://aitoolgems.tech/" + page_path.name
        jp_url = "https://aitoolgems.tech/jp/" + page_path.name
    
    # Create hreflang link tags
    hreflang_tags = f'''
<!-- Hreflang for SEO -->
<link rel="alternate" hreflang="en-PK" href="{pk_url}" />
<link rel="alternate" hreflang="ja-JP" href="{jp_url}" />
<link rel="alternate" hreflang="x-default" href="{pk_url}" />
'''
    
    # Insert before </head>
    if "</head>" in html:
        html = html.replace("</head>", hreflang_tags + "\n</head>")
    else:
        # Insert at the beginning
        html = hreflang_tags + "\n" + html
    
    try:
        page_path.write_text(html, encoding="utf-8")
        return {"path": str(page_path), "status": "✓ Hreflang added"}
    except Exception as e:
        return {"path": str(page_path), "status": "WRITE ERROR", "detail": str(e)}


def main():
    print("=" * 60)
    print("🌐 Adding Hreflang Tags to Static Pages")
    print("=" * 60)
    
    fixed = 0
    already = 0
    errors = []
    
    # Fix PK static pages
    for page_name in PK_STATIC:
        page_path = BASE / page_name
        if page_path.exists():
            result = add_hreflang_to_static(page_path, is_jp=False)
            if result["status"].startswith("✓ Hreflang"):
                fixed += 1
                print(f"  ✓ {result['path']}")
            elif result["status"].startswith("✓ Already"):
                already += 1
                print(f"  ○ {result['path']} — already has hreflang")
            else:
                errors.append(result)
                print(f"  ✗ {result['path']}: {result.get('detail', 'unknown')}")
    
    # Fix JP static pages
    for page_name in JP_STATIC:
        page_path = BASE / page_name
        if page_path.exists():
            result = add_hreflang_to_static(page_path, is_jp=True)
            if result["status"].startswith("✓ Hreflang"):
                fixed += 1
                print(f"  ✓ {result['path']}")
            elif result["status"].startswith("✓ Already"):
                already += 1
            else:
                errors.append(result)
    
    print("\n" + "=" * 60)
    print(f"✅ Hreflang added: {fixed} pages")
    print(f"○ Already had hreflang: {already} pages")
    print(f"✗ Errors: {len(errors)} pages")
    print("=" * 60)


if __name__ == "__main__":
    main()
