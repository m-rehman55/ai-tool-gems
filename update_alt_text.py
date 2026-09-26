#!/usr/bin/env python3
"""
SEO Step 3: Image Alt Text Audit + Product Schema
- Check all img tags for alt text
- Add missing alt text based on context
- Add Product JSON-LD schema to tool pages (if missing)
"""

import re
import json
from pathlib import Path
from urllib.parse import urljoin

BASE = Path(r"D:/ai-tool-gems")

# Alt text replacement rules (generic → specific)
ALT_RULES = [
    # Generic alt → descriptive
    ("logo", "AI Tool Gems logo"),
    ("brand", "AI Tool Gems brand logo"),
    ("favicon", ""),  # Leave favicon alt empty — decorative
    ("", None),  # Empty alt — skip (will be filled from context)
]

# Tool-specific default alt text
TOOL_IMAGE_ALTS = {
    "chatgpt": "ChatGPT Plus interface screenshot",
    "gemini": "Google Gemini Pro interface screenshot",
    "veo": "Google Veo 3 Ultra AI video generation interface",
    "leonardo": "Leonardo AI image generation dashboard",
    "elevenlabs": "ElevenLabs AI voice generation interface",
    "canva": "Canva Pro design editor interface",
    "figma": "Figma interface design editor",
    "capcut": "CapCut Pro video editing interface",
    "adobe": "Adobe Creative Cloud suite screenshot",
    "lovable": "Lovable AI app builder interface",
    "gamma": "Gamma AI presentation tool interface",
    "replit": "Replit AI coding environment screenshot",
    "n8n": "n8n workflow automation dashboard",
    "notion": "Notion workspace dashboard interface",
    "nordvpn": "NordVPN VPN service interface",
    "surfshark": "Surfshark VPN service interface",
    "youtube": "YouTube Premium interface screenshot",
    "netflix": "Netflix streaming interface screenshot",
    "linkedin": "LinkedIn Premium professional network interface",
    "windows": "Windows 11 Pro desktop screenshot",
}


def extract_img_info(img_tag: str) -> dict:
    """Extract src, alt, width, height from img tag."""
    src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
    alt_match = re.search(r'alt=["\']([^"\']*?)["\']', img_tag)
    width_match = re.search(r'width=["\']([^"\']+)["\']', img_tag)
    height_match = re.search(r'height=["\']([^"\']+)["\']', img_tag)
    return {
        "src": src_match.group(1) if src_match else "",
        "alt": alt_match.group(1) if alt_match else "",
        "width": width_match.group(1) if width_match else "",
        "height": height_match.group(1) if height_match else "",
        "tag": img_tag,
    }


def determine_alt_text(img_info: dict, tool_name: str, base_url: str) -> str | None:
    """Determine appropriate alt text for an image."""
    alt = img_info["alt"]
    src = img_info["src"]
    width = img_info["width"]
    height = img_info["height"]

    # If alt already present and meaningful, keep it
    if alt and alt.strip() and len(alt.strip()) > 2:
        return None  # No change needed

    # If it's a favicon, leave empty
    if "favicon" in src.lower() or "s2/favicons" in src:
        return ""

    # If it's a logo
    if "logo" in src.lower() or "brand" in src.lower():
        return "AI Tool Gems logo"

    # If it has width/height and looks like a product screenshot
    if width and height and (int(width) > 100 or int(height) > 100):
        # Try to find tool-specific alt
        if tool_name in TOOL_IMAGE_ALTS:
            return TOOL_IMAGE_ALTS[tool_name]

    # Generic: use filename
    if src:
        filename = Path(urljoin(base_url, src)).name
        if filename.endswith((".webp", ".png", ".jpg", ".jpeg", ".gif")):
            name = Path(filename).stem.replace("-", " ").replace("_", " ")
            return f"{name} image"

    return None


def add_product_schema_to_page(html: str, tool_name: str, price: str) -> str:
    """Add Product JSON-LD schema to a page if missing."""
    if '"@type": "Product"' in html:
        return html  # Already has Product schema

    # Check what's in existing JSON-LD
    jsonld_pattern = re.compile(
        r'(<script\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)',
        re.DOTALL
    )

    # Build Product schema
    product_schema = f"""  {{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "{tool_name.replace('-', ' ').title()}",
    "description": "AI Tool Gems listing for {tool_name}",
    "offers": {{
      "@type": "Offer",
      "price": "{price}",
      "priceCurrency": "PKR",
      "availability": "https://schema.org/InStock",
      "url": "https://aitoolgems.tech/tools/{tool_name}/"
    }}
  }}"""

    # Try to add to existing @graph
    def add_product_to_graph(match):
        pre = match.group(1)
        content = match.group(2).strip()
        post = match.group(3)
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return f"{pre}\n{product_schema}\n{post}"

        if isinstance(data, dict):
            if "@graph" in data:
                graph = data["@graph"]
                if not any(isinstance(n, dict) and n.get("@type") == "Product" for n in graph):
                    graph.append(json.loads(product_schema))
                    data["@graph"] = graph
                    return f"{pre}\n{json.dumps(data, ensure_ascii=False, indent=2)}\n{post}"
            else:
                # Single object — wrap in @graph with Product
                graph = [data, json.loads(product_schema)]
                wrapped = {"@context": "https://schema.org", "@graph": graph}
                return f"{pre}\n{json.dumps(wrapped, ensure_ascii=False, indent=2)}\n{post}"
        return match.group(0)

    new_html = jsonld_pattern.sub(add_product_to_graph, html)

    if '"@type": "Product"' not in new_html:
        # Add new JSON-LD block before </head>
        if "</head>" in new_html:
            new_html = new_html.replace(
                "</head>",
                f'<script type="application/ld+json">\n{product_schema}\n</script>\n</head>'
            )
        elif "<body>" in new_html:
            new_html = new_html.replace(
                "<body>",
                f'<script type="application/ld+json">\n{product_schema}\n</script>\n<body>',
                1
            )

    return new_html


def audit_alt_text(page_path: Path, tool_name: str) -> tuple[list, list, str]:
    """Audit image alt text on a page. Returns (missing, fixed, updated_html)."""
    html = page_path.read_text(encoding="utf-8", errors="replace")
    img_pattern = re.compile(r'<img[^>]+>', re.DOTALL)

    missing: list = []
    fixed: list = []

    for match in img_pattern.finditer(html):
        img_tag = match.group(0)
        img_info = extract_img_info(img_tag)

        if not img_info["src"]:
            continue

        alt_needed = determine_alt_text(img_info, tool_name, str(page_path.parent))

        if alt_needed is None:
            continue  # No change needed

        if alt_needed == "":
            # Remove empty alt (decorative image)
            if img_info["alt"] == "":
                new_tag = img_tag.replace('alt=""', 'alt=""')
                if new_tag != img_tag:
                    fixed.append((img_info["src"], "alt cleared (decorative)"))
                    html = html.replace(img_tag, new_tag, 1)
            continue

        # Add/Update alt text
        if img_info["alt"] == "":
            # Empty alt — add descriptive
            new_tag = re.sub(
                r'alt=""',
                f'alt="{alt_needed}"',
                img_tag,
                count=1
            )
        else:
            # Has alt but it's too short/generic — replace
            new_tag = re.sub(
                r'alt=["\'][^"\']*["\']',
                f'alt="{alt_needed}"',
                img_tag,
                count=1
            )

        if new_tag != img_tag:
            fixed.append((img_info["src"], alt_needed))
            html = html.replace(img_tag, new_tag, 1)

    # Also check for images without alt attribute at all
    img_no_alt_pattern = re.compile(r'<img(?![^>]*alt=)[^>]+>', re.DOTALL)
    for match in img_no_alt_pattern.finditer(html):
        img_tag = match.group(0)
        img_info = extract_img_info(img_tag)
        if not img_info["src"]:
            continue

        alt_text = determine_alt_text(img_info, tool_name, str(page_path.parent))
        if alt_text:
            if alt_text == "":
                new_tag = img_tag.replace(">", ' alt="">', 1)
            else:
                new_tag = img_tag.replace(">", f' alt="{alt_text}">', 1)
            if new_tag != img_tag:
                fixed.append((img_info["src"], alt_text))
                html = html.replace(img_tag, new_tag, 1)

    return missing, fixed, html


def main():
    import json

    print("=" * 60)
    print("🖼️  SEO Step 3: Image Alt Text Audit + Product Schema")
    print("=" * 60)

    # Tool pages
    tool_dirs = [
        (BASE / "tools", "PK"),
        (BASE / "jp" / "tools", "JP"),
    ]

    total_missing = 0
    total_fixed = 0
    total_product_schema_added = 0

    # Tool prices (matching what we have)
    TOOL_PRICES = {
        "chatgpt": "2300",
        "gemini": "800",
        "veo": "2100",
        "leonardo": "1900",
        "elevenlabs": "3300",
        "canva": "900",
        "figma": "3000",
        "capcut": "900",
        "adobe": "1700",
        "lovable": "1600",
        "gamma": "23000",
        "replit": "3200",
        "n8n": "7000",
        "notion": "2200",
        "nordvpn": "1800",
        "surfshark": "800",
        "youtube": "1200",
        "netflix": "400",
        "linkedin": "1500",
        "windows": "1900",
    }

    for tool_dir, region in tool_dirs:
        if not tool_dir.exists():
            print(f"\n⚠ Directory not found: {tool_dir}")
            continue

        rel_path = tool_dir.relative_to(BASE)
        print(f"\n📁 {rel_path}/")

        for tool_dir_name in sorted(tool_dir.iterdir()):
            if not tool_dir_name.is_dir():
                continue

            page_path = tool_dir_name / "index.html"
            if not page_path.exists():
                print(f"  ✗ {tool_dir_name.name}: page not found")
                continue

            html = page_path.read_text(encoding="utf-8", errors="replace")

            # Audit alt text
            missing, fixed, updated_html = audit_alt_text(page_path, tool_dir_name.name)

            if fixed:
                # Write back updated HTML
                page_path.write_text(updated_html, encoding="utf-8")
                for src, alt in fixed:
                    print(f"  + {tool_name}: alt='{alt}' — {src}")
                total_fixed += len(fixed)

            # Add Product schema if missing
            price = TOOL_PRICES.get(tool_dir_name.name, "0")
            if '"@type": "Product"' not in updated_html:
                updated_html = add_product_schema_to_page(updated_html, tool_dir_name.name, price)
                if '"@type": "Product"' in updated_html:
                    page_path.write_text(updated_html, encoding="utf-8")
                    print(f"  + {tool_dir_name.name}: Product schema added")
                    total_product_schema_added += 1

    print("\n" + "=" * 60)
    print("✅ Complete!")
    print(f"   Alt text fixed: {total_fixed} images")
    print(f"   Product schemas added: {total_product_schema_added}")
    print("=" * 60)


if __name__ == "__main__":
    main()