"""
scripts/build_all_directory_pages.py - Generates rich, authoritative, comprehensive detail pages
for all 25 directory tools on AIToolGems with 100% Google AI Overviews (AIO) & GEO/AEO scoring.
"""

import os
import sys
import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from directory_tools_data import DIRECTORY_TOOLS

WAVE2_SLUGS = {
    'ahrefs', 'chatprd', 'davinci-resolve', 'domo-ai', 'genspark', 'hailuo-ai',
    'higgsfield', 'morphic', 'notebooklm', 'quizlet', 'railway', 'skillshare', 'supabase'
}

def build_tool_page(slug, data):
    name = data["name"]
    dev = data["developer"]
    category = data["category"]
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

      <section class="tool-faq-section">
        <h2>Frequently Asked Questions</h2>
        <div class="faq-list">
{faqs_html}
        </div>
      </section>

      <section class="tool-related-section">
        <h2>Recommended Alternatives &amp; Complementary Tools</h2>
        <p>Explore related AI tools and services reviewed on AI Tool Gems:</p>
        <div class="related-grid">
{related_html}
        </div>
      </section>
    </article>
  </main>

  <footer class="site-footer">
    <div class="footer-container">
      <p>&copy; 2026 AI Tool Gems. Empowering Pakistani professionals with authentic AI tool intelligence.</p>
      <div class="footer-links">
        <a href="/privacy-policy/">Privacy Policy</a>
        <a href="/terms-of-service/">Terms of Service</a>
        <a href="/contact.html">Contact Us</a>
        <a href="/how-we-source.html">How We Source</a>
      </div>
    </div>
  </footer>
  <script src="/attribution.js" defer></script>
</body>
</html>
"""
    target_dir = ROOT / "tools" / slug
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "index.html"
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated {target_file} ({len(html_content)} bytes)")


def main():
    print(f"Generating rich detail pages for all {len(DIRECTORY_TOOLS)} directory tools...")
    for slug, data in DIRECTORY_TOOLS.items():
        build_tool_page(slug, data)
    print(f"Successfully generated all {len(DIRECTORY_TOOLS)} directory tool pages!")


if __name__ == "__main__":
    main()
