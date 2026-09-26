#!/usr/bin/env python3
"""
Fix: Add 'image' field to TOP LEVEL of all JSON-LD blocks that use @graph.
Also ensure all schemas have image at the appropriate level.
Google GSC needs image at the top level of the JSON-LD block.
"""
import json
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")
PK_IMAGE = "https://aitoolgems.tech/assets/brand-logo-light.png"
JP_IMAGE = "https://aitoolgems.tech/jp/assets/brand-logo-light.png"


def get_image_url(page_path: Path) -> str:
    rel = page_path.relative_to(BASE)
    if rel.parts[0] == "jp":
        return JP_IMAGE
    return PK_IMAGE


def add_image_to_top_level(block_str: str, image_url: str) -> str:
    """Add image to the top-level of a JSON-LD block."""
    try:
        data = json.loads(block_str.strip())
    except json.JSONDecodeError:
        return block_str
    
    changed = False
    
    # If @graph exists, add image to top level AND ensure all @graph items have image
    if "@graph" in data:
        # Add image at top level
        if "image" not in data:
            data["image"] = image_url
            changed = True
        
        # Also ensure each @graph item has image
        for item in data["@graph"]:
            if isinstance(item, dict) and "image" not in item:
                item["image"] = image_url
                changed = True
    else:
        # Top-level object (no @graph) — add image if missing
        if "image" not in data:
            data["image"] = image_url
            changed = True
    
    if changed:
        new_json = json.dumps(data, indent=2, ensure_ascii=False)
        return new_json
    return block_str


def process_file(page_path: Path) -> dict:
    try:
        html = page_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"file": str(page_path.relative_to(BASE)), "status": "ERROR", "detail": str(e)}
    
    image_url = get_image_url(page_path)
    original = html
    
    pattern = r'(<script type="application/ld\+json">)(.*?)(</script>)'
    
    def replace_block(match):
        open_tag = match.group(1)
        content = match.group(2)
        close_tag = match.group(3)
        new_content = add_image_to_top_level(content, image_url)
        return open_tag + "\n" + new_content + "\n" + close_tag
    
    new_html = re.sub(pattern, replace_block, html, flags=re.DOTALL)
    
    if new_html != original:
        try:
            page_path.write_text(new_html, encoding="utf-8")
            return {"file": str(page_path.relative_to(BASE)), "status": "✓ FIXED"}
        except Exception as e:
            return {"file": str(page_path.relative_to(BASE)), "status": "WRITE ERROR", "detail": str(e)}
    else:
        return {"file": str(page_path.relative_to(BASE)), "status": "✓ OK"}


def main():
    print("=" * 60)
    print("🔧 Fix: Add 'image' to TOP LEVEL of all JSON-LD blocks")
    print("=" * 60)
    
    html_files = sorted(BASE.rglob("*.html"))
    html_files = [f for f in html_files if ".git" not in str(f)]
    
    fixed = 0
    ok = 0
    errors = 0
    
    for f in html_files:
        result = process_file(f)
        if result["status"] == "✓ FIXED":
            fixed += 1
            print(f"  ✓ {result['file']}")
        elif result["status"] == "✓ OK":
            ok += 1
        else:
            errors += 1
            print(f"  ✗ {result['file']}: {result.get('detail', 'unknown')}")
    
    print(f"\n✅ Fixed: {fixed} | Already OK: {ok} | Errors: {errors}")


if __name__ == "__main__":
    main()
