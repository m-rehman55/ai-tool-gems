#!/usr/bin/env python3
"""
Integrates Phase 1 tools into index.html, sitemap.xml, llms.txt, and llms-full.txt.
"""

import re
import os

TOOLS = [
    {
        "id": "tradingview",
        "name": "TradingView Pro",
        "category": "Business",
        "desc": "Institutional-grade technical charting, custom Pine Script indicators, and real-time alerts.",
        "pkr": 3500,
        "old_pkr": 5000,
        "usd": "14.99",
        "duration": "1 Month",
        "access": "Private Plan",
        "badge": "Pro Trader",
        "tags": ["Charts", "Crypto", "Stocks"],
        "saving": "30%",
        "rating": "4.9",
        "warranty": "30 Days"
    },
    {
        "id": "kling",
        "name": "Kling AI",
        "category": "AI Video",
        "desc": "Hollywood-grade physics simulation, cinematic camera motion, and hyper-realistic AI video generation.",
        "pkr": 4800,
        "old_pkr": 6500,
        "usd": "19.99",
        "duration": "1 Month",
        "access": "Private Plan",
        "badge": "Ultra Realistic",
        "tags": ["Cinematic", "Motion", "VFX"],
        "saving": "26%",
        "rating": "4.9",
        "warranty": "30 Days"
    },
    {
        "id": "freepik",
        "name": "Freepik Premium",
        "category": "Design",
        "desc": "Millions of premium vector illustrations, high-res stock photos, PSD mockups, and AI Pikaso.",
        "pkr": 2400,
        "old_pkr": 3500,
        "usd": "9.99",
        "duration": "1 Month",
        "access": "Private Plan",
        "badge": "Graphic Essential",
        "tags": ["Vectors", "PSD", "Mockups"],
        "saving": "31%",
        "rating": "4.8",
        "warranty": "30 Days"
    },
    {
        "id": "spotify",
        "name": "Spotify Premium",
        "category": "Entertainment",
        "desc": "Ad-free music and podcasts, offline downloads, unlimited skips, and 320kbps extreme audio quality.",
        "pkr": 1200,
        "old_pkr": 1800,
        "usd": "5.99",
        "duration": "3 Months",
        "access": "Private Plan",
        "badge": "Ad-Free Audio",
        "tags": ["Music", "Podcasts", "Offline"],
        "saving": "33%",
        "rating": "4.9",
        "warranty": "30 Days"
    },
    {
        "id": "copilot",
        "name": "GitHub Copilot",
        "category": "Development",
        "desc": "AI pair programmer for VS Code and JetBrains with real-time autocompletion and Copilot Chat.",
        "pkr": 2500,
        "old_pkr": 3800,
        "usd": "9.99",
        "duration": "1 Month",
        "access": "Private Plan",
        "badge": "Developer Pick",
        "tags": ["VS Code", "Autocomplete", "Fullstack"],
        "saving": "34%",
        "rating": "4.9",
        "warranty": "30 Days"
    },
    {
        "id": "suno",
        "name": "Suno AI",
        "category": "AI Voice",
        "desc": "Generate studio-grade full vocal songs, catchy commercial jingles, and instrumental beats from text.",
        "pkr": 3200,
        "old_pkr": 4500,
        "usd": "12.99",
        "duration": "1 Month",
        "access": "Private Plan",
        "badge": "AI Music Hits",
        "tags": ["Songwriting", "Vocals", "Beats"],
        "saving": "28%",
        "rating": "4.8",
        "warranty": "30 Days"
    },
    {
        "id": "turnitin",
        "name": "Turnitin Student Account",
        "category": "Writing & SEO",
        "desc": "Non-repository academic similarity check and AI writing detection report for thesis and research.",
        "pkr": 3600,
        "old_pkr": 5000,
        "usd": "14.99",
        "duration": "1 Month",
        "access": "Private Plan",
        "badge": "Academic Pick",
        "tags": ["Thesis", "Assignments", "AI Detection"],
        "saving": "28%",
        "rating": "4.9",
        "warranty": "30 Days"
    },
    {
        "id": "office365",
        "name": "Microsoft Office 365 (1TB)",
        "category": "Productivity",
        "desc": "Word, Excel, PowerPoint, Outlook desktop apps on 5 devices simultaneously with 1TB OneDrive cloud.",
        "pkr": 2200,
        "old_pkr": 3800,
        "usd": "8.99",
        "duration": "1 Year",
        "access": "Private Plan",
        "badge": "1TB Cloud",
        "tags": ["Word/Excel", "OneDrive", "5 Devices"],
        "saving": "42%",
        "rating": "4.9",
        "warranty": "30 Days"
    }
]

def update_index_html():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update category counts in categoryGrid
    category_counts = {
        'AI Video': '5 tools',
        'Design': '6 tools',
        'Development': '5 tools',
        'Writing &amp; SEO': '4 tools',
        'Writing & SEO': '4 tools',
        'Productivity': '3 tools',
        'AI Voice': '2 tools',
        'Entertainment': '3 tools',
        'Business': '2 tools'
    }
    
    for cat, new_count in category_counts.items():
        # Match pattern: data-category="<cat>" ... <span class="category-count"><old></span>
        escaped_cat = re.escape(cat)
        pattern = rf'(data-category="{escaped_cat}".*?<span class="category-count">)[^<]+(</span>)'
        html = re.sub(pattern, rf'\g<1>{new_count}\g<2>', html, flags=re.DOTALL)

    # 2. Add product cards into productGrid
    # Generate cards HTML
    cards_html = []
    for t in TOOLS:
        tags_html = "".join([f'<button type="button" class="tag-chip" data-tag="{tag}">{tag}</button>' for tag in t["tags"]])
        card = f'''  <article class="product-card" data-id="{t['id']}">
    <div class="product-media">
      <span class="product-badge">{t['badge']}</span>
      <button class="favorite-toggle" data-favorite="{t['id']}" aria-label="Add {t['name']} to favorites" aria-pressed="false" title="Add to favorites">
        <svg><use href="#i-star"></use></svg>
      </button>
      <img class="brand-logo" src="assets/product-logos/{t['id']}.png" width="128" height="128" loading="lazy" alt="Official {t['name']} logo" decoding="async" referrerpolicy="no-referrer">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span>{t['category']}</span>
        <span class="rating">PKR pricing</span>
      </div>
      <h3><a class="product-page-link" href="tools/{t['id']}/">{t['name']}</a></h3>
      <p class="product-desc">{t['desc']}</p>
      <div class="tags">
        {tags_html}
      </div>
      <div class="product-specs">
        <span><i></i>{t['duration']}</span>
        <span>{t['access']}</span>
      </div>
      <div class="product-price">
        <div class="price-block">
          <small>Rs. {t['old_pkr']:,}</small>
          <strong>Rs. {t['pkr']:,}</strong>
        </div>
        <span class="saving">Save {t['saving']}</span>
      </div>
      <div class="card-actions">
        <button class="buy-now-card" data-order="{t['id']}"><svg><use href="#i-whatsapp"></use></svg> Buy now</button>
        <a class="detail-button" href="tools/{t['id']}/" style="display:grid;place-items:center;text-decoration:none;">View details</a>
        <button class="add-button " data-add="{t['id']}" aria-label="Add {t['name']} to cart" aria-pressed="false">
          <svg><use href="#i-plus"></use></svg>
        </button>
      </div>
    </div>
  </article>'''
        cards_html.append(card)

    cards_block = "\n" + "\n".join(cards_html)
    
    # Insert after allinone article
    target_allinone = 'data-id="allinone">'
    idx = html.find(target_allinone)
    if idx != -1:
        end_art_idx = html.find('</article>', idx)
        if end_art_idx != -1:
            insert_pos = end_art_idx + len('</article>')
            # Check if not already inserted
            if 'data-id="tradingview"' not in html:
                html = html[:insert_pos] + cards_block + html[insert_pos:]
                print("Inserted 8 product cards into productGrid")

    # 3. Add to catalog-directory
    dir_links = "".join(['<a href="tools/' + t['id'] + '/">' + t['name'] + '</a>' for t in TOOLS])
    cat_dir_target = '<a href="tools/allinone/">All-in-One Mega AI Portal</a>'
    if cat_dir_target in html and 'href="tools/tradingview/"' not in html[html.find('class="catalog-directory"'):html.find('</nav>', html.find('class="catalog-directory"'))]:
        html = html.replace(cat_dir_target, cat_dir_target + dir_links)
        print("Inserted 8 links into catalog-directory")

    # 4. Add to ItemList in schema
    schema_items = []
    start_pos = 21  # 20 exist in ItemList
    for i, t in enumerate(TOOLS):
        item_snippet = f''',
        {{
          "@type": "ListItem",
          "position": {start_pos + i},
          "item": {{
            "@id": "https://aitoolgems.tech/tools/{t['id']}/",
            "name": "{t['name']}"
          }}
        }}'''
        schema_items.append(item_snippet)
    
    items_block = "".join(schema_items)
    target_item20 = '"name": "Windows 11 Pro Key"\n          }\n        }'
    if target_item20 in html and 'https://aitoolgems.tech/tools/tradingview/' not in html[:html.find('class="product-grid"')]:
        html = html.replace(target_item20, target_item20 + items_block)
        print("Inserted 8 items into ItemList schema in index.html")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html updated successfully!")

def update_sitemap():
    with open("sitemap.xml", "r", encoding="utf-8") as f:
        xml = f.read()

    new_urls = []
    for t in TOOLS:
        url_snippet = f'''  <url>
    <loc>https://aitoolgems.tech/tools/{t['id']}/</loc>
    <lastmod>2026-10-24</lastmod>
  </url>'''
        if f"https://aitoolgems.tech/tools/{t['id']}/" not in xml:
            new_urls.append(url_snippet)

    if new_urls:
        insert_block = "\n".join(new_urls) + "\n</urlset>"
        xml = xml.replace("</urlset>", insert_block)
        with open("sitemap.xml", "w", encoding="utf-8") as f:
            f.write(xml)
        print(f"Added {len(new_urls)} URLs to sitemap.xml")
    else:
        print("All URLs already exist in sitemap.xml")

def update_llms():
    with open("llms.txt", "r", encoding="utf-8") as f:
        text = f.read()

    new_listings = [
        "- [TradingView Pro](https://aitoolgems.tech/tools/tradingview/) — Rs. 3,500 PKR ($14.99 USD) (1 Month, real-time charts, indicators & Pine Script, instant delivery)",
        "- [Kling AI](https://aitoolgems.tech/tools/kling/) — Rs. 4,800 PKR ($19.99 USD) (1 Month, 1080p cinematic AI video generator, instant delivery)",
        "- [Freepik Premium](https://aitoolgems.tech/tools/freepik/) — Rs. 2,400 PKR ($9.99 USD) (1 Month, unlimited vectors, PSDs, stock photos & Pikaso AI, instant delivery)",
        "- [Spotify Premium](https://aitoolgems.tech/tools/spotify/) — Rs. 1,200 PKR ($5.99 USD) (3 Months, ad-free music, offline songs & 320kbps audio, instant delivery)",
        "- [GitHub Copilot](https://aitoolgems.tech/tools/copilot/) — Rs. 2,500 PKR ($9.99 USD) (1 Month, AI code completions in VS Code & JetBrains, instant delivery)",
        "- [Suno AI](https://aitoolgems.tech/tools/suno/) — Rs. 3,200 PKR ($12.99 USD) (1 Month Pro, 2,500 credits, full vocal AI music generator, instant delivery)",
        "- [Turnitin Student Account](https://aitoolgems.tech/tools/turnitin/) — Rs. 3,600 PKR ($14.99 USD) (1 Month, non-repository similarity & AI detection report, instant delivery)",
        "- [Microsoft Office 365 (1TB)](https://aitoolgems.tech/tools/office365/) — Rs. 2,200 PKR ($8.99 USD) (1 Year, 5 devices simultaneously + 1TB OneDrive cloud, instant delivery)"
    ]

    target = "- [Windows 11 Pro Key](https://aitoolgems.tech/tools/windows/) — Rs. 1,900 PKR (Lifetime retail product key, instant digital activation)"
    if target in text and "TradingView Pro" not in text:
        text = text.replace("## Product Catalog (20 Verified Listings)", "## Product Catalog (28 Verified Listings)")
        text = text.replace(target, target + "\n" + "\n".join(new_listings))
        with open("llms.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Updated llms.txt")

def update_llms_full():
    with open("llms-full.txt", "r", encoding="utf-8") as f:
        text = f.read()

    entries = """
### 21. TradingView Pro (TradingView)
- URL: https://aitoolgems.tech/tools/tradingview/
- Listed Price: Rs. 3,500 PKR ($14.99 USD) / month (Regular: Rs. 5,000)
- Duration: 1 Month
- Access Type: Private Account (Dedicated credentials, full control)
- Delivery Time: Delivery after payment confirmation on WhatsApp
- Warranty: 30-Day Replacement Warranty
- Key Features: 5 indicators per chart, Bar Replay backtesting, Volume Profile analysis, unlimited custom watchlists, 20 server-side price alerts.

### 22. Kling AI (Kuaishou)
- URL: https://aitoolgems.tech/tools/kling/
- Listed Price: Rs. 4,800 PKR ($19.99 USD) / month (Regular: Rs. 6,500)
- Duration: 1 Month
- Access Type: Private Account
- Delivery Time: Delivery after payment confirmation on WhatsApp
- Warranty: 30-Day Replacement Warranty
- Key Features: 1080p full HD video generation, 3D camera controls, physics-accurate motion simulation, zero watermark, full commercial rights.

### 23. Freepik Premium (Freepik Company)
- URL: https://aitoolgems.tech/tools/freepik/
- Listed Price: Rs. 2,400 PKR ($9.99 USD) / month (Regular: Rs. 3,500)
- Duration: 1 Month
- Access Type: Private Account
- Delivery Time: Delivery after payment confirmation on WhatsApp
- Warranty: 30-Day Replacement Warranty
- Key Features: 100 daily premium downloads, 150M+ vectors, PSD mockups, stock photos, Pikaso AI generator, commercial license without attribution.

### 24. Spotify Premium (Spotify AB)
- URL: https://aitoolgems.tech/tools/spotify/
- Listed Price: Rs. 1,200 PKR ($5.99 USD) for 3 Months (Regular: Rs. 1,800)
- Duration: 3 Months
- Access Type: Private Account (Activated on your personal email)
- Delivery Time: Delivery after payment confirmation on WhatsApp
- Warranty: 30-Day Replacement Warranty
- Key Features: 100% ad-free music and podcasts, 10,000 songs offline downloads, ultra-high 320kbps audio bitrate, unlimited skips.

### 25. GitHub Copilot (GitHub / Microsoft)
- URL: https://aitoolgems.tech/tools/copilot/
- Listed Price: Rs. 2,500 PKR ($9.99 USD) / month (Regular: Rs. 3,800)
- Duration: 1 Month
- Access Type: Private Account (Direct activation on personal GitHub username)
- Delivery Time: Delivery after payment confirmation on WhatsApp
- Warranty: 30-Day Replacement Warranty
- Key Features: Real-time code completions, Copilot Chat inside VS Code and JetBrains, unit test generation, multi-language context understanding.

### 26. Suno AI (Suno, Inc.)
- URL: https://aitoolgems.tech/tools/suno/
- Listed Price: Rs. 3,200 PKR ($12.99 USD) / month (Regular: Rs. 4,500)
- Duration: 1 Month Pro
- Access Type: Private Account
- Delivery Time: Delivery after payment confirmation on WhatsApp
- Warranty: 30-Day Replacement Warranty
- Key Features: 2,500 monthly generation credits (~500 songs), full studio vocals, custom lyrics mode, commercial monetization rights.

### 27. Turnitin Student Account (Turnitin LLC)
- URL: https://aitoolgems.tech/tools/turnitin/
- Listed Price: Rs. 3,600 PKR ($14.99 USD) / month (Regular: Rs. 5,000)
- Duration: 1 Month
- Access Type: Private Account
- Delivery Time: Delivery after payment confirmation on WhatsApp
- Warranty: 30-Day Replacement Warranty
- Key Features: Strict Non-Repository submission guarantee (zero self-plagiarism match), similarity index percentage report, AI writing detection percentage.

### 28. Microsoft Office 365 (Microsoft Corporation)
- URL: https://aitoolgems.tech/tools/office365/
- Listed Price: Rs. 2,200 PKR ($8.99 USD) / year (Regular: Rs. 3,800)
- Duration: 1 Year (12 Months)
- Access Type: Private Account
- Delivery Time: Delivery after payment confirmation on WhatsApp
- Warranty: 30-Day Replacement Warranty
- Key Features: Full Word, Excel, PowerPoint & Outlook desktop apps, 1TB (1,000 GB) secure OneDrive cloud storage, 5 devices simultaneously.
"""
    if "TradingView Pro" not in text:
        text = text.strip() + "\n" + entries
        with open("llms-full.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Updated llms-full.txt")

if __name__ == "__main__":
    update_index_html()
    update_sitemap()
    update_llms()
    update_llms_full()
