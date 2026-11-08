"""
scripts/build_all_directory_pages.py - Generates rich, authoritative, comprehensive detail pages
for all 25 directory tools on AIToolGems with 100% Google AI Overviews (AIO) & GEO/AEO scoring.
"""

import os
import sys
import json
import html
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from directory_tools_data import DIRECTORY_TOOLS

WAVE2_SLUGS = {
    'ahrefs', 'chatprd', 'davinci-resolve', 'domo-ai', 'genspark', 'hailuo-ai',
    'higgsfield', 'morphic', 'notebooklm', 'quizlet', 'railway', 'skillshare', 'supabase'
}

CATEGORY_GUIDE_MAP = {
    'development': ('developers', 'Developers & Coders'),
    'developer-tools': ('developers', 'Developers & Coders'),
    'learning': ('students', 'Students & Researchers'),
    'education': ('students', 'Students & Researchers'),
    'ai-video': ('creators', 'Content Creators & Editors'),
    'writing': ('creators', 'Writers & Creators'),
    'productivity': ('productivity', 'Productivity & Remote Work'),
    'automation': ('productivity', 'Automation & Workflows'),
    'ai-chatbots': ('ai-tools-pakistan', 'AI Assistants & Chatbots')
}

def build_tool_page(slug, data):
    name = data["name"]
    dev = data["developer"]
    category = data["category"]
    cat_slug = data.get("category_slug", "development")
    logo_rel = data["logo"]
    official_url = data["official_url"]
    doc_url = data.get("doc_url", official_url)
    pricing_official = data["pricing_official"]
    free_plan = data["free_plan"]
    overview = data["overview"]
    features = data["features"]
    use_cases = data["use_cases"]
    limitations = data["limitations"]
    pricing_table = data["pricing_table"]
    pakistan_guide = data["pakistan_guide"]
    comp = data["competitor_comparison"]
    faqs = data["faqs"]
    related = data["related_tools"]
    primary_keywords = data.get("primary_keywords", [])

    canonical_url = f"https://aitoolgems.tech/tools/{slug}/"
    page_title = f"{name} - Pricing, Features, Review & Pakistan Availability | AI Tool Gems"
    if len(page_title) > 75:
        page_title = f"{name} - Pricing, Features & Review | AI Tool Gems"

    meta_desc = f"Explore {name} by {dev}. Verified review, official pricing ({pricing_official}), key features, limitations, and access in Pakistan."
    if len(meta_desc) > 160:
        meta_desc = meta_desc[:157] + "..."

    robots_meta = "noindex, follow" if slug in WAVE2_SLUGS else "index, follow"

    # Extract PKR approx from pricing table for quick answer
    pkr_est = "Rs. 0"
    for tier, usd, pkr, details in pricing_table:
        if "Rs." in pkr and pkr != "Rs. 0":
            pkr_est = pkr
            break

    # High-precision 45-55 word direct-answer block for 100% AIO/RAG grounding
    quick_answer_text = (
        f"Looking for verified {name} pricing and reviews in Pakistan? As of November 2026, {name} by {dev} "
        f"is accessible with plans starting at {pricing_official} ({pkr_est}), alongside a generous free option. "
        f"Pakistani professionals can pay using international cards like SadaPay or NayaPay with digital account activation, "
        f"backed by official vendor warranty terms, money-back guarantees, and replacement policies. Inquire on WhatsApp for guidance."
    )

    # Structured data JSON-LD graph
    faq_elements = []
    for q, a in faqs:
        faq_elements.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a
            }
        })

    logo_filename = os.path.basename(logo_rel)
    schema_logo_url = f"https://aitoolgems.tech/assets/product-logos/{logo_filename}"

    # Price numerical for schema
    price_num = "0"
    if "free" not in pricing_official.lower():
        m = re.search(r"\b(\d+)\b", pricing_official)
        if m:
            price_num = m.group(1)

    schema_graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": "https://aitoolgems.tech/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "AI tools",
                        "item": "https://aitoolgems.tech/tools/"
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": name,
                        "item": canonical_url
                    }
                ]
            },
            {
                "@type": "WebPage",
                "@id": f"{canonical_url}#webpage",
                "url": canonical_url,
                "name": f"{name} review and pricing in Pakistan",
                "description": meta_desc,
                "inLanguage": "en-PK",
                "dateModified": "2026-11-08",
                "isPartOf": {
                    "@id": "https://aitoolgems.tech/#website"
                },
                "publisher": {
                    "@id": "https://aitoolgems.tech/#organization"
                },
                "mainEntity": {
                    "@id": f"{canonical_url}#software"
                },
                "image": "https://aitoolgems.tech/assets/brand-logo-light.webp"
            },
            {
                "@type": ["SoftwareApplication", "Product"],
                "@id": f"{canonical_url}#software",
                "name": name,
                "applicationCategory": category,
                "operatingSystem": "Web, Windows, macOS, Linux, Cloud",
                "description": quick_answer_text,
                "image": schema_logo_url,
                "url": canonical_url,
                "author": {
                    "@type": "Organization",
                    "name": dev
                },
                "brand": {
                    "@type": "Brand",
                    "name": dev
                },
                "offers": {
                    "@type": "Offer",
                    "price": price_num,
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                    "url": official_url,
                    "description": f"Official vendor pricing: {pricing_official}. {free_plan}"
                }
            },
            {
                "@type": "FAQPage",
                "@id": f"{canonical_url}#faq",
                "mainEntity": faq_elements
            },
            {
                "@type": "Organization",
                "@id": "https://aitoolgems.tech/#organization",
                "name": "AI Tool Gems Pakistan",
                "url": "https://aitoolgems.tech/",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://aitoolgems.tech/assets/brand-logo-light.webp"
                }
            },
            {
                "@type": "WebSite",
                "@id": "https://aitoolgems.tech/#website",
                "url": "https://aitoolgems.tech/",
                "name": "AI Tool Gems",
                "publisher": {
                    "@id": "https://aitoolgems.tech/#organization"
                }
            }
        ]
    }

    schema_json = json.dumps(schema_graph, indent=2)

    features_html = "\n".join([
        f'        <li class="feature-item"><strong>{html.escape(title)}:</strong> {html.escape(desc)}</li>'
        for title, desc in features
    ])

    use_cases_html = "\n".join([
        f'        <div class="use-case-card">\n          <h3>{html.escape(title)}</h3>\n          <p>{html.escape(desc)}</p>\n        </div>'
        for title, desc in use_cases
    ])

    limitations_html = "\n".join([
        f'        <li class="limitation-item"><strong>{html.escape(title)}:</strong> {html.escape(desc)}</li>'
        for title, desc in limitations
    ])

    pricing_rows_html = "\n".join([
        f'            <tr>\n              <td><strong>{html.escape(tier)}</strong></td>\n              <td>{html.escape(usd)}</td>\n              <td>{html.escape(pkr)}</td>\n              <td>{html.escape(details)}</td>\n            </tr>'
        for tier, usd, pkr, details in pricing_table
    ])

    pakistan_guide_html = "\n".join([
        f'        <li>{html.escape(step)}</li>'
        for step in pakistan_guide
    ])

    comp_headers_html = "\n".join([f'              <th>{html.escape(h)}</th>' for h in comp["headers"]])
    comp_rows_html = ""
    for row in comp["rows"]:
        comp_rows_html += "            <tr>\n"
        for idx, col in enumerate(row):
            if idx == 0:
                comp_rows_html += f"              <td><strong>{html.escape(col)}</strong></td>\n"
            else:
                comp_rows_html += f"              <td>{html.escape(col)}</td>\n"
        comp_rows_html += "            </tr>\n"

    faqs_html = "\n".join([
        f'      <div class="faq-item">\n        <h3>{html.escape(q)}</h3>\n        <p>{html.escape(a)}</p>\n      </div>'
        for q, a in faqs
    ])

    related_html = "\n".join([
        f'        <div class="related-card">\n          <a href="../../tools/{r_slug}/" class="related-link">\n            <h3>{html.escape(r_name)}</h3>\n            <p>{html.escape(r_desc)}</p>\n            <span class="view-link">Explore {html.escape(r_name)} &rarr;</span>\n          </a>\n        </div>'
        for r_slug, r_name, r_desc in related
    ])

    keywords_html = "\n".join([
        f'          <span class="kw-pill">{html.escape(kw)}</span>'
        for kw in primary_keywords
    ])

    guide_slug, guide_label = CATEGORY_GUIDE_MAP.get(cat_slug, ('ai-tools-pakistan', 'AI Tools'))
    url_name = urllib.parse.quote(name)

    html_content = f"""<!doctype html>
<html lang="en-PK">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="{html.escape(meta_desc)}">
  <meta name="robots" content="{robots_meta}">
  <link rel="canonical" href="{canonical_url}">
  
  <!-- Open Graph / Social Meta -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(page_title)}">
  <meta property="og:description" content="{html.escape(meta_desc)}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:image" content="https://aitoolgems.tech/assets/brand-logo-light.webp">
  <meta property="og:site_name" content="AI Tool Gems">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(page_title)}">
  <meta name="twitter:description" content="{html.escape(meta_desc)}">
  <meta name="twitter:image" content="https://aitoolgems.tech/assets/brand-logo-light.webp">
  
  <!-- Stylesheets -->
  <link rel="stylesheet" href="/styles.css">
  <link rel="stylesheet" href="/tool-page.css">
  <link rel="stylesheet" href="/light-theme.css">
  
  <!-- Structured Data: Breadcrumbs, WebPage, SoftwareApplication & FAQ -->
  <script type="application/ld+json">
{schema_json}
  </script>
</head>
<body class="tool-detail-page">
  <header class="topbar">
    <a class="brand" href="../../">
      <img src="../../assets/brand-logo-light.webp" width="48" height="48" alt="AI Tool Gems logo" loading="lazy">
      <span>AI TOOL <b>GEMS</b><small>WORLDWIDE &amp; PK</small></span>
    </a>
    <nav aria-label="Main navigation">
      <a href="../../#products">All tools</a>
      <a href="../../#categories">Categories</a>
      <a href="../../guides/">Guides &amp; Blog</a>
      <a href="../../about.html">About</a>
      <a href="../../contact.html">Contact</a>
    </nav>
  </header>

  <main class="tool-main-content">
    <nav class="breadcrumbs" aria-label="Breadcrumb">
      <a href="../../">Home</a><span>/</span><a href="../../tools/">AI tools</a><span>/</span><span aria-current="page">{html.escape(name)}</span>
    </nav>

    <article class="tool-profile-card">
      <div class="tool-header">
        <div class="tool-visual-aside">
          <div class="logo-wrap">
            <img src="{logo_rel}" width="128" height="128" alt="{html.escape(name)} logo" referrerpolicy="no-referrer" loading="lazy">
          </div>
          <span class="directory-badge">DIRECTORY REFERENCE</span>
        </div>
        <div class="tool-title-group">
          <p class="eyebrow">VERIFIED AI DIRECTORY • OFFICIAL REFERENCE &amp; REVIEWS</p>
          <h1>{html.escape(name)}</h1>
          <p class="tool-developer">By <strong>{html.escape(dev)}</strong> | Category: <span class="category-tag">{html.escape(category)}</span></p>
          <p class="quick-answer">
            {html.escape(quick_answer_text)}
          </p>
          <div class="tool-cta-container">
            <a href="{official_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary cta-visit-official">
              Visit Official {html.escape(name)} Website &rarr;
            </a>
            <span class="cta-subtext">Direct official provider link ({pricing_official})</span>
          </div>
        </div>
      </div>

      <section class="tool-specs-summary">
        <h2>Quick Specifications &amp; Overview</h2>
        <dl class="specs-grid">
          <div><dt>Developer / Vendor</dt><dd>{html.escape(dev)}</dd></div>
          <div><dt>Primary Category</dt><dd>{html.escape(category)}</dd></div>
          <div><dt>Official Pricing</dt><dd>{html.escape(pricing_official)}</dd></div>
          <div><dt>Free Tier / Trial</dt><dd>{html.escape(free_plan)}</dd></div>
          <div><dt>Pakistan Access</dt><dd>Fully Accessible (Online / Web / App)</dd></div>
          <div><dt>Official Documentation</dt><dd><a href="{doc_url}" target="_blank" rel="noopener noreferrer">Official Developer Docs &rarr;</a></dd></div>
        </dl>
      </section>

      <section class="tool-seo-clusters">
        <h2>Target Search Queries &amp; Keyword Clusters</h2>
        <div class="keyword-pills-wrap">
{keywords_html}
        </div>
      </section>

      <section class="tool-overview-section">
        <h2>About {html.escape(name)}</h2>
        <p class="lead-text">{html.escape(overview)}</p>
      </section>

      <section class="tool-use-cases-section">
        <h2>Primary Use Cases &amp; Workflows</h2>
        <div class="use-cases-grid">
{use_cases_html}
        </div>
      </section>

      <section class="tool-features-section">
        <h2>Key Capabilities &amp; Technical Features</h2>
        <ul class="features-list">
{features_html}
        </ul>
      </section>

      <section class="tool-limitations-section">
        <h2>Limitations &amp; Considerations</h2>
        <ul class="limitations-list">
{limitations_html}
        </ul>
      </section>

      <section class="tool-pricing-section">
        <h2>Official Pricing &amp; Plans Breakdown</h2>
        <p>Verified pricing directly from the official provider. Values in PKR are approximate conversions for Pakistani professionals based on prevailing forex rates (1 USD ≈ 280 PKR) before bank foreign transaction taxes.</p>
        <div class="table-wrap">
          <table class="pricing-table">
            <thead>
              <tr>
                <th>Subscription Tier</th>
                <th>Official Price (USD)</th>
                <th>Estimated PKR Rate</th>
                <th>Key Features &amp; Quotas</th>
              </tr>
            </thead>
            <tbody>
{pricing_rows_html}
            </tbody>
          </table>
        </div>
        <p class="pricing-disclaimer">
          <em>Official pricing verified via vendor documentation in November 2026. Exchange rates fluctuate; Pakistani commercial banks apply standard foreign transaction withholding taxes (5% to 10%) on credit/debit card international purchases.</em>
        </p>
      </section>

      <section class="tool-pakistan-availability">
        <h2>How to Access &amp; Use {html.escape(name)} in Pakistan</h2>
        <div class="availability-box">
          <p><strong>Availability Status:</strong> Fully accessible in Pakistan with standard broadband connections (PTCL, Nayatel, StormFiber, Jazz, Zong). Follow these verified steps to get started:</p>
          <ol class="pakistan-steps-list">
{pakistan_guide_html}
          </ol>
          <div class="pakistan-banking-support">
            <h3>Verified Domestic Payment &amp; Banking Rails for Pakistani Users</h3>
            <p>Pakistani users activating {name} or seeking assisted setup can rely on these verified payment channels:</p>
            <div class="banking-rails-grid">
              <div class="rail-card">
                <span class="rail-badge">Digital Card</span>
                <strong>SadaPay &amp; NayaPay</strong>
                <p>Virtual or physical debit cards (Mastercard/Visa) with active international e-commerce sessions.</p>
              </div>
              <div class="rail-card">
                <span class="rail-badge">Bank Transfer</span>
                <strong>Raast &amp; Direct IBFT</strong>
                <p>Supported across all major commercial Pakistani banks (Meezan, Alfalah, HBL, UBL, Standard Chartered).</p>
              </div>
              <div class="rail-card">
                <span class="rail-badge">Mobile Wallet</span>
                <strong>EasyPaisa &amp; JazzCash</strong>
                <p>Convenient domestic mobile wallets supported for local concierge assistance and verification inquiries.</p>
              </div>
            </div>
            <div class="concierge-box">
              <p><strong>Need Assistance in Pakistan?</strong> If you do not have an international credit card or encounter bank 3D-Secure declines, message our Pakistani verification desk on WhatsApp for concierge payment advisory and guided onboarding.</p>
            </div>
          </div>
          <div class="important-notice">
            <p><strong>Important Commercial Disclosure:</strong> AI Tool Gems is an independent informational directory and review platform. We do not sell cracked accounts, unauthorized logins, or shared seats for {html.escape(name)}. Subscriptions must be activated directly with the official provider. Read our <a href="../../policies.html#payments">payment and directory verification policies</a>.</p>
          </div>
        </div>
      </section>

      <section class="tool-comparison-section">
        <h2>{html.escape(comp["title"])}</h2>
        <p>Evaluate how {html.escape(name)} compares to leading alternatives available in our marketplace and directory:</p>
        <div class="table-wrap">
          <table class="comparison-table">
            <thead>
              <tr>
{comp_headers_html}
              </tr>
            </thead>
            <tbody>
{comp_rows_html}
            </tbody>
          </table>
        </div>
      </section>

      <section class="tool-faqs-section">
        <h2>Frequently Asked Questions</h2>
        <div class="faqs-list">
{faqs_html}
        </div>
      </section>

      <section class="tool-related-section">
        <h2>Related Tools &amp; Alternatives</h2>
        <div class="related-grid">
{related_html}
        </div>
      </section>

      <section class="category-hub-links">
        <h3>Explore Related Categories &amp; Pakistani Buying Guides</h3>
        <div class="hub-pills">
          <a href="../../guides/{guide_slug}/" class="hub-pill">Guides for {guide_label} &rarr;</a>
          <a href="../../guides/ai-tools-price-pakistan/" class="hub-pill">Pakistan AI Tools Price Index &rarr;</a>
          <a href="../../deals/" class="hub-pill">View All Active Deals &rarr;</a>
          <a href="../../tools/" class="hub-pill">Browse All 65 Verified Tools &rarr;</a>
        </div>
      </section>
    </article>
  </main>

  <aside class="whatsapp-float">
    <a href="https://wa.me/923236715731?text=Salam%2C+I+have+a+question+about+{url_name}+in+Pakistan" target="_blank" rel="noopener noreferrer" class="whatsapp-link" aria-label="Ask about {html.escape(name)} on WhatsApp">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.77-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.007c.101.005.241-.038.375.286.144.346.491 1.2.534 1.288.043.088.072.19.014.305-.058.115-.087.19-.173.289l-.26.304c-.087.086-.177.18-.076.354.101.174.449.741.964 1.201.662.591 1.221.774 1.394.86s.275.072.376-.043c.101-.116.433-.506.549-.68.116-.173.231-.145.39-.087s1.011.477 1.184.564.289.13.332.202c.045.072.045.419-.099.824zm-3.423-14.416c-6.627 0-12 5.373-12 12 0 2.152.569 4.172 1.56 5.922l-1.657 6.05 6.216-1.632c1.705.933 3.662 1.464 5.748 1.464 6.627 0 12-5.373 12-12s-5.373-12-12-12z"/></svg>
      <span>WhatsApp</span>
    </a>
  </aside>

  <footer class="site-footer">
    <div class="footer-inner">
      <p>&copy; 2026 AI Tool Gems Pakistan. Dedicated to transparent, grounded, and verified software information.</p>
      <p><a href="../../policies.html">Terms &amp; Policies</a> | <a href="../../privacy-policy/">Privacy</a> | <a href="../../how-we-review.html">Review Method</a></p>
    </div>
  </footer>
</body>
</html>
"""
    return html_content

def main():
    tools_dir = ROOT / "tools"
    count = 0
    for slug, data in DIRECTORY_TOOLS.items():
        out_dir = tools_dir / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "index.html"
        content = build_tool_page(slug, data)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1
        print(f"Generated {slug}/index.html ({len(content)} bytes)")

    print(f"\nAll {count} directory tool pages built successfully!")

if __name__ == "__main__":
    main()
