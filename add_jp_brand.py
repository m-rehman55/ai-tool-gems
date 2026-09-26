#!/usr/bin/env python3
"""
Add brand field to all JP tool Product schemas for better GSC rich results.
"""
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

JP_TOOLS = [
    "chatgpt", "gemini", "veo", "leonardo", "elevenlabs",
    "canva", "figma", "capcut", "adobe", "lovable",
    "gamma", "replit", "n8n", "notion", "nordvpn",
    "surfshark", "youtube", "netflix", "linkedin", "windows", "manus"
]

def tool_brand(tool_name: str) -> str:
    """Return the brand name for each tool."""
    brands = {
        "chatgpt": "OpenAI",
        "gemini": "Google",
        "veo": "Google DeepMind",
        "leonardo": "Leonardo AI",
        "elevenlabs": "ElevenLabs",
        "canva": "Canva",
        "figma": "Figma",
        "capcut": "CapCut",
        "adobe": "Adobe",
        "lovable": "Lovable",
        "gamma": "Gamma",
        "replit": "Replit",
        "n8n": "n8n",
        "notion": "Notion",
        "nordvpn": "Nord Security",
        "surfshark": "Nord Security",
        "youtube": "Google",
        "netflix": "Netflix",
        "linkedin": "Microsoft",
        "windows": "Microsoft",
        "manus": "Manus",
    }
    return brands.get(tool_name, tool_name.title())

def fix_jp_tool_page(page_path: Path, brand_name: str) -> dict:
    """Add brand field to Product schema if not present."""
    try:
        html = page_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"path": str(page_path.relative_to(BASE)), "status": "ERROR", "detail": str(e)}
    
    if '"brand"' in html:
        return {"path": str(page_path.relative_to(BASE)), "status": "✓ Already has brand"}
    
    if '"@type": "Product"' not in html:
        return {"path": str(page_path.relative_to(BASE)), "status": "✗ No Product schema"}
    
    # Find Product block and add brand after image field
    def add_brand(match):
        block = match.group(0)
        # Insert brand after image line
        updated = re.sub(
            r'(\s+"image":\s*"https://aitoolgems\.tech/assets/brand-logo-light\.webp",?\s*\n)(\s+"offers")',
            r'\1      "brand": {\n        "@type": "Brand",\n        "name": "' + brand_name + '"\n      },\n\2',
            block
        )
        if updated == block:
            # Try after description
            updated = re.sub(
                r'(\s+"description":\s*"[^"]*",?\s*\n)(\s+"url":)',
                r'\1      "brand": {\n        "@type": "Brand",\n        "name": "' + brand_name + '"\n      },\n\2',
                block
            )
        return updated
    
    new_html = re.sub(
        r'\{[^{}]*"@type":\s*"Product"[^{}]*\}',
        add_brand,
        html,
        flags=re.DOTALL
    )
    
    if new_html != html:
        try:
            page_path.write_text(new_html, encoding="utf-8")
            return {"path": str(page_path.relative_to(BASE)), "status": "✓ Brand added"}
        except Exception as e:
            return {"path": str(page_path.relative_to(BASE)), "status": "WRITE ERROR", "detail": str(e)}
    else:
        return {"path": str(page_path.relative_to(BASE)), "status": "⚠ Could not add (pattern mismatch)"}


def main():
    print("=" * 60)
    print("🏷 Add Brand to JP Tool Pages")
    print("=" * 60)
    
    fixed = 0
    already = 0
    errors = []
    partial = []
    
    for tool in sorted(JP_TOOLS):
        page = BASE / "jp" / "tools" / tool / "index.html"
        if not page.exists():
            errors.append(f"Missing: {tool}")
            continue
        
        brand = tool_brand(tool)
        result = fix_jp_tool_page(page, brand)
        
        status = result["status"]
        path = result["path"]
        
        if status == "✓ Brand added":
            fixed += 1
            print(f"  ✓ {path} (brand: {brand})")
        elif status.startswith("✓ Already"):
            already += 1
            print(f"  ○ {path} — already has brand")
        elif status.startswith("✗"):
            errors.append(f"{path}: {status}")
            print(f"  ✗ {path}: {status}")
        else:
            partial.append(f"{path}: {status}")
            print(f"  ⚠ {path}: {status}")
    
    print("\n" + "=" * 60)
    print(f"✅ Brand added: {fixed}")
    print(f"○ Already had brand: {already}")
    print(f"⚠ Partial/failed: {len(partial) + len(errors)}")
    if partial:
        print("\nPartial matches:")
        for p in partial:
            print(f"  {p}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  {e}")
    print("=" * 60)


if __name__ == "__main__":
    main()
