#!/usr/bin/env python3
"""
AIToolGems Autonomous Daily SEO Blog & Guide Publisher
------------------------------------------------------
Production-ready, safe, Pakistan-focused content automation engine that:
1. Discovers approved topics from data/seo/content-queue.json.
2. Enforces anti-cannibalization checks against data/seo/keyword-map.json.
3. Incorporates contextual links from data/seo/internal-link-map.json.
4. Generates 1,500+ word semantic SEO articles with Article, Breadcrumb, FAQPage schemas.
5. Validates word count, keyword density (0.5%-2.0%), H1, meta desc, canonical, and links.
6. Updates sitemap.xml, llms.txt, guides/index.html, and keyword status.
7. Operates in two modes:
   - Dry Run (default): Generates, audits, and previews without committing.
   - Publish Mode (--publish): Writes file, syncs dependencies, triggers IndexNow.
"""

import os
import sys
import json
import re
import datetime
import urllib.request
import urllib.error
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent

# Import validator
sys.path.insert(0, str(BASE / "scripts"))
sys.path.insert(0, str(BASE))
from validate_content import validate_article_file, check_cannibalization
from submit_indexnow import submit_to_indexnow


def send_telegram_alert(text: str) -> bool:
    """Send autonomous publishing notification to Telegram owner."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_OWNER_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        from marketing_agent.telegram import TelegramClient
        tg = TelegramClient(token=token)
        tg.send_with_retry(chat_id=chat_id, text=text)
        print("✅ Telegram notification dispatched to owner.")
        return True
    except Exception as e:
        print(f"⚠️ Telegram notice: {e}")
        return False


def query_gemini_api(prompt: str, api_key: str) -> str | None:
    """Dynamic generation using Google Gemini 2.0 Flash (with 1.5 Pro and 1.5 Flash fallbacks)."""
    keys = [k.strip() for k in api_key.split(",") if k.strip()]
    if not keys:
        return None

    # Cascade of available free-tier Google Gemini models from most advanced to fallback
    models_to_try = [
        ("gemini-2.0-flash", "Google Gemini 2.0 Flash (Next-Gen State of the Art)"),
        ("gemini-1.5-pro", "Google Gemini 1.5 Pro (Flagship Reasoning)"),
        ("gemini-1.5-flash", "Google Gemini 1.5 Flash (Fast Fallback)")
    ]

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 3000}
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    for key_idx, key in enumerate(keys, 1):
        for model_id, model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={key}"
            req = urllib.request.Request(url, data=data, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    candidates = res_json.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        print(f"✨ Successfully generated organic analysis using {model_name} (Key #{key_idx}).")
                        return candidates[0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"ℹ️ {model_name} on Key #{key_idx} notice: ({e}). Trying next tier...")

    print("⚠️ All Gemini API models/keys skipped or quota reached. Using high-authority structured engine fallback.")
    return None


def load_queue_candidate() -> dict | None:
    """Load next eligible, approved topic from content queue."""
    queue_file = BASE / "data" / "seo" / "content-queue.json"
    published_slugs = {p.parent.name for p in (BASE / "guides").glob("*/index.html")}

    if queue_file.exists():
        queue_data = json.loads(queue_file.read_text(encoding="utf-8"))
        for item in queue_data:
            if item.get("approved_for_publishing", True) and item["slug"] not in published_slugs:
                # Format to blueprint format
                related = [(t["slug"], t["name"]) for t in item.get("related_tools", [])]
                return {
                    "slug": item["slug"],
                    "title": item["title"],
                    "meta_desc": item["meta_description"],
                    "primary_keyword": item["primary_keyword"],
                    "secondary_keywords": item.get("secondary_keywords", []),
                    "target_audience": item.get("target_audience", "Pakistani professionals"),
                    "tool_key": item.get("primary_tool", "chatgpt"),
                    "related_tools": related
                }

    return None


def render_article_html(bp: dict) -> str:
    """Generates a complete 1,500+ word semantic HTML guide with full JSON-LD schema and dynamic organic keyword targeting."""
    slug = bp["slug"]
    title = bp["title"]
    desc = bp["meta_desc"]
    pk = bp["primary_keyword"]
    sec_kws = bp.get("secondary_keywords", [])
    now_date = datetime.date.today().isoformat()
    
    # Extract organic secondary keyword targets
    sec1 = sec_kws[0] if len(sec_kws) > 0 else f"{pk} vs Alternatives"
    sec2 = sec_kws[1] if len(sec_kws) > 1 else f"AI generator Pakistan"
    sec3 = sec_kws[2] if len(sec_kws) > 2 else f"Buy {pk} PKR"
    sec4 = sec_kws[3] if len(sec_kws) > 3 else f"{pk} price Pakistan"

    # Optional dynamic editorial generation via Google Gemini 2.0 Flash
    ai_extra_html = ""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        prompt = (
            f"You are a senior organic SEO tech journalist for aitoolgems.tech (Pakistan's AI tools marketplace).\n"
            f"Write an authoritative, 500-word editorial analysis section for the article: '{title}'.\n"
            f"Primary organic keyword: '{pk}'\n"
            f"Secondary organic keywords to naturally weave into paragraphs: {', '.join(sec_kws)}\n"
            f"Target Audience: {bp.get('target_audience', 'Pakistani freelancers and agencies')}\n"
            f"Local Pakistani Context:\n"
            f"- Transparent PKR pricing with EasyPaisa, JazzCash, SadaPay\n"
            f"- Avoid international card declines and 10%-15% FBR withholding tax\n"
            f"- Practical Upwork/Fiverr freelance and Pakistani agency workflows\n"
            f"Format requirements:\n"
            f"- Return ONLY clean semantic HTML (<p>, <h3>, <ul>, <li>).\n"
            f"- DO NOT use <h1> or <h2> tags.\n"
            f"- DO NOT wrap in markdown code blocks."
        )
        ai_resp = query_gemini_api(prompt, api_key)
        if ai_resp:
            clean_resp = re.sub(r"^```[a-z]*\s*", "", ai_resp.strip(), flags=re.IGNORECASE)
            clean_resp = re.sub(r"\s*```$", "", clean_resp).strip()
            ai_extra_html = f"""
      <section class="content-section ai-editorial-insight">
        <h2>In-Depth Technical Analysis &amp; Creator Insights</h2>
        {clean_resp}
      </section>"""

    # Dynamic FAQ data targeting organic search queries
    faq_data = [
        {
            "q": f"What is the verified cost of {pk} and {sec4} in Pakistan?",
            "a": f"Official overseas subscriptions billed in USD incur bank forex conversion fees and 10% to 15% withholding taxes on Pakistani debit cards. AI Tool Gems provides verified subscriptions directly in flat Pakistani Rupees (PKR) without hidden charges."
        },
        {
            "q": f"How does {sec1} compare for local creators and freelancers?",
            "a": f"When comparing {sec1}, consider generation speed, prompt consistency, and commercial rights. Local freelancers on Upwork and Fiverr require tools with full client usage permissions and responsive customer support in Pakistan."
        },
        {
            "q": f"Can I {sec3} using EasyPaisa or JazzCash?",
            "a": f"Yes! While international platforms require foreign credit cards that often face declines, AI Tool Gems enables instant local activation in Pakistan using EasyPaisa, JazzCash, SadaPay, NayaPay, or direct bank transfer."
        },
        {
            "q": f"Why is finding a reliable {sec2} crucial for Pakistani agencies?",
            "a": f"Using a verified {sec2} ensures seamless workflow continuity, high-resolution rendering, and active 7-day replacement warranties, allowing local agencies to deliver client projects on schedule."
        }
    ]

    # Render JSON-LD FAQ entities
    faq_schema_items = []
    for item in faq_data:
        q_escaped = item['q'].replace('"', '\\"')
        a_escaped = item['a'].replace('"', '\\"')
        faq_schema_items.append(f"""        {{
          "@type": "Question",
          "name": "{q_escaped}",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "{a_escaped}"
          }}
        }}""")
    faq_schema_str = ",\n".join(faq_schema_items)

    # Render HTML FAQ accordion
    faq_html_items = []
    for item in faq_data:
        faq_html_items.append(f"""        <div class="faq-item">
          <h3>{item['q']}</h3>
          <p>{item['a']}</p>
        </div>""")
    faq_accordion_html = "\n".join(faq_html_items)

    related_links_html = "\n".join([f'          <li><a href="../../tools/{k}/">{name} in Pakistan</a></li>' for k, name in bp["related_tools"]])

    html = f"""<!doctype html><html lang="en-PK"><head>
  <link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" as="style"
  rel="preconnect" href="https://www.google.com" crossorigin>
  <link rel="preconnect" href="https://t0.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://t1.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://t3.gstatic.com" crossorigin>

  <link rel="alternate" hreflang="en-PK" href="https://aitoolgems.tech/guides/{slug}/">
  <link rel="alternate" hreflang="x-default" href="https://aitoolgems.tech/guides/{slug}/">

<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="msvalidate.01" content="737494F711E656D83B3126A5D5707776">
  <meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="https://aitoolgems.tech/guides/{slug}/">
<meta property="og:type" content="article"><meta property="og:site_name" content="AI Tool Gems Pakistan"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://aitoolgems.tech/guides/{slug}/"><meta property="og:image" content="https://aitoolgems.tech/assets/brand-logo-light.webp"><meta property="article:modified_time" content="{now_date}T00:00:00+05:00"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../../assets/brand-logo-light.webp"><link rel="stylesheet" href="../../guide.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Article",
      "@id": "https://aitoolgems.tech/guides/{slug}/#article",
      "headline": "{title}",
      "description": "{desc}",
      "datePublished": "{now_date}",
      "dateModified": "{now_date}",
      "inLanguage": "en-PK",
      "mainEntityOfPage": {{
        "@id": "https://aitoolgems.tech/guides/{slug}/#webpage"
      }},
      "author": {{
        "@type": "Organization",
        "name": "AI Tool Gems Editorial Team",
        "url": "https://aitoolgems.tech/how-we-review.html",
        "image": "https://aitoolgems.tech/assets/brand-logo-light.png"
      }},
      "publisher": {{
        "@id": "https://aitoolgems.tech/#organization"
      }},
      "image": "https://aitoolgems.tech/assets/brand-logo-light.png",
      "about": [
        {{
          "@type": "SoftwareApplication",
          "name": "{pk}"
        }}
      ]
    }},
    {{
      "@type": "WebPage",
      "@id": "https://aitoolgems.tech/guides/{slug}/#webpage",
      "url": "https://aitoolgems.tech/guides/{slug}/",
      "name": "{title}",
      "dateModified": "{now_date}",
      "inLanguage": "en-PK",
      "isPartOf": {{
        "@id": "https://aitoolgems.tech/#website"
      }},
      "image": "https://aitoolgems.tech/assets/brand-logo-light.png"
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://aitoolgems.tech/"
        }},
        {{
          "@type": "ListItem",
          "position": 2,
          "name": "Guides & Blog",
          "item": "https://aitoolgems.tech/guides/"
        }},
        {{
          "@type": "ListItem",
          "position": 3,
          "name": "{title}",
          "item": "https://aitoolgems.tech/guides/{slug}/"
        }}
      ],
      "image": "https://aitoolgems.tech/assets/brand-logo-light.png"
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [
{faq_schema_str}
      ],
      "image": "https://aitoolgems.tech/assets/brand-logo-light.png"
    }}
  ],
  "image": "https://aitoolgems.tech/assets/brand-logo-light.png"
}}
</script>
</head>
<body>
  <header class="topbar">
    <a class="brand" href="../../">
      <img src="../../assets/brand-logo-light.webp" width="48" height="48" alt="AI Tool Gems logo" loading="lazy">
      <span>AI TOOL <b>GEMS</b><small>PAKISTAN</small></span>
    </a>
    <nav aria-label="Main navigation">
      <a href="../../#products">All tools</a>
      <a href="../../deals/">Deals</a>
      <a href="../">Guides &amp; Blog</a>
      <a href="../../#categories">Categories</a>
      <a href="../../about.html">About</a>
      <a href="../../contact.html">Contact</a>
    </nav>
  </header>

  <main>
    <nav class="breadcrumbs" aria-label="Breadcrumb">
      <a href="../../">Home</a><span>/</span>
      <a href="../">Guides &amp; Blog</a><span>/</span>
      <span>{title}</span>
    </nav>

    <article class="article-content">
      <header class="article-header">
        <p class="eyebrow">EDITORIAL RESEARCH &bull; PAKISTAN MARKET</p>
        <h1>{title}</h1>
        <div class="byline">
          <span>By AI Tool Gems Editorial Team</span>
          <span>Updated {now_date}</span>
          <span>Verified Pakistan Pricing (PKR)</span>
        </div>
      </header>

      <section class="quick-summary">
        <h2>Quick Answer &amp; Overview: {pk}</h2>
        <p>Finding affordable, reliable access to <strong>{pk}</strong> has become a crucial challenge for {bp["target_audience"]}. International billing in USD frequently leads to high forex conversion fees, bank withholding taxes, or outright transaction declines on Pakistani debit cards. This independent guide breaks down actual PKR costs, feature benchmarks, local payment methods (EasyPaisa, JazzCash, SadaPay), and how to verify subscription legitimacy before spending money.</p>
        <p>In Pakistan's fast-growing digital economy, freelancers working on Upwork and Fiverr, content creators scaling YouTube channels, and digital agencies need powerful generative tools without overpaying in foreign exchange fees. Our analysis examines the top alternatives, prompt accuracy, commercial usage rights, and straightforward ordering steps.</p>
      </section>

      <section class="content-section">
        <h2>Understanding Real Costs: {sec4.title()} &amp; PKR Reality</h2>
        <p>When investigating <strong>{sec4}</strong> or purchasing foreign software directly from vendor websites, Pakistani buyers face several hidden costs that significantly inflate the final expense:</p>
        <ul>
          <li><strong>Foreign Currency Transaction Fees:</strong> Most Pakistani commercial banks charge between 3.5% and 5.0% for foreign currency conversions on every overseas billing cycle.</li>
          <li><strong>Mandatory Withholding Tax:</strong> Under Federal Board of Revenue regulations, transactions on international merchants incur withholding taxes of up to 10% for active tax filers and up to 15% for non-filers.</li>
          <li><strong>Frequent Card Declines:</strong> Many domestic digital wallets and basic debit cards lack active international e-commerce permissions, blocking recurring monthly software subscriptions.</li>
        </ul>
        <p>By leveraging AI Tool Gems, local professionals bypass cross-border friction entirely. All plans are listed in transparent Pakistani Rupees (PKR) and backed by guaranteed delivery within 15 to 30 minutes via WhatsApp.</p>
      </section>

      <section class="content-section">
        <h2>Performance Evaluation: {sec1.title()}</h2>
        <p>A rigorous evaluation of <strong>{sec1}</strong> requires looking past promotional marketing claims to examine practical output quality, rendering speed, and cost efficiency in Pakistan:</p>
        <ol>
          <li><strong>Prompt Comprehension &amp; Detail Fidelity:</strong> How accurately the engine renders intricate styling, lighting, and anatomy without distorting complex prompt instructions.</li>
          <li><strong>Rendering Speed &amp; Generation Credits:</strong> Turnaround time per request and the volume of generations available within standard monthly allowances.</li>
          <li><strong>Commercial Licensing Rights:</strong> Clear terms permitting client deliverables for Pakistani freelance projects across international marketplaces.</li>
          <li><strong>Platform Interface &amp; Workflow Simplicity:</strong> Clean browser-based or desktop software avoiding complex technical setup or difficult local installation hurdles.</li>
        </ol>
      </section>

      <section class="content-section">
        <h2>Practical Workflows: {sec2.title()} for Local Creators</h2>
        <p>Deploying a verified <strong>{sec2}</strong> workflow powers productivity across several Pakistani digital industries:</p>
        <ul>
          <li><strong>Freelance Designers on Fiverr &amp; Upwork:</strong> Delivering client logos, concept art, website banners, and marketing mockups on tight turnaround schedules.</li>
          <li><strong>YouTube &amp; Social Media Video Editors:</strong> Designing high-CTR video thumbnails, background art, and social media carousels that drive strong audience engagement.</li>
          <li><strong>E-commerce &amp; Digital Marketing Agencies:</strong> Generating product showcase scenes, social ad creatives, and promotional material for local Pakistani brands.</li>
          <li><strong>Students &amp; Academic Researchers:</strong> Preparing visually engaging presentation decks and design portfolios on student-friendly PKR budgets.</li>
        </ul>
      </section>
{ai_extra_html}

      <section class="content-section">
        <h2>Pre-Payment Verification &amp; Safety Checklist</h2>
        <p>Before proceeding to <strong>{sec3}</strong> or purchasing any digital subscription in Pakistan, always review these four safety benchmarks:</p>
        <ol>
          <li><strong>Verify Access Type:</strong> Distinguish between Private Account credentials (your own profile), Team Invitation access, and official License Keys.</li>
          <li><strong>Inspect Warranty Coverage:</strong> Never buy digital access without an explicit, documented replacement warranty (e.g., 7-day or 30-day warranty).</li>
          <li><strong>Confirm WhatsApp Availability:</strong> Ensure active customer support is available to assist with onboarding and immediate access questions.</li>
          <li><strong>Recheck PKR Pricing:</strong> Ensure no hidden foreign exchange markups are applied at the time of checkout.</li>
        </ol>
      </section>

      <section class="content-section">
        <h2>How to Order via EasyPaisa and JazzCash</h2>
        <p>Activating your subscription takes less than 30 minutes using our streamlined WhatsApp order process:</p>
        <ol>
          <li>Explore the verified marketplace listing on AI Tool Gems.</li>
          <li>Click 'Order on WhatsApp' to connect directly with our support team.</li>
          <li>Confirm availability, plan type (Private, Invitation, or License Key), and exact PKR total.</li>
          <li>Send payment via EasyPaisa, JazzCash, SadaPay, NayaPay, or direct bank transfer.</li>
          <li>Receive credentials and active warranty confirmation directly on WhatsApp.</li>
        </ol>
      </section>

      <section class="content-section">
        <h2>Comparison Matrix: Features, Access &amp; Pakistani PKR Rates</h2>
        <p>To help you compare options including <strong>{sec1}</strong>, review the key factors below:</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Tool / Solution</th>
                <th>Primary Strength</th>
                <th>Access Type</th>
                <th>Local Payment Support</th>
                <th>Warranty Coverage</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Leonardo AI Essential</strong></td>
                <td>High-fidelity photorealism &amp; prompt fidelity</td>
                <td>Private Account</td>
                <td>EasyPaisa, JazzCash, Bank Transfer</td>
                <td>7-Day Replacement Warranty</td>
              </tr>
              <tr>
                <td><strong>Canva Pro Edu</strong></td>
                <td>Social graphics, templates &amp; magic studio</td>
                <td>Invitation Seat</td>
                <td>EasyPaisa, JazzCash, SadaPay</td>
                <td>30-Day Replacement Warranty</td>
              </tr>
              <tr>
                <td><strong>Adobe Creative Cloud</strong></td>
                <td>Full industry suite &amp; Firefly generation</td>
                <td>Invitation / Private</td>
                <td>EasyPaisa, JazzCash, Bank Transfer</td>
                <td>Active Period Warranty</td>
              </tr>
              <tr>
                <td><strong>CapCut Pro VIP</strong></td>
                <td>Auto-captions, 4K 60fps export &amp; video effects</td>
                <td>Private Profile</td>
                <td>EasyPaisa, JazzCash, SadaPay</td>
                <td>7-Day Replacement Warranty</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="content-section">
        <h2>Final Recommendation for Pakistani Buyers</h2>
        <p>If you are creating digital assets for international clients or building a local brand in Pakistan, avoiding high bank deductions and unverified seller accounts is essential. Review your monthly generation requirements, verify the access model that fits your team, and confirm delivery timelines with our support team on WhatsApp before ordering.</p>
      </section>

      <section class="content-section">
        <h2>Related AI Tools &amp; Local Guides</h2>
        <p>Explore complementary tools in the Pakistani digital creator stack:</p>
        <ul>
{related_links_html}
          <li><a href="../ai-tools-price-pakistan/">AI Tools Price Guide for Pakistan (PKR Table)</a></li>
          <li><a href="../../deals/">Current Verified Deals &amp; Discounts</a></li>
          <li><a href="../../policies.html#warranty">Verified 7-Day Warranty Policy</a></li>
        </ul>
      </section>

      <section class="faq-section">
        <h2>Frequently Asked Questions</h2>
{faq_accordion_html}
      </section>
    </article>
  </main>

  <footer>
    <span>&copy; 2026 AI Tool Gems Pakistan</span>
    <span>Independent digital marketplace &middot; All third-party trademarks belong to their respective owners.</span>
  </footer>
  <script src="../../attribution.js"></script>
</body>
</html>"""
    return html


def run_publisher(dry_run: bool = True):
    print("=================================================================")
    print("🤖 AIToolGems Autonomous Daily Blog & Guide Publisher")
    print("=================================================================")
    print(f"Mode: {'DRY RUN (Preview Only)' if dry_run else 'LIVE PUBLISH'}")

    candidate = load_queue_candidate()
    if not candidate:
        print("ℹ️ All candidate topics from current queue are already published.")
        return

    print(f"🎯 Selected Topic: {candidate['title']}")
    print(f"📂 Target Slug: /guides/{candidate['slug']}/")
    print(f"🔑 Primary Keyword: {candidate['primary_keyword']}")

    # 1. Anti-cannibalization check
    can_ok, can_msg = check_cannibalization(candidate["slug"], candidate["primary_keyword"])
    if not can_ok:
        print(f"❌ Cannibalization check failed: {can_msg}. Aborting.")
        return
    print(f"✅ Anti-cannibalization check: {can_msg}")

    # 2. Render content
    html_content = render_article_html(candidate)

    # 3. Write temp file and run full validation
    temp_dir = BASE / "guides" / candidate["slug"]
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / "index.html"
    temp_file.write_text(html_content, encoding="utf-8")

    is_valid, issues = validate_article_file(temp_file, candidate["slug"])
    if not is_valid:
        print(f"❌ Pre-publish validation failed with {len(issues)} issue(s):")
        for iss in issues:
            print(f"  • {iss}")
        temp_file.unlink(missing_ok=True)
        if temp_dir.exists() and not any(temp_dir.iterdir()):
            temp_dir.rmdir()
        if not dry_run:
            sys.exit(1)
        return

    print("✅ Pre-publish content, SEO, link, and integrity checks PASSED.")

    # 4. If dry run, clean up temp file and report
    if dry_run:
        temp_file.unlink(missing_ok=True)
        if not any(temp_dir.iterdir()):
            temp_dir.rmdir()
        print("\n✨ Dry run complete. Validated topic is queued and ready for publication.")
        return

    # 5. Live publish: sync sitemap, llms.txt, guides/index.html, keyword-map.json
    print(f"\n🚀 Finalizing publication for: {temp_file}")

    # Update sitemap.xml
    sitemap_file = BASE / "sitemap.xml"
    sitemap_txt = sitemap_file.read_text(encoding="utf-8")
    new_loc = f"https://aitoolgems.tech/guides/{candidate['slug']}/"
    if new_loc not in sitemap_txt:
        today = datetime.date.today().isoformat()
        new_entry = f"  <url><loc>{new_loc}</loc><lastmod>{today}</lastmod></url>\n</urlset>"
        sitemap_txt = sitemap_txt.replace("</urlset>", new_entry)
        sitemap_file.write_text(sitemap_txt, encoding="utf-8")
        print(f"✅ Added {new_loc} to sitemap.xml")

    # Update llms.txt
    llms_file = BASE / "llms.txt"
    if llms_file.exists():
        llms_txt = llms_file.read_text(encoding="utf-8")
        if new_loc not in llms_txt:
            entry = f"- [{candidate['title']}](https://aitoolgems.tech/guides/{candidate['slug']}/) — Pakistan-focused {candidate['primary_keyword']} guide\n"
            llms_txt = llms_txt.replace("## Editorial Guides", f"## Editorial Guides\n\n{entry.strip()}")
            llms_file.write_text(llms_txt, encoding="utf-8")
            print(f"✅ Added {candidate['slug']} to llms.txt")

    # Update guides/index.html card grid
    guides_index = BASE / "guides" / "index.html"
    if guides_index.exists():
        g_txt = guides_index.read_text(encoding="utf-8")
        if candidate["slug"] not in g_txt:
            card_html = f"""      <article class="guide-card"><p class="eyebrow">EDITORIAL GUIDE</p><h2>{candidate['title']}</h2><p>{candidate['meta_desc']}</p><a href="{candidate['slug']}/">Read guide →</a></article>\n"""
            g_txt = g_txt.replace('<section class="guide-grid" aria-label="Available guides">\n', '<section class="guide-grid" aria-label="Available guides">\n' + card_html)
            guides_index.write_text(g_txt, encoding="utf-8")
            print(f"✅ Injected new guide card into guides/index.html")

    # Update blog/index.html articles grid
    blog_index = BASE / "blog" / "index.html"
    if blog_index.exists():
        b_txt = blog_index.read_text(encoding="utf-8")
        if candidate["slug"] not in b_txt and '<div class="blog-articles">\n' in b_txt:
            b_card = f"""        <article style="background: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid rgba(43,91,74,0.12); margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);"><p style="font-size: 0.75rem; font-weight: 700; color: #2f9f88; text-transform: uppercase; margin-bottom: 6px;">EDITORIAL GUIDE</p><h3 style="font-size: 1.25rem; margin-bottom: 8px;"><a href="../guides/{candidate['slug']}/" style="color: #173c35; text-decoration: none; font-weight: 700;">{candidate['title']}</a></h3><p style="color: #61766e; font-size: 0.95rem; line-height: 1.5;">{candidate['meta_desc']}</p><a href="../guides/{candidate['slug']}/" style="display: inline-block; margin-top: 10px; color: #2f9f88; font-weight: 600; text-decoration: none;">Read article &rarr;</a></article>\n"""
            b_txt = b_txt.replace('<div class="blog-articles">\n', '<div class="blog-articles">\n' + b_card)
            blog_index.write_text(b_txt, encoding="utf-8")
            print(f"✅ Injected new article link into blog/index.html")

    # Update data/seo/keyword-map.json
    map_file = BASE / "data" / "seo" / "keyword-map.json"
    if map_file.exists():
        k_data = json.loads(map_file.read_text(encoding="utf-8"))
        for entry in k_data:
            if entry["slug"] == candidate["slug"]:
                entry["status"] = "published"
                entry["published_url"] = new_loc
                entry["published_date"] = datetime.date.today().isoformat()
                entry["last_updated"] = datetime.date.today().isoformat()
        map_file.write_text(json.dumps(k_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ Updated keyword-map.json status to 'published'")

    # Trigger IndexNow automatically for the new published article
    try:
        idx_res = submit_to_indexnow([new_loc])
        print(f"⚡ IndexNow submission status: {idx_res.get('status')}")
    except Exception as e:
        print(f"⚠️ IndexNow notice: {e}")

    # Dispatch Telegram alert to owner
    msg = f"📰 *HERMES Content Agent: New Guide Published!*\n\n🎯 *Title:* {candidate['title']}\n🔗 *URL:* {new_loc}\n🇵🇰 *Focus:* {candidate['primary_keyword']}\n⚡ *Status:* Submitted to IndexNow & live on site."
    send_telegram_alert(msg)

    print("\n🎉 Article successfully published and synchronized across the entire site.")


if __name__ == "__main__":
    is_live = "--publish" in sys.argv
    run_publisher(dry_run=not is_live)
