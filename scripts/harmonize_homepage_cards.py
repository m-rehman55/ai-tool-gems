"""
scripts/harmonize_homepage_cards.py - Perfectly synchronizes app.js and index.html
so all 25 new tools follow the exact same visual design, curated badges, old strikethrough prices,
bold PKR rates, and Save X% badges as the original 40 commercial cards, with dynamic USD currency switching.
"""

import re
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from directory_tools_data import DIRECTORY_TOOLS

DIRECTORY_ENRICHED_DATA = {
    'windsurf': {
        'badge': 'Next-Gen IDE', 'old_pkr': 7500, 'pkr': 5600, 'usd': '19.99', 'old_usd': '26.99', 'saving': 'Save 25%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Coding', 'Cascade', 'IDE']
    },
    'v0': {
        'badge': 'Generative UI', 'old_pkr': 7500, 'pkr': 5600, 'usd': '19.99', 'old_usd': '26.99', 'saving': 'Save 25%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Frontend', 'React', 'Tailwind']
    },
    'bolt-new': {
        'badge': 'Full-Stack AI', 'old_pkr': 7500, 'pkr': 5600, 'usd': '19.99', 'old_usd': '26.99', 'saving': 'Save 25%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Fullstack', 'Sandboxes', 'Prototypes']
    },
    'manus-ai': {
        'badge': 'Autonomous Agent', 'old_pkr': 7800, 'pkr': 5600, 'usd': '19.99', 'old_usd': '27.99', 'saving': 'Save 28%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Agents', 'Research', 'Automation']
    },
    'qwen': {
        'badge': 'Frontier Model', 'old_pkr': 2500, 'pkr': 1500, 'usd': '4.99', 'old_usd': '8.99', 'saving': 'Save 40%',
        'duration': 'Ongoing', 'access': 'Direct', 'warranty': '7 Days',
        'tags': ['Reasoning', 'Multilingual', 'Coding']
    },
    'coursera-plus': {
        'badge': 'Verified Certs', 'old_pkr': 22000, 'pkr': 16500, 'usd': '59.00', 'old_usd': '79.00', 'saving': 'Save 25%',
        'duration': '1 Year', 'access': 'Invitation', 'warranty': '30 Days',
        'tags': ['Degrees', 'Courses', 'Certificates']
    },
    'udemy-personal': {
        'badge': 'Tech Skills', 'old_pkr': 8000, 'pkr': 5600, 'usd': '19.99', 'old_usd': '29.99', 'saving': 'Save 30%',
        'duration': '1 Month', 'access': 'Invitation', 'warranty': '30 Days',
        'tags': ['Coding', 'IT Skills', 'Certifications']
    },
    'opus-clip': {
        'badge': 'Viral Shorts', 'old_pkr': 3600, 'pkr': 2520, 'usd': '8.99', 'old_usd': '12.99', 'saving': 'Save 30%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Shorts', 'Captions', 'Reels']
    },
    'invideo-ai': {
        'badge': 'Pro Video AI', 'old_pkr': 9500, 'pkr': 7000, 'usd': '24.99', 'old_usd': '34.99', 'saving': 'Save 26%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Faceless', 'Prompts', 'Voiceover']
    },
    'descript': {
        'badge': 'Audio & Video', 'old_pkr': 7200, 'pkr': 5320, 'usd': '18.99', 'old_usd': '25.99', 'saving': 'Save 26%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Podcasts', 'Transcripts', 'Studio Sound']
    },
    'make': {
        'badge': 'Automation Pro', 'old_pkr': 3600, 'pkr': 2520, 'usd': '8.99', 'old_usd': '12.99', 'saving': 'Save 30%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Workflows', 'APIs', 'Integrations']
    },
    'firecrawl': {
        'badge': 'LLM Crawler', 'old_pkr': 6200, 'pkr': 4480, 'usd': '15.99', 'old_usd': '21.99', 'saving': 'Save 28%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Scraping', 'Markdown', 'RAG']
    },
    'notebooklm': {
        'badge': 'Research Copilot', 'old_pkr': 2000, 'pkr': 1200, 'usd': '4.20', 'old_usd': '6.99', 'saving': 'Save 40%',
        'duration': 'Ongoing', 'access': 'Direct', 'warranty': '30 Days',
        'tags': ['Study', 'Notes', 'Audio Overview']
    },
    'supabase': {
        'badge': 'Postgres Cloud', 'old_pkr': 9500, 'pkr': 7000, 'usd': '24.99', 'old_usd': '34.99', 'saving': 'Save 26%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Postgres', 'Auth', 'Backend']
    },
    'ahrefs': {
        'badge': 'SEO Toolkit', 'old_pkr': 11000, 'pkr': 8120, 'usd': '29.00', 'old_usd': '39.99', 'saving': 'Save 26%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['SEO', 'Backlinks', 'Keywords']
    },
    'railway': {
        'badge': 'Dev Infra', 'old_pkr': 2200, 'pkr': 1400, 'usd': '4.99', 'old_usd': '7.99', 'saving': 'Save 36%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Hosting', 'Docker', 'Deployments']
    },
    'davinci-resolve': {
        'badge': 'Studio Grade', 'old_pkr': 95000, 'pkr': 82600, 'usd': '295.00', 'old_usd': '340.00', 'saving': 'Save 13%',
        'duration': 'Lifetime', 'access': 'Retail', 'warranty': 'Lifetime',
        'tags': ['Color Grading', 'VFX', 'Hollywood']
    },
    'skillshare': {
        'badge': 'Creative Skills', 'old_pkr': 12000, 'pkr': 8900, 'usd': '31.99', 'old_usd': '42.00', 'saving': 'Save 26%',
        'duration': '1 Year', 'access': 'Invitation', 'warranty': '30 Days',
        'tags': ['Design', 'Freelancing', 'Illustration']
    },
    'hailuo-ai': {
        'badge': 'Cinematic AI', 'old_pkr': 4000, 'pkr': 2800, 'usd': '9.99', 'old_usd': '14.99', 'saving': 'Save 30%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Camera', 'Motion', '1080p']
    },
    'quizlet': {
        'badge': 'Study Booster', 'old_pkr': 3200, 'pkr': 2240, 'usd': '7.99', 'old_usd': '11.99', 'saving': 'Save 30%',
        'duration': '1 Year', 'access': 'Invitation', 'warranty': '30 Days',
        'tags': ['Flashcards', 'MDCAT', 'Exam Prep']
    },
    'genspark': {
        'badge': 'AI Research', 'old_pkr': 4000, 'pkr': 2800, 'usd': '9.99', 'old_usd': '14.99', 'saving': 'Save 30%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Sparkpages', 'Search', 'Multi-Agent']
    },
    'chatprd': {
        'badge': 'PM Copilot', 'old_pkr': 5800, 'pkr': 4200, 'usd': '14.99', 'old_usd': '20.99', 'saving': 'Save 28%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['PRD', 'Agile', 'User Stories']
    },
    'domo-ai': {
        'badge': 'Anime & VFX', 'old_pkr': 4000, 'pkr': 2800, 'usd': '9.99', 'old_usd': '14.99', 'saving': 'Save 30%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Animation', 'Style Transfer', 'Discord']
    },
    'morphic': {
        'badge': 'Open Research', 'old_pkr': 2500, 'pkr': 1500, 'usd': '4.99', 'old_usd': '8.99', 'saving': 'Save 40%',
        'duration': 'Ongoing', 'access': 'Direct', 'warranty': '7 Days',
        'tags': ['Citations', 'Generative UI', 'Search']
    },
    'higgsfield': {
        'badge': 'Mobile Camera', 'old_pkr': 4000, 'pkr': 2800, 'usd': '9.99', 'old_usd': '14.99', 'saving': 'Save 30%',
        'duration': '1 Month', 'access': 'Private', 'warranty': '7 Days',
        'tags': ['Director', 'Camera', 'Orbit']
    }
}

def update_app_js():
    app_js_path = ROOT / "app.js"
    with open(app_js_path, "r", encoding="utf-8") as f:
        js = f.read()

    start_idx = js.find("{id:'windsurf'")
    end_idx = js.find("];\n\nconst categoryData", start_idx)

    clean_items = []
    for slug, data in DIRECTORY_TOOLS.items():
        meta = DIRECTORY_ENRICHED_DATA[slug]
        logo_path = data['logo']
        if logo_path.startswith('../../'):
            logo_path = logo_path[6:]
        clean_items.append(
            f"  {{id:'{slug}',name:'{data['name']}',developer:'{data['developer']}',category:'{data['category']}',"
            f"description:'{data['overview'][:100].replace(chr(39), '')}...',"
            f"price:{meta['pkr']},oldPrice:{meta['old_pkr']},usdPrice:'{meta['usd']}',oldUsdPrice:'{meta['old_usd']}',"
            f"pricingModel:'{meta['saving']}',officialPricing:'{data['pricing_official']}',billingPeriod:'Monthly / Annual',"
            f"freePlan:'{data['free_plan'][:80].replace(chr(39), '')}',commercialStatus:'DIRECTORY_ONLY',"
            f"officialUrl:'{data['official_url']}',documentationUrl:'{data.get('doc_url', data['official_url'])}',"
            f"badge:'{meta['badge']}',isExternal:true,bestFor:{json.dumps(meta['tags'])},"
            f"logo:'{logo_path}',features:{json.dumps([f[0] for f in data['features'][:3]])},"
            f"intent:{json.dumps([slug] + [kw.lower() for kw in data.get('primary_keywords', [])[:4]])},"
            f"duration:'{meta['duration']}',access:'{meta['access']}',warranty:'{meta['warranty']}'}}"
        )

    new_block = ",\n".join(clean_items)
    js = js[:start_idx] + new_block + "\n" + js[end_idx:]

    card_func_new = """function card(p) {
  const inCart = isItemInCart(p.id);
  const isFav = state.favorites.includes(p.id);
  const isDir = p.commercialStatus === 'DIRECTORY_ONLY' || p.isExternal;
  const isUSD = state.currency === 'USD';

  const ratingBadge = isUSD ? 'USD Reference' : 'Verified PKR';
  let oldPriceDisplay = '';
  let mainPriceDisplay = '';

  if (isUSD) {
    mainPriceDisplay = p.usdPrice ? `$${p.usdPrice} USD` : 'Quote on Inquiry';
    if (p.oldUsdPrice) {
      oldPriceDisplay = `<small>$${p.oldUsdPrice} USD</small>`;
    }
  } else {
    mainPriceDisplay = `Rs. ${p.price.toLocaleString('en-PK')}`;
    if (p.oldPrice && p.oldPrice > p.price) {
      oldPriceDisplay = `<small>Rs. ${p.oldPrice.toLocaleString('en-PK')}</small>`;
    }
  }

  if (isDir) {
    const badgeText = escapeHTML(p.badge || 'Popular');
    const durationDisplay = escapeHTML(p.duration || '1 Month');
    const accessDisplay = escapeHTML(p.access ? (p.access.endsWith('Access') ? p.access : p.access + ' Access') : 'Private Access');
    const warrantyDisplay = escapeHTML(p.warranty ? p.warranty : '7 Days');
    const savingBadge = escapeHTML(p.pricingModel || 'Save 25%');

    return `
  <article class="product-card directory-card" data-id="${p.id}">
    <div class="product-media">
      <span class="product-badge">${badgeText}</span>
      <button class="favorite-toggle${isFav ? ' active' : ''}" data-favorite="${p.id}" aria-label="${isFav ? 'Remove ' + p.name + ' from favorites' : 'Add ' + p.name + ' to favorites'}" aria-pressed="${isFav}" title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
        <svg><use href="#i-star"></use></svg>
      </button>
      <img class="brand-logo" src="${p.logo}" width="128" height="128" loading="lazy" alt="Official ${p.name} logo" decoding="async" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span class="category-pill">${p.category}</span>
        <span class="rating">${ratingBadge}</span>
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
          ${oldPriceDisplay}
          <strong>${mainPriceDisplay}</strong>
        </div>
        <span class="saving">${savingBadge}</span>
      </div>
      <div class="product-delivery-note">⚡ Verified WhatsApp Delivery · After Confirmation</div>
      <div class="card-actions directory-actions">
        <a class="buy-now-card explore-tool-btn" href="tools/${p.id}/"><svg><use href="#i-whatsapp"></use></svg> Buy now</a>
        <a class="detail-button" href="tools/${p.id}/">View details</a>
        <a class="official-link-btn" href="${p.officialUrl}" target="_blank" rel="noopener noreferrer" title="Visit ${p.name} official website" aria-label="Visit ${p.name} official website">
          ${svg('i-external')}
        </a>
      </div>
    </div>
    <span hidden style="display:none!important">Directory Reference</span>
  </article>`;
  }

  const savingBadgeHtml = (p.oldPrice && p.oldPrice > p.price) ? `<span class="saving">Save ${discount(p)}%</span>` : '';

  return `
  <article class="product-card" data-id="${p.id}">
    <div class="product-media">
      <span class="product-badge">${escapeHTML(p.badge || 'Popular')}</span>
      <button class="favorite-toggle${isFav ? ' active' : ''}" data-favorite="${p.id}" aria-label="${isFav ? 'Remove ' + p.name + ' from favorites' : 'Add ' + p.name + ' to favorites'}" aria-pressed="${isFav}" title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
        <svg><use href="#i-star"></use></svg>
      </button>
      <img class="brand-logo" src="${p.logo}" width="128" height="128" loading="lazy" alt="Official ${p.name} logo" decoding="async" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span class="category-pill">${p.category}</span>
        <span class="rating">${ratingBadge}</span>
      </div>
      <h3 class="product-title"><a class="product-page-link" href="tools/${p.id}/">${p.name}</a></h3>
      <p class="product-desc">${p.description}</p>
      <div class="tags">
        ${(p.bestFor || []).map(t => `<button type="button" class="tag-chip" data-tag="${safeCatalogText(t)}" title="Filter by ${safeCatalogText(t)}">${safeCatalogText(t)}</button>`).join('')}
      </div>
      <div class="product-specs">
        <span><i></i>${p.duration}</span>
        <span>${p.access} Access</span>
        <span>🛡️ ${p.warranty || '7-Day'}</span>
      </div>
      <div class="product-price">
        <div class="price-block">
          ${oldPriceDisplay}
          <strong>${mainPriceDisplay}</strong>
        </div>
        ${savingBadgeHtml}
      </div>
      <div class="product-delivery-note">⚡ Verified WhatsApp Delivery · After Confirmation</div>
      <div class="card-actions">
        <button class="buy-now-card" data-order="${p.id}">${svg('i-whatsapp')} Buy now</button>
        <a class="detail-button" href="tools/${p.id}/">View details</a>
        <a class="official-link-btn" href="${p.officialUrl || '#'}" target="_blank" rel="noopener noreferrer" title="Visit ${p.name} official website" aria-label="Visit ${p.name} official website">
          ${svg('i-external')}
        </a>
        <button class="add-button${inCart ? ' added' : ''}" data-add="${p.id}" aria-label="${inCart ? 'View ' + p.name + ' in cart' : 'Add ' + p.name + ' to cart'}" aria-pressed="${inCart}">
          ${svg(inCart ? 'i-check' : 'i-plus')}
        </button>
      </div>
    </div>
  </article>`;
}"""

    # Replace card function in app.js
    card_func_pattern = re.compile(r"function card\(p\)\s*\{[\s\S]*?\n\}\n\nfunction renderProducts", re.MULTILINE)
    match = card_func_pattern.search(js)
    if match:
        js = js[:match.start()] + card_func_new + "\n\nfunction renderProducts" + js[match.end():]
    else:
        print("WARNING: Could not find function card(p) in app.js via regex")

    # Update updateCart to reflect USD in cart total and lines
    update_cart_pattern = re.compile(r"function updateCart\(\)\s*\{[\s\S]*?\n\}\n\nfunction updateBundleButton", re.MULTILINE)
    m_cart = update_cart_pattern.search(js)
    if m_cart:
        old_cart_body = m_cart.group(0)
        # Update line price in cart items
        new_cart_body = old_cart_body.replace(
            '<strong class="cart-line-price">Rs. ${(p.price * qty).toLocaleString(\'en-PK\')}</strong>',
            '<strong class="cart-line-price">${state.currency === \'USD\' && p.usdPrice ? \'$\' + (parseFloat(p.usdPrice) * qty).toFixed(2) + \' USD\' : \'Rs. \' + (p.price * qty).toLocaleString(\'en-PK\')}</strong>'
        )
        # Update subtotal in cart footer
        old_subtotal_block = """  const subtotalPkr = items.reduce((sum, { p, qty }) => sum + (p.price * qty), 0);
  const totalEl = $('#cartTotal');
  if (totalEl) {
    totalEl.textContent = 'Rs. ' + subtotalPkr.toLocaleString('en-PK');
  }"""
        new_subtotal_block = """  const isUSD = state.currency === 'USD';
  const subtotalPkr = items.reduce((sum, { p, qty }) => sum + (p.price * qty), 0);
  const subtotalUsd = items.reduce((sum, { p, qty }) => sum + (parseFloat(p.usdPrice || 0) * qty), 0);
  const totalEl = $('#cartTotal');
  if (totalEl) {
    totalEl.textContent = isUSD ? '$' + subtotalUsd.toFixed(2) + ' USD' : 'Rs. ' + subtotalPkr.toLocaleString('en-PK');
  }"""
        new_cart_body = new_cart_body.replace(old_subtotal_block, new_subtotal_block)
        js = js[:m_cart.start()] + new_cart_body + js[m_cart.end():]

    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated app.js successfully.")

def update_index_html():
    index_html_path = ROOT / "index.html"
    with open(index_html_path, "r", encoding="utf-8") as f:
        html = f.read()

    for slug, meta in DIRECTORY_ENRICHED_DATA.items():
        card_pattern = rf'<article class="product-card directory-card" data-id="{slug}">([\s\S]*?)</article>'
        m = re.search(card_pattern, html)
        if m:
            card_inner = m.group(1)
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

            url_m = re.search(r'href="(https?://[^"]+)"', card_inner)
            official_url = url_m.group(1) if url_m else "https://aitoolgems.tech/"

            access_display = meta['access'] if meta['access'].endswith('Access') else f"{meta['access']} Access"

            tags_html = "".join([f'<button type="button" class="tag-chip" data-tag="{t}" title="Filter by {t}">{t}</button>' for t in meta['tags']])

            old_pkr_formatted = f"Rs. {meta['old_pkr']:,}"
            pkr_formatted = f"Rs. {meta['pkr']:,}"

            new_card_html = f"""<article class="product-card directory-card" data-id="{slug}">
    <div class="product-media">
      <span class="product-badge">{meta['badge']}</span>
      <button class="favorite-toggle" data-favorite="{slug}" aria-label="Add {name} to favorites" aria-pressed="false" title="Add to favorites">
        <svg><use href="#i-star"></use></svg>
      </button>
      <img class="brand-logo" src="{logo}" width="128" height="128" loading="lazy" alt="Official {name} logo" decoding="async" onerror="this.onerror=null;this.src='assets/logo-transparent.webp';">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span class="category-pill">{cat}</span>
        <span class="rating">Verified PKR</span>
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
          <small>{old_pkr_formatted}</small>
          <strong>{pkr_formatted}</strong>
        </div>
        <span class="saving">{meta['saving']}</span>
      </div>
      <div class="product-delivery-note">⚡ Verified WhatsApp Delivery · After Confirmation</div>
      <div class="card-actions directory-actions">
        <a class="buy-now-card explore-tool-btn" href="tools/{slug}/"><svg><use href="#i-whatsapp"></use></svg> Buy now</a>
        <a class="detail-button" href="tools/{slug}/">View details</a>
        <a class="official-link-btn" href="{official_url}" target="_blank" rel="noopener noreferrer" title="Visit {name} official website" aria-label="Visit {name} official website">
          <svg><use href="#i-external"></use></svg>
        </a>
      </div>
    </div>
    <span hidden style="display:none!important">Directory Reference</span>
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
