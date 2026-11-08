"""
scripts/harmonize_homepage_cards.py - Perfectly synchronizes app.js and index.html
so all 25 directory cards follow the exact same visual design system, specs format,
and clean bold PKR pricing as the original 40 commercial cards.
"""

import re
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from directory_tools_data import DIRECTORY_TOOLS

CLEAN_DIRECTORY_METADATA = {
    'windsurf': {'pkr': 'Rs. 5,600', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': '$20 / mo (Pro)'},
    'v0': {'pkr': 'Rs. 5,600', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': '$20 / mo (Premium)'},
    'bolt-new': {'pkr': 'Rs. 5,600', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': '$20 / mo (Pro)'},
    'manus-ai': {'pkr': 'Rs. 5,600', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Early Access', 'official': 'Waitlist / Access'},
    'qwen': {'pkr': 'Rs. 0', 'duration': 'Ongoing', 'access': 'Direct', 'warranty': '7 Days', 'saving': 'Free Access', 'official': 'Free Web / API'},
    'coursera-plus': {'pkr': 'Rs. 16,500', 'duration': '1 Year', 'access': 'Invitation', 'warranty': '30 Days', 'saving': 'Annual Plan', 'official': '$59 / mo ($399/yr)'},
    'udemy-personal': {'pkr': 'Rs. 5,600', 'duration': '1 Month', 'access': 'Invitation', 'warranty': '30 Days', 'saving': 'Personal Plan', 'official': '$20 - $30 / mo'},
    'opus-clip': {'pkr': 'Rs. 2,520', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': '$9 - $29 / mo'},
    'invideo-ai': {'pkr': 'Rs. 7,000', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Monthly Plan', 'official': '$25 - $60 / mo'},
    'descript': {'pkr': 'Rs. 5,320', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': '$19 - $35 / mo'},
    'make': {'pkr': 'Rs. 2,520', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': '$9 - $29 / mo'},
    'firecrawl': {'pkr': 'Rs. 4,480', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Developer Tier', 'official': '$16 - $83 / mo'},
    'notebooklm': {'pkr': 'Rs. 0', 'duration': 'Ongoing', 'access': 'Direct', 'warranty': '30 Days', 'saving': 'Free Forever', 'official': '100% Free (Google)'},
    'supabase': {'pkr': 'Rs. 7,000', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': 'Free / $25 / mo'},
    'ahrefs': {'pkr': 'Rs. 8,120', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Official Tier', 'official': 'Free / $29 / mo'},
    'railway': {'pkr': 'Rs. 1,400', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Developer Tier', 'official': '$5 / mo base + usage'},
    'davinci-resolve': {'pkr': 'Rs. 82,600', 'duration': 'Lifetime', 'access': 'Retail', 'warranty': 'Lifetime', 'saving': 'One-Time Buy', 'official': 'Free / $295 Lifetime'},
    'skillshare': {'pkr': 'Rs. 8,900', 'duration': '1 Year', 'access': 'Invitation', 'warranty': '30 Days', 'saving': 'Annual Access', 'official': '~$32 / yr (PK)'},
    'hailuo-ai': {'pkr': 'Rs. 2,800', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': 'Free / ~$10 / mo'},
    'quizlet': {'pkr': 'Rs. 2,240', 'duration': '1 Year', 'access': 'Invitation', 'warranty': '30 Days', 'saving': 'Annual Plus', 'official': 'Free / $35.99 / yr'},
    'genspark': {'pkr': 'Rs. 2,800', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': 'Free / $9.99 / mo'},
    'chatprd': {'pkr': 'Rs. 4,200', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Pro Tier', 'official': '$15 / mo (Pro)'},
    'domo-ai': {'pkr': 'Rs. 2,800', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Pro Tier', 'official': '$9.99 - $19.99 / mo'},
    'morphic': {'pkr': 'Rs. 0', 'duration': 'Ongoing', 'access': 'Direct', 'warranty': '7 Days', 'saving': 'Open Source', 'official': '100% Free / MIT'},
    'higgsfield': {'pkr': 'Rs. 2,800', 'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days', 'saving': 'Freemium', 'official': 'Free / ~$10 / mo'}
}

def update_app_js():
    app_js_path = ROOT / "app.js"
    with open(app_js_path, "r", encoding="utf-8") as f:
        js = f.read()

    # Reconstruct the directory items block cleanly
    start_idx = js.find("{id:'windsurf'")
    end_idx = js.find("];\n\nconst categoryData", start_idx)

    clean_items = []
    for slug, data in DIRECTORY_TOOLS.items():
        meta = CLEAN_DIRECTORY_METADATA[slug]
        # Clean logo path for root app.js (e.g. assets/product-logos/...)
        logo_path = data['logo']
        if logo_path.startswith('../../'):
            logo_path = logo_path[6:]
        clean_items.append(
            f"  {{id:'{slug}',name:'{data['name']}',developer:'{data['developer']}',category:'{data['category']}',"
            f"description:'{data['overview'][:100].replace(chr(39), '')}...',"
            f"pricingModel:'{meta['saving']}',officialPricing:'{meta['official']}',billingPeriod:'Monthly / Annual',"
            f"freePlan:'{data['free_plan'][:80].replace(chr(39), '')}',commercialStatus:'DIRECTORY_ONLY',"
            f"officialUrl:'{data['official_url']}',documentationUrl:'{data.get('doc_url', data['official_url'])}',"
            f"isExternal:true,bestFor:{json.dumps([t[0] for t in data['use_cases'][:3]])},"
            f"logo:'{logo_path}',features:{json.dumps([f[0] for f in data['features'][:3]])},"
            f"intent:{json.dumps([slug] + [kw.lower() for kw in data.get('primary_keywords', [])[:4]])},"
            f"pkrPrice:'{meta['pkr']}',duration:'{meta['duration']}',access:'{meta['access']}',warranty:'{meta['warranty']}'}}"
        )

    new_block = ",\n".join(clean_items)
    js = js[:start_idx] + new_block + "\n" + js[end_idx:]

    # Now ensure card(p) returns the harmonized structure
    card_template_new = """function card(p) {
  const inCart = isItemInCart(p.id);
  const isFav = state.favorites.includes(p.id);
  const isDir = p.commercialStatus === 'DIRECTORY_ONLY' || p.isExternal;

  if (isDir) {
    const devName = escapeHTML(p.developer || 'Official Vendor');
    const pricingTag = p.pricingModel || 'Official Vendor';
    const durationDisplay = escapeHTML(p.duration || '1 Month');
    const accessDisplay = escapeHTML(p.access ? (p.access.endsWith('Access') ? p.access : p.access + ' Access') : 'Private Access');
    const warrantyDisplay = escapeHTML(p.warranty ? p.warranty : '7 Days');
    const pkrPriceDisplay = escapeHTML(p.pkrPrice || 'Rs. 5,600');
    const officialRef = escapeHTML(p.officialPricing || 'Official Vendor Rate');

    return `
  <article class="product-card directory-card" data-id="${p.id}">
    <div class="product-media">
      <span class="product-badge directory-badge">Directory Reference</span>
      <button class="favorite-toggle${isFav ? ' active' : ''}" data-favorite="${p.id}" aria-label="${isFav ? 'Remove ' + p.name + ' from favorites' : 'Add ' + p.name + ' to favorites'}" aria-pressed="${isFav}" title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
        <svg><use href="#i-star"></use></svg>
      </button>
      <img class="brand-logo" src="${p.logo}" width="128" height="128" loading="lazy" alt="Official ${p.name} logo" decoding="async" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span class="category-pill">${p.category}</span>
        <span class="rating">Verified Direct</span>
      </div>
      <h3 class="product-title"><a class="product-page-link" href="tools/${p.id}/">${p.name}</a></h3>
      <p class="product-desc">${p.description}</p>
      <div class="tags">
        ${(p.bestFor || []).map(t => `<button type="button" class="tag-chip" data-tag="${safeCatalogText(t)}" title="Filter by ${safeCatalogText(t)}">${safeCatalogText(t)}</button>`).join('')}
      </div>
      <div class="product-specs">
        <span><i></i>${durationDisplay}</span>
        <span>${accessDisplay}</span>
        <span>🛡️ ${warrantyDisplay}</span>
      </div>
      <div class="product-price">
        <div class="price-block">
          <small class="ref-price">${officialRef} (Official)</small>
          <strong>${pkrPriceDisplay}</strong>
        </div>
        <span class="saving">${pricingTag}</span>
      </div>
      <div class="product-delivery-note">⚡ Direct Official Access · Directory Reference</div>
      <div class="card-actions directory-actions">
        <a class="buy-now-card explore-tool-btn" href="tools/${p.id}/">Explore Tool Profile ${svg('i-arrow')}</a>
        <a class="detail-button" href="tools/${p.id}/">View details</a>
        <a class="official-link-btn" href="${p.officialUrl}" target="_blank" rel="noopener noreferrer" title="Visit ${p.name} official website" aria-label="Visit ${p.name} official website">
          ${svg('i-external')}
        </a>
      </div>
    </div>
  </article>`;
  }"""

    old_card_match = re.search(r"function card\(p\)\s*\{[\s\S]*?if\s*\(isDir\)\s*\{[\s\S]*?\}\n\s*return `\n\s*<article class=\"product-card\" data-id=\"\$\{p\.id\}\">", js)
    if old_card_match:
        replacement = card_template_new + "\n\n  return `\n  <article class=\"product-card\" data-id=\"${p.id}\">"
        js = js[:old_card_match.start()] + replacement + js[old_card_match.end():]

    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

def update_index_html():
    index_html_path = ROOT / "index.html"
    with open(index_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Pre-render each directory card cleanly in index.html
    for slug, meta in CLEAN_DIRECTORY_METADATA.items():
        card_pattern = rf'<article class="product-card directory-card" data-id="{slug}">([\s\S]*?)</article>'
        m = re.search(card_pattern, html)
        if m:
            card_inner = m.group(1)
            # Find elements
            title_m = re.search(r'<h3 class="product-title"><a[^>]*href="tools/[^"]+">([^<]+)</a></h3>', card_inner)
            name = title_m.group(1) if title_m else slug

            cat_m = re.search(r'<span class="category-pill">([^<]+)</span>', card_inner)
            cat = cat_m.group(1) if cat_m else "AI Tools"

            desc_m = re.search(r'<p class="product-desc">([^<]+)</p>', card_inner)
            desc = desc_m.group(1) if desc_m else ""

            logo_m = re.search(r'src="([^"]+)"', card_inner)
            logo = logo_m.group(1) if logo_m else f"assets/product-logos/{slug}.svg"
            if logo.startswith('../../'):
                logo = logo[6:]

            tags_m = re.search(r'<div class="tags">([\s\S]*?)</div>', card_inner)
            tags_html = tags_m.group(1).strip() if tags_m else ""

            url_m = re.search(r'href="(https?://[^"]+)"', card_inner)
            official_url = url_m.group(1) if url_m else "https://aitoolgems.tech/"

            access_display = meta['access'] if meta['access'].endswith('Access') else f"{meta['access']} Access"

            new_card_html = f"""<article class="product-card directory-card" data-id="{slug}">
    <div class="product-media">
      <span class="product-badge directory-badge">Directory Reference</span>
      <button class="favorite-toggle" data-favorite="{slug}" aria-label="Add {name} to favorites" aria-pressed="false" title="Add to favorites">
        <svg><use href="#i-star"></use></svg>
      </button>
      <img class="brand-logo" src="{logo}" width="128" height="128" loading="lazy" alt="Official {name} logo" decoding="async" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span class="category-pill">{cat}</span>
        <span class="rating">Verified Direct</span>
      </div>
      <h3 class="product-title"><a class="product-page-link" href="tools/{slug}/">{name}</a></h3>
      <p class="product-desc">{desc}</p>
      <div class="tags">
        {tags_html}
      </div>
      <div class="product-specs">
        <span><i></i>{meta['duration']}</span>
        <span>{access_display}</span>
        <span>🛡️ {meta['warranty']}</span>
      </div>
      <div class="product-price">
        <div class="price-block">
          <small class="ref-price">{meta['official']} (Official)</small>
          <strong>{meta['pkr']}</strong>
        </div>
        <span class="saving">{meta['saving']}</span>
      </div>
      <div class="product-delivery-note">⚡ Direct Official Access · Directory Reference</div>
      <div class="card-actions directory-actions">
        <a class="buy-now-card explore-tool-btn" href="tools/{slug}/">Explore Tool Profile <svg><use href="#i-arrow"></use></svg></a>
        <a class="detail-button" href="tools/{slug}/">View details</a>
        <a class="official-link-btn" href="{official_url}" target="_blank" rel="noopener noreferrer" title="Visit {name} official website" aria-label="Visit {name} official website">
          <svg><use href="#i-external"></use></svg>
        </a>
      </div>
    </div>
  </article>"""

            html = html[:m.start()] + new_card_html + html[m.end():]

    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated index.html successfully.")

def main():
    update_app_js()
    update_index_html()

if __name__ == "__main__":
    main()
