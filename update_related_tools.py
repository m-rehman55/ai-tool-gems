#!/usr/bin/env python3
"""
SEO Step 2: Add 3-4 related tools links to every tool page's related-tools section.
Pakistan + Japan, 20 tools each = 40 pages.
"""

import re
import json
from pathlib import Path

BASE = Path(r"D:\ai-tool-gems")

# ── Related tools mapping ─────────────────────────────────────────────────
# Har tool ke liye 3-4 related tools (course ke mutabiq: same category / workflow)

RELATED_TOOLS = {
    "chatgpt": [
        ("gemini", "Gemini Pro"),
        ("notion", "Notion Business"),
        ("elevenlabs", "ElevenLabs"),
    ],
    "gemini": [
        ("chatgpt", "ChatGPT Plus"),
        ("canva", "Canva Pro Edu"),
        ("n8n", "n8n Starter"),
    ],
    "veo": [
        ("capcut", "CapCut Pro"),
        ("adobe", "Adobe Creative Cloud"),
        ("elevenlabs", "ElevenLabs"),
    ],
    "leonardo": [
        ("canva", "Canva Pro Edu"),
        ("figma", "Figma Pro Private"),
        ("adobe", "Adobe Creative Cloud"),
    ],
    "elevenlabs": [
        ("chatgpt", "ChatGPT Plus"),
        ("capcut", "CapCut Pro"),
        ("adobe", "Adobe Creative Cloud"),
    ],
    "canva": [
        ("figma", "Figma Pro Private"),
        ("adobe", "Adobe Creative Cloud"),
        ("gamma", "Gamma Pro"),
    ],
    "figma": [
        ("canva", "Canva Pro Edu"),
        ("adobe", "Adobe Creative Cloud"),
        ("lovable", "Lovable Pro"),
    ],
    "capcut": [
        ("veo", "Veo 3 Ultra"),
        ("elevenlabs", "ElevenLabs"),
        ("adobe", "Adobe Creative Cloud"),
    ],
    "adobe": [
        ("canva", "Canva Pro Edu"),
        ("figma", "Figma Pro Private"),
        ("capcut", "CapCut Pro"),
    ],
    "lovable": [
        ("replit", "Replit Core"),
        ("n8n", "n8n Starter"),
        ("figma", "Figma Pro Private"),
    ],
    "gamma": [
        ("notion", "Notion Business"),
        ("canva", "Canva Pro Edu"),
        ("lovable", "Lovable Pro"),
    ],
    "replit": [
        ("lovable", "Lovable Pro"),
        ("n8n", "n8n Starter"),
        ("chatgpt", "ChatGPT Plus"),
    ],
    "n8n": [
        ("replit", "Replit Core"),
        ("gemini", "Gemini Pro"),
        ("notion", "Notion Business"),
    ],
    "notion": [
        ("gamma", "Gamma Pro"),
        ("n8n", "n8n Starter"),
        ("adobe", "Adobe Creative Cloud"),
    ],
    "nordvpn": [
        ("surfshark", "Surfshark VPN"),
        ("youtube", "YouTube Premium"),
        ("netflix", "Netflix Premium 4K"),
    ],
    "surfshark": [
        ("nordvpn", "NordVPN"),
        ("youtube", "YouTube Premium"),
        ("netflix", "Netflix Premium 4K"),
    ],
    "youtube": [
        ("netflix", "Netflix Premium 4K"),
        ("nordvpn", "NordVPN"),
        ("surfshark", "Surfshark VPN"),
    ],
    "netflix": [
        ("youtube", "YouTube Premium"),
        ("nordvpn", "NordVPN"),
        ("surfshark", "Surfshark VPN"),
    ],
    "linkedin": [
        ("notion", "Notion Business"),
        ("gamma", "Gamma Pro"),
        ("chatgpt", "ChatGPT Plus"),
    ],
    "windows": [
        ("adobe", "Adobe Creative Cloud"),
        ("replit", "Replit Core"),
        ("lovable", "Lovable Pro"),
    ],
}


# ── Related tools section HTML ────────────────────────────────────────────

def build_related_tools_html(tool_name, related):
    """Build related tools HTML section (replaces existing related-tools section)."""
    links_html = ""
    for slug, label in related:
        links_html += f'        <a href="../{slug}/">{label}</a> and '

    # Remove trailing " and "
    links_html = links_html.rstrip(" and ")

    return f"""    <section class="answer related-tools">
      <h2>Compare related tools before ordering</h2>
      <p>If {tool_name} does not fully match your workflow, compare {links_html}. You can also use our <a href="../../guides/">comparison guides</a> for task-based guidance and current PKR listing data.</p>
    </section>
"""


# ── Update one page ───────────────────────────────────────────────────────

def update_related_tools(page_path: Path, tool_name: str, related: list):
    """Update the related-tools section of one tool page."""
    html = page_path.read_text(encoding="utf-8", errors="replace")

    new_section = build_related_tools_html(tool_name, related)

    # Replace existing related-tools section if present
    pattern = re.compile(
        r'<section class="answer related-tools">.*?</section>',
        re.DOTALL
    )

    if pattern.search(html):
        html = pattern.sub(new_section, html)
        page_path.write_text(html, encoding="utf-8")
        return "updated"
    else:
        # No related-tools section found — add before <section class="faq-section"> or </main>
        if "<section class=\"faq-section\">" in html:
            html = html.replace(
                '<section class="faq-section">',
                new_section + '\n    <section class="faq-section">'
            )
            page_path.write_text(html, encoding="utf-8")
            return "added"
        elif "</main>" in html:
            html = html.replace("</main>", new_section + "</main>")
            page_path.write_text(html, encoding="utf-8")
            return "added"
        else:
            return "no_insert_point"


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🔗 SEO Step 2: Internal Linking — Related Tools")
    print("=" * 60)

    for tool_dir in [BASE / "tools", BASE / "jp" / "tools"]:
        if not tool_dir.exists():
            continue

        rel = tool_dir.relative_to(BASE)
        print(f"\n📁 {rel}/")

        for tool_name, related in RELATED_TOOLS.items():
            page_path = tool_dir / tool_name / "index.html"
            if not page_path.exists():
                print(f"  ✗ {tool_name}: page not found")
                continue

            result = update_related_tools(page_path, tool_name, related)
            if result == "updated":
                print(f"  ✓ {tool_name}: related tools updated")
            elif result == "added":
                print(f"  + {tool_name}: related tools section added")
            else:
                print(f"  ✗ {tool_name}: {result}")

    print("\n" + "=" * 60)
    print("✅ Internal linking update complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
