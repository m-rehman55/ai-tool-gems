"""
scripts/apply_official_link_to_all_cards.py

Configures Option 1:
1. Adds officialUrl to all 40 commercial tools in app.js and index.html.
2. Updates card(p) in app.js so commercial cards have:
   [ Buy now (WhatsApp) ]
   [ View details ] [ ↗ Official Site ] [ + Cart ]
3. Updates index.html commercial cards pre-rendered HTML to match.
4. Updates styles.css for seamless 3-button layout on commercial cards and 2-button layout on directory cards.
"""

import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COMMERCIAL_OFFICIAL_URLS = {
    'chatgpt': 'https://chatgpt.com',
    'gemini': 'https://gemini.google.com',
    'veo': 'https://deepmind.google/technologies/veo/',
    'leonardo': 'https://leonardo.ai',
    'elevenlabs': 'https://elevenlabs.io',
    'canva': 'https://www.canva.com',
    'figma': 'https://www.figma.com',
    'capcut': 'https://www.capcut.com',
    'adobe': 'https://www.adobe.com',
    'lovable': 'https://lovable.dev',
    'gamma': 'https://gamma.app',
    'replit': 'https://replit.com',
    'n8n': 'https://n8n.io',
    'notion': 'https://www.notion.so',
    'nordvpn': 'https://nordvpn.com',
    'surfshark': 'https://surfshark.com',
    'youtube': 'https://www.youtube.com/premium',
    'netflix': 'https://www.netflix.com',
    'linkedin': 'https://www.linkedin.com/premium',
    'windows': 'https://www.microsoft.com/windows',
    'claude': 'https://claude.ai',
    'midjourney': 'https://www.midjourney.com',
    'cursor': 'https://www.cursor.com',
    'perplexity': 'https://www.perplexity.ai',
    'deepseek': 'https://chat.deepseek.com',
    'grok': 'https://x.ai',
    'runway': 'https://runwayml.com',
    'heygen': 'https://www.heygen.com',
    'grammarly': 'https://www.grammarly.com',
    'quillbot': 'https://quillbot.com',
    'semrush': 'https://www.semrush.com',
    'allinone': 'https://aitoolgems.tech/deals/',
    'tradingview': 'https://www.tradingview.com',
    'kling': 'https://klingai.com',
    'freepik': 'https://www.freepik.com',
    'spotify': 'https://spotify.com',
    'copilot': 'https://github.com/features/copilot',
    'suno': 'https://suno.com',
    'turnitin': 'https://turnitin.com',
    'office365': 'https://www.microsoft.com/microsoft-365'
}

def update_app_js():
    app_js_path = ROOT / "app.js"
    with open(app_js_path, "r", encoding="utf-8") as f:
        js = f.read()

    # Add officialUrl to commercial products
    for slug, url in COMMERCIAL_OFFICIAL_URLS.items():
        pattern = rf"(\{{id:'{slug}',[^}}]+)(intent:\[[^\]]+\])(\}})"
        m = re.search(pattern, js)
        if m and "officialUrl:" not in m.group(0):
            replacement = f"{m.group(1)}{m.group(2)},officialUrl:'{url}'{m.group(3)}"
            js = js[:m.start()] + replacement + js[m.end():]

    # Update commercial card template in card(p)
    # Target the commercial return block:
    old_comm_actions = """      <div class="card-actions">
        <button class="buy-now-card" data-order="${p.id}">${svg('i-whatsapp')} Buy now</button>
        <a class="detail-button" href="tools/${p.id}/">View details</a>
        <button class="add-button${inCart ? ' added' : ''}" data-add="${p.id}" aria-label="${inCart ? 'View ' + p.name + ' in cart' : 'Add ' + p.name + ' to cart'}" aria-pressed="${inCart}">
          ${svg(inCart ? 'i-check' : 'i-plus')}
        </button>
      </div>"""

    new_comm_actions = """      <div class="card-actions">
        <button class="buy-now-card" data-order="${p.id}">${svg('i-whatsapp')} Buy now</button>
        <a class="detail-button" href="tools/${p.id}/">View details</a>
        <a class="official-link-btn" href="${p.officialUrl || '#'}" target="_blank" rel="noopener noreferrer" title="Visit ${p.name} official website" aria-label="Visit ${p.name} official website">
          ${svg('i-external')}
        </a>
        <button class="add-button${inCart ? ' added' : ''}" data-add="${p.id}" aria-label="${inCart ? 'View ' + p.name + ' in cart' : 'Add ' + p.name + ' to cart'}" aria-pressed="${inCart}">
          ${svg(inCart ? 'i-check' : 'i-plus')}
        </button>
      </div>"""

    if old_comm_actions in js:
        js = js.replace(old_comm_actions, new_comm_actions)
        print("Updated commercial card-actions in app.js")
    else:
        print("Note: old_comm_actions pattern already replaced or different in app.js")

    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

def update_index_html():
    index_html_path = ROOT / "index.html"
    with open(index_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    for slug, url in COMMERCIAL_OFFICIAL_URLS.items():
        # Match commercial card actions
        pattern = rf'(<article class="product-card" data-id="{slug}">[\s\S]*?<div class="card-actions">[\s\S]*?<a class="detail-button" href="tools/{slug}/">View details</a>\s*)(<button class="add-button")'
        m = re.search(pattern, html)
        if m:
            title_m = re.search(r'<h3 class="product-title"><a[^>]*>([^<]+)</a></h3>', html[m.start():m.end() + 200])
            name = title_m.group(1) if title_m else slug
            official_link_html = f'<a class="official-link-btn" href="{url}" target="_blank" rel="noopener noreferrer" title="Visit {name} official website" aria-label="Visit {name} official website"><svg><use href="#i-external"></use></svg></a>\n        '
            # Check if not already added
            sub = html[m.start():m.end() + 100]
            if 'official-link-btn' not in sub:
                html = html[:m.start(2)] + official_link_html + html[m.start(2):]

    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html commercial cards successfully.")

def update_styles_css():
    styles_css_path = ROOT / "styles.css"
    with open(styles_css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Update or add card-actions styles
    custom_card_actions_css = """
/* Tri-Action Buttons for Commercial Cards & Dual-Action for Directory Cards */
.card-actions {
  display: grid !important;
  grid-template-columns: 1fr 38px 38px !important;
  gap: 6px !important;
  height: 90px !important;
  margin-top: 14px !important;
}
.card-actions .buy-now-card {
  grid-column: 1 / -1 !important;
  height: 42px !important;
}
.card-actions.directory-actions {
  display: grid !important;
  grid-template-columns: 1fr 42px !important;
  gap: 8px !important;
}
.card-actions.directory-actions .buy-now-card {
  grid-column: 1 / -1 !important;
  height: 42px !important;
}
.card-actions .official-link-btn,
.card-actions .add-button {
  width: 100% !important;
  height: 40px !important;
  min-height: 40px !important;
  padding: 0 !important;
  display: grid !important;
  place-items: center !important;
}
.card-actions .detail-button {
  height: 40px !important;
  min-height: 40px !important;
  display: grid !important;
  place-items: center !important;
  font-size: 11px !important;
  white-space: nowrap !important;
  padding: 0 6px !important;
}
"""
    if "/* Tri-Action Buttons for Commercial Cards" in css:
        # replace existing block
        css = re.sub(r"/\* Tri-Action Buttons[\s\S]*?(?=\n/\* Accessibility|\Z)", custom_card_actions_css.strip() + "\n", css)
    else:
        # insert before Accessibility section
        if "/* Accessibility & Screen Reader Utilities */" in css:
            css = css.replace("/* Accessibility & Screen Reader Utilities */", custom_card_actions_css + "\n/* Accessibility & Screen Reader Utilities */")
        else:
            css += "\n" + custom_card_actions_css

    with open(styles_css_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated styles.css successfully.")

def main():
    update_app_js()
    update_index_html()
    update_styles_css()

if __name__ == "__main__":
    main()

