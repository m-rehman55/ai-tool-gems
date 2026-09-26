#!/usr/bin/env python3
"""
Permanent Fix: Update image URLs in ALL JP pages to use correct path.
The file brand-logo-light.webp exists at root assets/, not jp/assets/.
Also update Product schema brand for better GSC rich results.
"""
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

# Correct image URL (exists on live site)
CORRECT_IMAGE = "https://aitoolgems.tech/assets/brand-logo-light.webp"
# JP-specific branding
JP_LOGO_HTML = "AI Tool Gems Japan logo"

# Pages to fix (JP pages that reference jp/assets/brand-logo-light.webp)
JP_TOOLS = [
    "chatgpt", "gemini", "veo", "leonardo", "elevenlabs",
    "canva", "figma", "capcut", "adobe", "lovable",
    "gamma", "replit", "n8n", "notion", "nordvpn",
    "surfshark", "youtube", "netflix", "linkedin", "windows", "manus"
]

def fix_jp_page(page_path: Path) -> dict:
    """Fix image URLs in a JP page. Returns status."""
    try:
        html = page_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"path": str(page_path), "status": "ERROR", "detail": str(e)}
    
    original = html
    
    # 1. Fix JSON-LD image URLs: jp/assets/brand-logo-light.webp -> assets/brand-logo-light.webp
    # But keep the URL as https://aitoolgems.tech/assets/brand-logo-light.webp (full URL, works for GSC)
    html = re.sub(
        r'("image"\s*:\s*")https://aitoolgems\.tech/jp/assets/brand-logo-light\.webp(")',
        r'\1' + CORRECT_IMAGE + r'\2',
        html
    )
    
    # 2. Fix any relative references: ../assets/brand-logo-light.webp is correct for body images
    # Don't change those - they resolve correctly
    
    # 3. Add brand to Product schema if missing (for better rich results)
    def add_brand_to_product(match):
        block = match.group(0)
        # Check if brand already exists
        if '"brand"' in block:
            return block
        # Add brand after the opening of Product object
        # Find: "Product",\n      "name": ... and add brand after name or description
        updated = re.sub(
            r'(\s{2,}"description":\s*"[^"]*"),?\s*\n(\s{2,}"url":)',
            r'\1,\n\2      "brand": {\n        "@type": "Brand",\n        "name": "OpenAI"\n      },\n\3',
            block
        )
        if updated != block:
            return updated
        # Try after "url" line
        updated = re.sub(
            r'(\s{2,}"url":\s*"[^"]*"),?\s*\n(\s{2,}"category")',
            r'\1,\n\2      "brand": {\n        "@type": "Brand",\n        "name": "OpenAI"\n      },\n\3',
            block
        )
        return updated
    
    # Apply brand fix to Product schemas
    html = re.sub(
        r'\{[^{}]*"@type":\s*"Product"[^{}]*\}',
        add_brand_to_product,
        html
    )
    
    if html != original:
        try:
            page_path.write_text(html, encoding="utf-8")
            return {"path": str(page_path.relative_to(BASE)), "status": "✓ FIXED"}
        except Exception as e:
            return {"path": str(page_path.relative_to(BASE)), "status": "WRITE ERROR", "detail": str(e)}
    else:
        return {"path": str(page_path.relative_to(BASE)), "status": "✓ OK (no changes needed)"}


def main():
    print("=" * 60)
    print("🔧 Permanent Fix: Update JP page image URLs + add brand")
    print("=" * 60)
    
    results = {"fixed": [], "ok": [], "errors": []}
    
    # Fix JP tool pages
    jp_tools_dir = BASE / "jp" / "tools"
    for tool_dir in sorted(jp_tools_dir.iterdir()):
        if tool_dir.is_dir():
            page = tool_dir / "index.html"
            if page.exists():
                result = fix_jp_page(page)
                if result["status"] == "✓ FIXED":
                    results["fixed"].append(result["path"])
                    print(f"  ✓ {result['path']}")
                elif result["status"] == "✓ OK (no changes needed)":
                    results["ok"].append(result["path"])
                    print(f"  ○ {result['path']} — already correct")
                else:
                    results["errors"].append(result)
                    print(f"  ✗ {result['path']}: {result.get('detail', 'unknown')}")
    
    # Fix jp index page
    jp_index = BASE / "jp" / "index.html"
    if jp_index.exists():
        result = fix_jp_page(jp_index)
        if result["status"] == "✓ FIXED":
            results["fixed"].append(result["path"])
            print(f"  ✓ {result['path']}")
        elif result["status"].startswith("✓ OK"):
            results["ok"].append(result["path"])
        else:
            results["errors"].append(result)
    
    print("\n" + "=" * 60)
    print(f"✅ Fixed: {len(results['fixed'])} pages")
    print(f"○ Already correct: {len(results['ok'])} pages")
    print(f"✗ Errors: {len(results['errors'])} pages")
    print("=" * 60)
    
    if results["errors"]:
        print("\nErrors detail:")
        for e in results["errors"]:
            print(f"  {e}")


if __name__ == "__main__":
    main()
