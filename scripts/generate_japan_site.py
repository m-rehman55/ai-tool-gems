from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://aitoolgems.tech"
JP_WA = "817095128428"

PRODUCTS = [
    ("gemini", "Gemini Pro", "AI Assistants", 849, "18 Months", "Invitation", "Gemini Proを日本向けに比較。18か月、¥849。利用条件と提供状況は注文前に確認します。"),
    ("chatgpt", "ChatGPT Plus", "AI Assistants", 1697, "1 Month", "Private", "ChatGPT Plusを日本向けに比較。1か月、¥1,697。利用条件と提供状況は注文前に確認します。"),
    ("veo", "Veo 3 Ultra", "AI Video", 1415, "Unlimited", "Shared", "Veo 3 Ultraの日本向け掲載。¥1,415。動画生成プランと利用条件は注文前に確認します。"),
    ("leonardo", "Leonardo AI Essential", "Design", 1358, "8,500 Credits", "Private", "Leonardo AI Essentialを日本向けに比較。8,500クレジット、¥1,358。"),
    ("elevenlabs", "ElevenLabs", "AI Voice", 2150, "1 Month", "Private", "ElevenLabsの日本向け掲載。130Kクレジット、1か月、¥2,150。"),
    ("canva", "Canva Pro Edu", "Design", 679, "1 Year", "Invitation", "Canva Pro Eduを日本向けに比較。1年、¥679。利用条件は注文前に確認します。"),
    ("figma", "Figma Pro Private", "Design", 2207, "2 Years", "Private", "Figma Pro Privateを日本向けに比較。2年、¥2,207。"),
    ("capcut", "CapCut Pro", "AI Video", 679, "1 Month", "Private", "CapCut Proを日本向けに比較。1か月、¥679。"),
    ("adobe", "Adobe Creative", "Design", 1075, "2 Months / 1 Year", "Private", "Adobe Creativeの日本向け掲載。2か月¥1,075、1年¥15,277。プランは注文前に確認します。"),
    ("lovable", "Lovable Pro", "Development", 1075, "1 Month", "Private", "Lovable Proを日本向けに比較。1か月、¥1,075。"),
    ("gamma", "Gamma Pro", "Productivity", 14711, "1 Year", "Private", "Gamma Proを日本向けに比較。1年、¥14,711。"),
    ("replit", "Replit Core", "Development", 2150, "$40 Credits / 1 Year", "Private", "Replit Coreの日本向け掲載。$40クレジット¥2,150、1年¥7,921。プランは注文前に確認します。"),
    ("n8n", "n8n Starter", "Development", 4526, "1 Year", "Private", "n8n Starterを日本向けに比較。1年、¥4,526。"),
    ("manus", "Manus AI Pro", "AI Assistants", 8487, "1 Year", "Private", "Manus AI Proの日本向け掲載。1年、¥8,487。利用条件は注文前に確認します。"),
    ("notion", "Notion Business", "Productivity", 1415, "3 Months", "Invitation", "Notion Businessを日本向けに比較。3か月、¥1,415。"),
    ("nordvpn", "NordVPN", "VPN & Security", 6846, "3 Months", "Private", "NordVPNを日本向けに比較。3か月、¥6,846。"),
    ("surfshark", "Surfshark VPN", "VPN & Security", 679, "2 Months", "Shared", "Surfshark VPNを日本向けに比較。2か月、¥679。"),
    ("youtube", "YouTube Premium", "Entertainment", 1018, "3 Months", "Invitation", "YouTube Premiumを日本向けに比較。3か月、¥1,018。"),
    ("netflix", "Netflix Premium 4K", "Entertainment", 453, "1 Month", "Shared", "Netflix Premium 4Kを日本向けに比較。1か月、¥453。"),
    ("linkedin", "LinkedIn Premium", "Business", 1075, "2 Months", "Invitation", "LinkedIn Premiumを日本向けに比較。2か月、¥1,075。"),
    ("windows", "Windows 11 Pro License Key", "Software", 1245, "Lifetime", "License Key", "Windows 11 Pro License Keyを日本向けに比較。¥1,245。ライセンス条件は注文前に確認します。"),
]


def hreflang(jp_url: str, pk_url: str) -> str:
    return (
        f'<link rel="alternate" hreflang="ja-JP" href="{jp_url}">\n'
        f'  <link rel="alternate" hreflang="en-PK" href="{pk_url}">\n'
        f'  <link rel="alternate" hreflang="x-default" href="{pk_url}">'
    )


def page_head(title: str, description: str, canonical: str, alternate: str, schema: str) -> str:
    asset_prefix = "../../" if "/jp/tools/" in canonical else "../"
    return f'''<!doctype html>
<html lang="ja-JP">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{canonical}">
  {hreflang(canonical, alternate)}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="AI Tool Gems Japan">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/assets/brand-logo-light.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="{asset_prefix}assets/brand-logo-light.png">
  <link rel="stylesheet" href="{asset_prefix}tool-page.css">
  <script type="application/ld+json">{schema}</script>
</head>'''


def product_page(product: tuple) -> str:
    pid, name, category, price, duration, access, description = product
    canonical = f"{SITE}/jp/tools/{pid}/"
    pk = f"{SITE}/tools/{pid}/"
    order = f"https://wa.me/{JP_WA}?text={name.replace(' ', '%20')}%20の在庫、条件、配送時間を確認したいです。"
    schema = json.dumps({
        "@context": "https://schema.org", "@type": "Product", "name": name,
        "description": description, "url": canonical, "category": category,
        "inLanguage": "ja-JP", "offers": {"@type": "Offer", "priceCurrency": "JPY", "price": str(price), "availability": "https://schema.org/LimitedAvailability", "url": canonical},
    }, ensure_ascii=False, separators=(",", ":"))
    return page_head(f"{name} 日本価格 | AI Tool Gems Japan", description, canonical, pk, schema) + f'''
<body>
  <header class="topbar"><a class="brand" href="../../"><img src="../../assets/brand-logo-light.webp" width="48" height="48" alt="AI Tool Gems Japan logo"><span>AI TOOL <b>GEMS</b><small>JAPAN</small></span></a><nav aria-label="Main navigation"><a href="../../">すべてのツール</a><a href="../../#products">カテゴリー</a><a href="../../../tools/{pid}/">English version</a><a href="../../contact.html">お問い合わせ</a></nav></header>
  <main><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../../">ホーム</a><span>/</span><span>{escape(name)}</span></nav>
    <article class="product-layout"><section class="product-visual"><span class="category">{escape(category)}</span><div class="logo-wrap"><img src="../../assets/brand-logo-light.webp" width="128" height="128" alt="{escape(name)}"></div><p>独立系マーケットプレイス</p></section>
    <section class="product-copy"><p class="eyebrow">AI TOOL SUBSCRIPTION IN JAPAN</p><h1>{escape(name)} 日本価格</h1><p class="lead">{escape(description)} AI Tool Gems Japanでは、価格・期間・アクセス条件を確認してから注文できます。</p><p class="quick-answer"><strong>概要:</strong> 掲載価格は <strong>¥{price:,}</strong>。期間は {escape(duration)}、アクセス形式は {escape(access)} です。提供状況と正確な条件はWhatsAppで注文前に確認します。</p><div class="price"><span>掲載価格</span><strong>¥{price:,}</strong></div><dl><div><dt>期間</dt><dd>{escape(duration)}</dd></div><div><dt>アクセス</dt><dd>{escape(access)}</dd></div><div><dt>通貨</dt><dd>JPY</dd></div></dl><a class="buy" href="{order}" target="_blank" rel="noopener">WhatsAppで注文・確認</a><p class="availability">在庫、支払い方法、配送時間、利用条件は支払い前に確認します。</p></section></article>
    <section class="answer"><h2>ご注文前にご確認ください</h2><p>AI Tool Gems Japanは独立系のデジタルマーケットプレイスです。表示価格は日本向けの掲載価格であり、第三者ブランドの公式販売店・提携先であることを意味しません。ブランド名と商標はそれぞれの権利者に帰属します。</p><p>利用条件、アカウント形式、地域制限、保証・返金条件は商品ごとに異なるため、WhatsAppで最新情報を確認してください。</p></section>
    <section class="answer"><h2>Related information</h2><p><a href="../../">日本向けAIツール一覧</a> | <a href="../../../tools/{pid}/">English version</a> | <a href="../../contact.html">お問い合わせ</a></p></section>
  </main><footer><span>© 2026 AI Tool Gems Japan</span><span>Independent digital marketplace · Third-party trademarks belong to their owners.</span></footer>
</body></html>'''


def home_page() -> str:
    canonical = f"{SITE}/jp/"
    schema = json.dumps({"@context": "https://schema.org", "@type": ["Organization", "OnlineStore"], "name": "AI Tool Gems Japan", "url": canonical, "areaServed": {"@type": "Country", "name": "Japan"}, "contactPoint": {"@type": "ContactPoint", "telephone": "+" + JP_WA, "contactType": "customer support", "areaServed": "JP", "availableLanguage": ["Japanese", "English"]}}, ensure_ascii=False, separators=(",", ":"))
    cards = "\n".join(f'<article><h2><a href="tools/{pid}/">{escape(name)}</a></h2><p>{escape(description)}</p><strong>¥{price:,}</strong><p>{escape(duration)} · {escape(access)}</p></article>' for pid, name, category, price, duration, access, description in PRODUCTS)
    return page_head("AI Tools Japan | JPY Prices & WhatsApp Support", "Compare AI tools and digital subscriptions for customers in Japan with JPY prices, bilingual support, and direct WhatsApp ordering.", canonical, SITE + "/", schema) + f'''
<body><header class="topbar"><a class="brand" href="./"><img src="../assets/brand-logo-light.webp" width="48" height="48" alt="AI Tool Gems Japan logo"><span>AI TOOL <b>GEMS</b><small>JAPAN</small></span></a><nav aria-label="Main navigation"><a href="#products">AIツール</a><a href="#how">ご利用方法</a><a href="../">English version</a><a href="contact.html">お問い合わせ</a></nav></header>
<main><section class="hero"><p class="eyebrow">AI TOOLS FOR JAPAN</p><h1>日本向けAIツールとサブスクリプション</h1><p>JPY価格、期間、アクセス条件を比較。日本語・English対応で、注文前にWhatsAppで在庫と条件を確認できます。</p><a class="buy" href="https://wa.me/{JP_WA}?text=AI%20Tool%20Gems%20Japan%20の商品について相談したいです。">WhatsAppで相談する</a></section><section id="products"><h2>AI Tools — JPY Prices</h2><div class="product-grid">{cards}</div></section><section id="how" class="answer"><h2>ご利用方法 / How it works</h2><ol><li>商品と掲載価格を比較します。</li><li>WhatsAppで在庫、アクセス形式、支払い、配送時間を確認します。</li><li>条件に同意した後に注文を進めます。</li></ol><p>AI Tool Gems Japanは独立系マーケットプレイスであり、第三者ブランドの公式提携を意味しません。</p></section></main><footer><span>© 2026 AI Tool Gems Japan</span><span>Japan support: +81 70 9512 8428</span></footer></body></html>'''


def generate_visual_home() -> None:
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    source = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", source, flags=re.S)
    for old, new in {
        '<html lang="en-PK">': '<html lang="ja-JP">',
        "AI Tool Gems Pakistan": "AI Tool Gems Japan",
        "PAKISTAN": "JAPAN",
        "Pakistan-based AI Tools Marketplace": "Japan AI Tools Marketplace",
        "Premium AI Tools in Pakistan": "Premium AI Tools in Japan",
        'href="assets/': 'href="../assets/',
        'src="assets/': 'src="../assets/',
        'href="styles.css"': 'href="../styles.css"',
        'href="light-theme.css"': 'href="../light-theme.css"',
        'src="attribution.js"': 'src="../attribution.js"',
        'src="app.js"': 'src="app-jp.js"',
        'href="deals/"': 'href="../deals/"',
        'href="guides/"': 'href="../guides/"',
        'href="guides/': 'href="../guides/',
        'href="privacy.html"': 'href="../privacy.html"',
        'href="terms.html"': 'href="../terms.html"',
        'href="policies.html': 'href="../policies.html',
        'href="sitemap.xml"': 'href="../sitemap-jp.xml"',
    }.items():
        source = source.replace(old, new)
    source = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Compare AI tools and digital subscriptions in Japan with JPY pricing, Japanese and English support, and direct WhatsApp ordering.">', source, count=1)
    source = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://aitoolgems.tech/jp/">\n  <link rel="alternate" hreflang="ja-JP" href="https://aitoolgems.tech/jp/">\n  <link rel="alternate" hreflang="en-PK" href="https://aitoolgems.tech/">\n  <link rel="alternate" hreflang="x-default" href="https://aitoolgems.tech/">', source, count=1)
    source = re.sub(r'<title>.*?</title>', '<title>AI Tools Japan — JPY Prices &amp; WhatsApp Support</title>', source, count=1, flags=re.S)
    source = source.replace('https://wa.me/923236715731', 'https://wa.me/817095128428').replace('Rs. ', '¥').replace('PKR', 'JPY')
    source = source.replace('Pakistan', 'Japan').replace('PAKISTAN', 'JAPAN').replace('Japan / English', 'English version').replace('facebook.com/people/AI-Tool-Gems-Japan/', 'facebook.com/people/AI-Tool-Gems-Pakistan/').replace('20 AI', '22 AI').replace('all 20', 'all 22').replace('20 listings', '22 listings')
    for old, new in {
        'Premium AI tools': '日本向けプレミアムAIツール',
        'Compare before you choose.': '選ぶ前に比較しましょう。',
        'Find my tool': '最適なツールを探す',
        'How it works': 'ご利用方法',
        'Marketplace': 'マーケットプレイス',
        'Categories': 'カテゴリー',
        'Guides': 'ガイド',
        'Cart': 'カート',
        'Search': '検索',
        'Buy now': '今すぐ注文',
        'Order on WhatsApp': 'WhatsAppで注文',
        'WhatsApp support': 'WhatsAppサポート',
        'Compare': '比較',
        'All tools': 'すべてのツール',
        'How it works': 'ご利用方法',
    }.items():
        source = source.replace(old, new)
    (ROOT / "jp" / "index.html").write_text(source, encoding="utf-8")

    app = (ROOT / "app.js").read_text(encoding="utf-8")
    lines = []
    for pid, name, category, price, duration, access, description in PRODUCTS:
        lines.append(f"  {{id:'{pid}',name:'{name}',category:'{category}',description:'{description}',price:{price},oldPrice:{round(price * 1.2)},duration:'{duration}',access:'{access}',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']}}")
    app = re.sub(r'const products = \[.*?\];\n\nconst categoryData', "const products = [\n" + ",\n".join(lines) + "\n];\n\nconst categoryData", app, count=1, flags=re.S)
    app = app.replace("const DEFAULT_WA_NUMBER = '923236715731';", "const DEFAULT_WA_NUMBER = '817095128428';").replace("const LEGACY_WA_NUMBER = ['923', '476', '242709'].join('');", "const LEGACY_WA_NUMBER = '923236715731';")
    app = app.replace("'Rs. ' + n.toLocaleString('en-PK')", "'¥' + n.toLocaleString('ja-JP')").replace("'PKR'", "'JPY'").replace("PKR pricing", "JPY pricing").replace("assets/", "../assets/")
    for old, new in {
        'Marketplace': 'マーケットプレイス', 'Categories': 'カテゴリー', 'Guides': 'ガイド',
        'Find my tool': '最適なツールを探す', 'How it works': 'ご利用方法', 'Buy now': '今すぐ注文',
        'Order on WhatsApp': 'WhatsAppで注文', 'Compare now': '比較する', 'Select 2 or 3 products': '2〜3個の商品を選択',
        'Price': '価格', 'Duration': '期間', 'Access': 'アクセス', 'Features': '機能',
        'Cart': 'カート', 'All tools': 'すべてのツール', 'Search': '検索',
    }.items():
        app = app.replace(old, new)
    (ROOT / "jp" / "app-jp.js").write_text(app, encoding="utf-8")


def main() -> None:
    home = ROOT / "jp"
    (home / "tools").mkdir(parents=True, exist_ok=True)
    (home / "index.html").write_text(home_page(), encoding="utf-8")
    for product in PRODUCTS:
        path = home / "tools" / product[0] / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(product_page(product), encoding="utf-8")

    equivalents = {"index.html": f"{SITE}/jp/", "contact.html": f"{SITE}/jp/contact.html"}
    for pid, *_ in PRODUCTS:
        equivalents[f"tools/{pid}/index.html"] = f"{SITE}/jp/tools/{pid}/"
    for relative, jp_url in equivalents.items():
        path = ROOT / relative
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        if 'hreflang="ja-JP"' in html:
            continue
        pk_url = f"{SITE}/" if relative == "index.html" else f"{SITE}/{relative.replace('/index.html', '/').replace('index.html', '')}"
        tags = f'  <link rel="alternate" hreflang="ja-JP" href="{jp_url}">\n  <link rel="alternate" hreflang="en-PK" href="{pk_url}">\n  <link rel="alternate" hreflang="x-default" href="{pk_url}">\n'
        path.write_text(html.replace("</head>", tags + "</head>", 1), encoding="utf-8")
    generate_visual_home()


if __name__ == "__main__":
    main()
