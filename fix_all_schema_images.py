#!/usr/bin/env python3
"""
Fix missing 'image' field in all JSON-LD schemas across the site.
Adds brand-logo-light.png as image for Organization, WebSite, WebPage,
LocalBusiness, AboutPage, ItemList, Article, Product, FAQPage, Person schemas.
"""
import json
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

# Image URLs
PK_IMAGE = "https://aitoolgems.tech/assets/brand-logo-light.png"
JP_IMAGE = "https://aitoolgems.tech/jp/assets/brand-logo-light.png"
# For JP pages, use the same brand image (it's in root assets)

def get_image_url(html: str, page_path: Path) -> str:
    """Determine which image URL to use based on page location."""
    rel = page_path.relative_to(BASE)
    parts = rel.parts
    if parts and parts[0] == "jp":
        return JP_IMAGE
    return PK_IMAGE


def add_image_to_schema_block(block_str: str, image_url: str) -> str:
    """
    Add 'image' field to a JSON-LD block if missing.
    Returns modified block string.
    """
    # Parse the JSON
    try:
        data = json.loads(block_str.strip())
    except json.JSONDecodeError:
        return block_str
    
    def add_image(obj):
        """Recursively add image field where needed."""
        if isinstance(obj, dict):
            schema_type = obj.get("@type")
            if isinstance(schema_type, list):
                schema_type = schema_type[0] if schema_type else None
            
            types_needing_image = [
                "Organization", "WebSite", "WebPage", "LocalBusiness",
                "AboutPage", "ItemList", "Article", "Product", "FAQPage",
                "Person", "BlogPosting", "CollectionPage"
            ]
            
            if schema_type in types_needing_image and "image" not in obj:
                obj["image"] = image_url
            
            # Recurse
            for key, val in list(obj.items()):
                if key not in ("@context", "@type", "@id", "image"):
                    add_image(val)
        elif isinstance(obj, list):
            for item in obj:
                add_image(item)
    
    add_image(data)
    
    # Re-serialize with proper indentation
    new_json = json.dumps(data, indent=2, ensure_ascii=False)
    return new_json


def process_file(page_path: Path) -> dict:
    """Process one HTML file. Returns stats."""
    try:
        html = page_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"file": str(page_path.relative_to(BASE)), "status": "ERROR", "detail": str(e), "changes": 0}
    
    image_url = get_image_url(html, page_path)
    original_html = html
    
    # Find all JSON-LD script blocks
    pattern = r'(<script type="application/ld\+json">)(.*?)(</script>)'
    
    changes = 0
    def replace_block(match):
        nonlocal changes
        open_tag = match.group(1)
        block_content = match.group(2)
        close_tag = match.group(3)
        
        new_content = add_image_to_schema_block(block_content, image_url)
        if new_content != block_content:
            changes += 1
        
        return open_tag + "\n" + new_content + "\n" + close_tag
    
    new_html = re.sub(pattern, replace_block, html, flags=re.DOTALL)
    
    if new_html != original_html:
        try:
            page_path.write_text(new_html, encoding="utf-8")
            return {
                "file": str(page_path.relative_to(BASE)),
                "status": "✓ FIXED",
                "changes": changes,
                "detail": f"Added image to {changes} schema block(s)"
            }
        except Exception as e:
            return {"file": str(page_path.relative_to(BASE)), "status": "WRITE ERROR", "detail": str(e), "changes": 0}
    else:
        return {"file": str(page_path.relative_to(BASE)), "status": "✓ OK", "changes": 0, "detail": "All schemas already have image"}


def main():
    print("=" * 60)
    print("🛠️  Fix Missing 'image' in All JSON-LD Schemas")
    print("=" * 60)
    
    html_files = sorted(BASE.rglob("*.html"))
    html_files = [f for f in html_files if ".git" not in str(f)]
    
    results = {"fixed": [], "ok": [], "errors": []}
    
    for html_file in html_files:
        result = process_file(html_file)
        rel = result["file"]
        
        if result["status"] == "✓ FIXED":
            results["fixed"].append(result)
            print(f"  ✓ {rel}: +{result['changes']} image(s)")
        elif result["status"] == "✓ OK":
            results["ok"].append(result)
        else:
            results["errors"].append(result)
            print(f"  ✗ {rel}: {result['detail']}")
    
    print("\n" + "=" * 60)
    print(f"✅ Fixed: {len(results['fixed'])} files")
    print(f"✓ Already OK: {len(results['ok'])} files")
    print(f"✗ Errors: {len(results['errors'])} files")
    print("=" * 60)


if __name__ == "__main__":
    main()
