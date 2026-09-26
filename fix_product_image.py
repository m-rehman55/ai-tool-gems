#!/usr/bin/env python3
"""
Add 'image' field to Product schema in all tool pages.
Fixes GSC critical error: "Missing field 'image'"
"""
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

PK_IMAGE = "https://aitoolgems.tech/assets/brand-logo-light.webp"
JP_IMAGE = "https://aitoolgems.tech/jp/assets/brand-logo-light.webp"


def add_image_to_product_schema(html: str, image_url: str) -> tuple[str, bool]:
    """
    Add 'image' field to Product schema if missing.
    Returns (new_html, changed)
    """
    # Pattern: Product type object without image field
    # We look for the Product schema block and add image after a known field
    
    # Check if image already exists
    if '"image"' in html:
        return html, False
    
    # Find Product schema block (first @type: "Product" in @graph)
    # Pattern: "image" is missing - we add it after "inLanguage" line
    # or after "url" line or after "description" line
    
    # Strategy: find the Product object and insert image field
    # Look for: "category": "..." followed eventually by "inLanguage": "...",
    # or just insert after "description": "..."
    
    def add_image_after_description(match):
        block = match.group(0)
        if '"image"' in block:
            return block
        # Add image field after description line
        # Find the description line and add image after it
        desc_pattern = r'(\s+"description":\s*"[^"]*"),?\s*\n'
        replacement = r'\1,\n      "image": "' + image_url + '",\n'
        new_block, count = re.subn(desc_pattern, replacement, block, count=1)
        if count:
            return new_block
        return block
    
    # First, try to find and fix within each Product object
    # The Product schema is usually the first item in @graph
    pattern = r'\{[^}]*"@type":\s*"Product"[^}]*\}'
    
    new_html = re.sub(pattern, add_image_after_description, html, count=1)
    
    changed = new_html != html
    return new_html, changed


def process_tool_page(page_path: Path, image_url: str) -> tuple[str, str, bool, str]:
    """Process one tool page. Returns (name, status, changed, detail)"""
    tool_name = page_path.parent.name
    try:
        html = page_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return tool_name, "ERROR", False, str(e)
    
    new_html, changed = add_image_to_product_schema(html, image_url)
    
    if changed:
        try:
            page_path.write_text(new_html, encoding="utf-8")
            return tool_name, "✓ UPDATED", True, "Added image to Product schema"
        except Exception as e:
            return tool_name, "ERROR", False, f"Write failed: {e}"
    else:
        return tool_name, "⚠ NO CHANGE", False, "image already present or Product schema not found"


def main():
    print("=" * 60)
    print("🤖 AI Tool Gems — GSC Image Field Fix")
    print("Adding 'image' to Product schema (critical GSC fix)")
    print("=" * 60)
    
    results = {"updated": [], "no_change": [], "errors": []}
    
    # Process PK tool pages
    print("\n📁 tools/ (Pakistan)")
    pk_tools_dir = BASE / "tools"
    if pk_tools_dir.exists():
        for tool_dir in sorted(pk_tools_dir.iterdir()):
            if tool_dir.is_dir():
                page = tool_dir / "index.html"
                if page.exists():
                    name, status, changed, detail = process_tool_page(page, PK_IMAGE)
                    print(f"   {status}: {name} — {detail}")
                    if changed:
                        results["updated"].append(name)
                    elif "NO CHANGE" in status:
                        results["no_change"].append(name)
                    else:
                        results["errors"].append(f"{name}: {detail}")
    
    # Process JP tool pages
    print("\n📁 jp/tools/ (Japan)")
    jp_tools_dir = BASE / "jp" / "tools"
    if jp_tools_dir.exists():
        for tool_dir in sorted(jp_tools_dir.iterdir()):
            if tool_dir.is_dir():
                page = tool_dir / "index.html"
                if page.exists():
                    name, status, changed, detail = process_tool_page(page, JP_IMAGE)
                    print(f"   {status}: {name} — {detail}")
                    if changed:
                        results["updated"].append(f"jp-{name}")
                    elif "NO CHANGE" in status:
                        results["no_change"].append(f"jp-{name}")
                    else:
                        results["errors"].append(f"jp-{name}: {detail}")
    
    print("\n" + "=" * 60)
    print(f"✅ FIXED: {len(results['updated'])} pages — image added to Product schema")
    print(f"⚠ ALREADY: {len(results['no_change'])} pages — image already present")
    print(f"❌ ERRORS: {len(results['errors'])} pages")
    if results["errors"]:
        for e in results["errors"]:
            print(f"   {e}")
    print("=" * 60)


if __name__ == "__main__":
    main()
