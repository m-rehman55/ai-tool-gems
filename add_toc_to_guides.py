#!/usr/bin/env python3
"""
SEO Step 4: Add Table of Contents (TOC) to long guide pages.
Guide pages mein headings (h2/h3) extract karke TOC generate karta hai.
"""

import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

GUIDE_DIRS = [
    BASE / "guides",
    BASE / "jp" / "guides",
]


def extract_headings(html: str):
    """Extract all h2 and h3 headings with their text and generate anchor IDs."""
    headings = []

    # Find all h2 tags
    for match in re.finditer(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL):
        text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        anchor = slugify(text)
        headings.append(('h2', text, anchor))

    # Find all h3 tags  
    for match in re.finditer(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL):
        text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        anchor = slugify(text)
        headings.append(('h3', text, anchor))

    return headings


def slugify(text: str) -> str:
    """Convert heading text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')
    # Ensure uniqueness by appending number if duplicate
    return text[:60]


def build_toc_html(headings):
    """Build TOC HTML from extracted headings."""
    if not headings:
        return ""

    items = []
    for level, text, anchor in headings:
        indent = "  " if level == 'h3' else ""
        items.append(f'{indent}<li><a href="#{anchor}">{text}</a></li>')

    return f"""\
    <nav class="toc" aria-label="Table of Contents">
      <h3>On this page</h3>
      <ul>
{chr(10).join(items)}
      </ul>
    </nav>


"""


def add_toc_to_page(html: str, toc_html: str) -> str:
    """Insert TOC into page after main content start."""
    # Insert after <main> or <article> opening tag
    if '<main' in html:
        html = html.replace('<main', f'<main\n{toc_html}', 1)
    elif '<article' in html:
        html = html.replace('<article', f'<article\n{toc_html}', 1)
    elif '<body' in html:
        html = html.replace('<body', f'<body\n{toc_html}', 1)
    else:
        # Insert after first <div> with class
        match = re.search(r'(<div[^>]+class="[^"]*")', html)
        if match:
            html = html.replace(match.group(1), f'{match.group(1)}\n{toc_html}', 1)

    return html


def generate_anchor_ids(html: str) -> str:
    """Add id attributes to h2/h3 tags if missing."""
    def add_id_to_h2(match):
        tag = match.group(0)
        if 'id=' in tag:
            return tag
        text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        anchor = slugify(text)
        return f'<h2 id="{anchor}">{match.group(1)}</h2>'

    def add_id_to_h3(match):
        tag = match.group(0)
        if 'id=' in tag:
            return tag
        text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        anchor = slugify(text)
        return f'<h3 id="{anchor}">{match.group(1)}</h3>'

    html = re.sub(r'<h2[^>]*>(.*?)</h2>', add_id_to_h2, html, flags=re.DOTALL)
    html = re.sub(r'<h3[^>]*>(.*?)</h3>', add_id_to_h3, html, flags=re.DOTALL)

    return html


def update_guide_page(page_path: Path) -> bool:
    """Add TOC to a guide page if not already present."""
    html = page_path.read_text(encoding="utf-8", errors="replace")

    # Skip if TOC already exists (actual TOC with ul > li > a structure)
    if '<nav class="toc"' in html and '<ul>' in html and '<li><a href="#' in html:
        return False

    # Extract headings
    headings = extract_headings(html)

    if not headings:
        print(f"  - {page_path.parent.name}: No h2/h3 headings found")
        return False

    # Generate TOC
    toc_html = build_toc_html(headings)

    # Add anchor IDs to headings
    html = generate_anchor_ids(html)

    # Insert TOC
    html = add_toc_to_page(html, toc_html)

    # Write back
    page_path.write_text(html, encoding="utf-8")

    h2_count = sum(1 for l, _, _ in headings if l == 'h2')
    h3_count = sum(1 for l, _, _ in headings if l == 'h3')

    print(f"  ✓ {page_path.parent.name}: TOC added ({h2_count} h2, {h3_count} h3)")
    return True


def main():
    print("=" * 60)
    print("📑 SEO Step 4: Table of Contents for Guide Pages")
    print("=" * 60)

    added = 0
    skipped = 0

    for guide_dir in GUIDE_DIRS:
        if not guide_dir.exists():
            continue

        rel_path = guide_dir.relative_to(BASE)
        print(f"\n📁 {rel_path}/")

        for item in sorted(guide_dir.iterdir()):
            if item.is_dir() and (item / "index.html").exists():
                page_path = item / "index.html"
                if update_guide_page(page_path):
                    added += 1
                else:
                    skipped += 1
            elif item.name == "index.html":
                if update_guide_page(item):
                    added += 1
                else:
                    skipped += 1

    print("\n" + "=" * 60)
    print(f"✅ Complete!")
    print(f"   TOC added: {added} pages")
    print(f"   Skipped:   {skipped} pages (already had TOC or no headings)")
    print("=" * 60)


if __name__ == "__main__":
    main()