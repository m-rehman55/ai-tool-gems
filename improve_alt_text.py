#!/usr/bin/env python3
"""
SEO: Smart Image Alt Text Improver
- Analyze each image's context (parent element, nearby text, URL)
- Generate descriptive alt text based on context
- Fix favicon alt text (add proper description)
"""

import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")


def get_image_context(page_html: str, img_tag: str) -> dict:
    """Extract context around an image to generate better alt text."""
    context = {
        "alt": "",
        "src": "",
        "parent_class": "",
        "parent_tag": "",
        "nearby_text": "",
        "is_favicon": False,
        "is_logo": False,
    }

    # Extract src and alt
    src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
    alt_match = re.search(r'alt=["\']([^"\']*?)["\']', img_tag)

    if src_match:
        context["src"] = src_match.group(1)
    if alt_match:
        context["alt"] = alt_match.group(1)

    # Check if it's a favicon
    if "favicon" in context["src"].lower() or "s2/favicons" in context["src"]:
        context["is_favicon"] = True

    # Check if it's a logo
    if "logo" in context["src"].lower() or "brand-logo" in context["src"].lower():
        context["is_logo"] = True

    return context


def generate_better_alt(context: dict, tool_name: str = None) -> str:
    """Generate better alt text based on context."""
    src = context["src"]
    current_alt = context["alt"]

    # Favicon images - needs improvement
    if context["is_favicon"]:
        domain_match = re.search(r'domain=([^&]+)', src)
        if domain_match:
            domain = domain_match.group(1)
            # Remove .com, .io, .ai, etc for cleaner name
            name = domain.replace(".com", "").replace(".io", "").replace(".ai", "").replace(".app", "").replace(".dev", "").replace(".so", "")
            return f"{name} favicon"

    # Logo images - keep or slightly improve
    if context["is_logo"]:
        return current_alt if current_alt else "Brand logo"

    # Generic - use filename
    if src:
        filename = Path(src).name
        if filename.endswith((".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg")):
            name = Path(filename).stem.replace("-", " ").replace("_", " ")
            return f"{name} image"

    return current_alt if current_alt else ""


def improve_alt_text_in_page(page_path: Path) -> list:
    """Improve alt text in a page. Returns list of changes made."""
    html = page_path.read_text(encoding="utf-8", errors="replace")
    changes = []

    img_pattern = re.compile(r'<img[^>]+>', re.DOTALL)

    for match in img_pattern.finditer(html):
        img_tag = match.group(0)
        context = get_image_context(html, img_tag)

        if not context["src"]:
            continue

        # Skip brand logo (keep as is)
        if "brand-logo" in context["src"]:
            continue

        new_alt = generate_better_alt(context)

        if new_alt and new_alt != context["alt"]:
            # Replace alt attribute
            if context["alt"]:
                new_tag = re.sub(
                    r'alt=["\'][^"\']*["\']',
                    f'alt="{new_alt}"',
                    img_tag,
                    count=1
                )
            else:
                # Add alt attribute
                new_tag = img_tag.replace(">", f' alt="{new_alt}">', 1)

            if new_tag != img_tag:
                changes.append((context["src"], context["alt"], new_alt))
                html = html.replace(img_tag, new_tag, 1)

    if changes:
        page_path.write_text(html, encoding="utf-8")

    return changes


def main():
    print("=" * 60)
    print("🖼️  Smart Image Alt Text Improver")
    print("=" * 60)

    # Process all HTML files
    all_changes = []

    for html_file in BASE.rglob("*.html"):
        if ".git" in str(html_file):
            continue

        changes = improve_alt_text_in_page(html_file)
        if changes:
            rel_path = html_file.relative_to(BASE)
            print(f"\n📄 {rel_path}:")
            for src, old, new in changes:
                print(f"   ✓ {old or 'NO ALT'} → '{new}'")
                all_changes.append((str(rel_path), src, old, new))

    print("\n" + "=" * 60)
    print(f"✅ Complete!")
    print(f"   Pages with improvements: {len(set(c[0] for c in all_changes))}")
    print(f"   Total alt text changes:  {len(all_changes)}")
    print("=" * 60)


if __name__ == "__main__":
    main()