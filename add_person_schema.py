#!/usr/bin/env python3
"""
SEO Step 5: Add Person schema (Author/Team) to about.html pages.
Pakistan + Japan about pages — AI Tool Gems Editorial Team ki Person schema.
"""

import json
import re
from pathlib import Path

BASE = Path(r"D:/ai-tool-gems")

ABOUT_PAGES = {
    BASE / "about.html": {
        "name": "AI Tool Gems Editorial Team",
        "url": "https://aitoolgems.tech/about.html",
        "job_title": "Digital Marketplace Editor",
        "description": "AI Tool Gems is a Pakistan-based independent marketplace that compares AI tools and digital subscriptions with PKR pricing and WhatsApp support.",
        "same_as": [
            "https://www.facebook.com/aitoolgems",
            "https://twitter.com/aitoolgems",
            "https://www.instagram.com/aitoolgems",
        ],
    },
    BASE / "jp" / "about.html": {
        "name": "AI Tool Gems Japan 編集チーム",
        "url": "https://aitoolgems.tech/jp/about.html",
        "job_title": "デジタルマーケットプレイス編集者",
        "description": "AI Tool Gems Japanは、日本のお客様向けにAIツールとデジタルサブスクリプションを比較する独立系マーケットプレイスです。",
        "same_as": [
            "https://www.facebook.com/aitoolgemsjapan",
            "https://twitter.com/aitoolgemsjp",
        ],
    },
}


def add_person_schema_to_page(html: str, person_data: dict) -> str:
    """Add Person JSON-LD schema to about page if not already present."""
    if '"@type": "Person"' in html:
        return html  # Already has Person schema

    person_schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": person_data["name"],
        "url": person_data["url"],
        "jobTitle": person_data["job_title"],
        "description": person_data["description"],
        "sameAs": person_data.get("same_as", []),
    }

    person_json = json.dumps(person_schema, ensure_ascii=False, indent=2)

    # Find existing JSON-LD and add Person to @graph
    jsonld_pattern = re.compile(
        r'(<script\s+type=["\']application/ld\+json["\']>)(.*?)(</script>)',
        re.DOTALL
    )

    def add_person_to_graph(match):
        pre = match.group(1)
        content = match.group(2).strip()
        post = match.group(3)

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return f'{pre}\n{person_json}\n{post}'

        if isinstance(data, dict) and "@graph" in data:
            graph = data["@graph"]
            if not any(isinstance(n, dict) and n.get("@type") == "Person" for n in graph):
                graph.append(json.loads(person_json))
                return f'{pre}\n{json.dumps(data, ensure_ascii=False, indent=2)}\n{post}'
            return match.group(0)
        elif isinstance(data, dict):
            # Single object — wrap in @graph with Person
            graph = [data, json.loads(person_json)]
            wrapped = {"@context": "https://schema.org", "@graph": graph}
            return f'{pre}\n{json.dumps(wrapped, ensure_ascii=False, indent=2)}\n{post}'
        else:
            return match.group(0)

    new_html = jsonld_pattern.sub(add_person_to_graph, html)

    if '"@type": "Person"' not in new_html:
        # Add new JSON-LD block
        if "</head>" in new_html:
            new_html = new_html.replace(
                "</head>",
                f'<script type="application/ld+json">\n{person_json}\n</script>\n</head>'
            )

    return new_html


def update_about_page(page_path: Path, person_data: dict) -> bool:
    """Update about page with Person schema."""
    html = page_path.read_text(encoding="utf-8", errors="replace")

    if '"@type": "Person"' in html:
        print(f"  ⚠ {page_path.relative_to(BASE)}: Person schema already present")
        return False

    new_html = add_person_schema_to_page(html, person_data)

    if '"@type": "Person"' in new_html:
        page_path.write_text(new_html, encoding="utf-8")
        print(f"  ✓ {page_path.relative_to(BASE)}: Person schema added")
        return True

    print(f"  ✗ {page_path.relative_to(BASE)}: Failed to add Person schema")
    return False


def main():
    print("=" * 60)
    print("👤 SEO Step 5: Person Schema for About Pages")
    print("=" * 60)

    added = 0
    for page_path, person_data in ABOUT_PAGES.items():
        if page_path.exists():
            if update_about_page(page_path, person_data):
                added += 1
        else:
            print(f"  ✗ {page_path.relative_to(BASE)}: page not found")

    print("\n" + "=" * 60)
    print(f"✅ Complete!")
    print(f"   Person schemas added: {added}")
    print("=" * 60)


if __name__ == "__main__":
    main()