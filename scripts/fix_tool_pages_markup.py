#!/usr/bin/env python3
"""
Surgically repairs broken markdown in HTML across all 20 Pakistan tool pages.
Replaces the unclosed <h2>## About ... block with clean semantic HTML.
Removes spammy keyword dumps.
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TOOLS_DIR = BASE / "tools"

def fix_tool_page(html_file: Path) -> bool:
    html = html_file.read_text(encoding="utf-8")
    
    # Pattern to match the broken block
    pattern = re.compile(
        r'<section class="faq-section">\s*<h2>\s*\n+## About ([^\n]+)\n+(.*?)\n+### Key Features\n+(.*?)\n+### Who Should Use This Tool\n+(.*?)\n+### Why Choose AI Tool Gems\?\n+(.*?)\n+### (?:Related Tools|Keywords).*?Frequently asked questions</h2>',
        re.DOTALL
    )
    
    match = pattern.search(html)
    if not match:
        print(f"Skipping (no match): {html_file.relative_to(BASE)}")
        return False
        
    tool_name = match.group(1).strip()
    desc = match.group(2).strip()
    features_raw = match.group(3).strip()
    audience_raw = match.group(4).strip()
    
    # Parse bullet points
    def parse_bullets(text):
        bullets = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                bullets.append(line[2:].strip())
        return bullets
        
    features = parse_bullets(features_raw)
    audience = parse_bullets(audience_raw)
    
    features_html = "\n".join(f"            <li>{f}</li>" for f in features)
    audience_html = "\n".join(f"            <li>{a}</li>" for a in audience)
    
    replacement = f"""    <section class="tool-overview">
      <h2>About {tool_name}</h2>
      <p>{desc}</p>
      <div class="overview-grid">
        <div class="overview-box">
          <h3>Key Features</h3>
          <ul>
{features_html}
          </ul>
        </div>
        <div class="overview-box">
          <h3>Who Should Use This Tool</h3>
          <ul>
{audience_html}
          </ul>
        </div>
        <div class="overview-box">
          <h3>Why Choose AI Tool Gems?</h3>
          <ul>
            <li>Instant 1-click WhatsApp delivery</li>
            <li>Upfront pricing in PKR (EasyPaisa, JazzCash, SadaPay &amp; Bank Transfer)</li>
            <li>1-on-1 human customer support</li>
            <li>Clear private / shared access tiers</li>
            <li>7-day replacement warranty</li>
          </ul>
        </div>
      </div>
    </section>
    <section class="faq-section">
      <h2>Frequently asked questions</h2>"""

    new_html = pattern.sub(replacement, html)
    html_file.write_text(new_html, encoding="utf-8")
    print(f"Repaired: {html_file.relative_to(BASE)}")
    return True

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    count = 0
    for tool_file in sorted(TOOLS_DIR.glob("*/index.html")):
        if fix_tool_page(tool_file):
            count += 1
            
    print(f"\nTotal pages repaired: {count}/20")

if __name__ == "__main__":
    main()
