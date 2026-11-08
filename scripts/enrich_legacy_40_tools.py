#!/usr/bin/env python3
"""
scripts/enrich_legacy_40_tools.py - Enriches the 40 commercial tool detail pages with:
1. Target Search Queries & Keyword Clusters (.tool-seo-clusters)
2. Verified Domestic Payment & Banking Rails (.pakistan-banking-support)
3. Category Hub & Buying Guide links (.category-hub-links)

Maintains 100% of existing H1s, titles, canonical URLs, pricing, cart/checkout invariants, and schema integrity.
"""

from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent.parent

COMMERCIAL_TOOL_CLUSTERS = {
    "adobe": ["Adobe Creative Cloud Pakistan", "Adobe CC price PKR", "Photoshop Illustrator subscription", "Adobe Creative Cloud discount", "Adobe Pakistan payment EasyPaisa"],
    "allinone": ["All in One AI tools pack", "AI mega bundle Pakistan", "ChatGPT Claude Midjourney bundle", "affordable AI tools pack PKR", "best AI subscription bundle"],
    "canva": ["Canva Pro price Pakistan", "Canva Pro Edu invitation", "Canva subscription PKR", "Canva Pro lifetime deal", "buy Canva Pro EasyPaisa"],
    "capcut": ["CapCut Pro price Pakistan", "CapCut Pro VIP account", "CapCut desktop Windows Mac", "CapCut video editor subscription", "buy CapCut Pro JazzCash"],
    "chatgpt": ["ChatGPT Plus price Pakistan", "ChatGPT 4o subscription PKR", "buy ChatGPT Plus on WhatsApp", "ChatGPT Plus EasyPaisa", "OpenAI ChatGPT Plus Pakistan"],
    "claude": ["Claude Pro price Pakistan", "Claude 3.5 Sonnet subscription", "Anthropic Claude Pro PKR", "Claude AI Pakistan access", "buy Claude Pro EasyPaisa"],
    "copilot": ["GitHub Copilot price Pakistan", "Copilot subscription PKR", "GitHub Copilot VS Code", "Copilot student individual", "buy GitHub Copilot JazzCash"],
    "cursor": ["Cursor AI Pro price Pakistan", "Cursor AI subscription PKR", "Cursor vs VS Code", "Cursor Pro Claude Sonnet", "buy Cursor AI Pro EasyPaisa"],
    "deepseek": ["DeepSeek Unlimited Pakistan", "DeepSeek R1 price PKR", "DeepSeek API subscription", "DeepSeek AI assistant", "buy DeepSeek access Pakistan"],
    "elevenlabs": ["ElevenLabs price Pakistan", "ElevenLabs Voice AI subscription", "AI voice cloning PKR", "ElevenLabs credits Pakistan", "buy ElevenLabs EasyPaisa"],
    "figma": ["Figma Pro price Pakistan", "Figma professional team subscription", "Figma UI UX design PKR", "Figma invitation seat", "buy Figma Pro SadaPay"],
    "freepik": ["Freepik Premium price Pakistan", "Freepik subscription PKR", "Freepik vector download limit", "Freepik Pikaso AI", "buy Freepik Premium EasyPaisa"],
    "gamma": ["Gamma App Pro price Pakistan", "Gamma AI presentation maker", "Gamma subscription PKR", "Gamma unlimited AI credits", "buy Gamma Pro JazzCash"],
    "gemini": ["Google Gemini Pro price Pakistan", "Gemini Advanced subscription", "Google One AI Premium PKR", "Gemini 18 Months invitation", "buy Gemini Pro EasyPaisa"],
    "grammarly": ["Grammarly Premium price Pakistan", "Grammarly subscription PKR", "Grammarly proofreading tool", "Grammarly plagiarism checker", "buy Grammarly Premium JazzCash"],
    "grok": ["Grok 2 price Pakistan", "SuperGrok subscription PKR", "xAI Grok access", "Grok Twitter X Premium", "buy Grok 2 Pakistan"],
    "heygen": ["HeyGen AI price Pakistan", "HeyGen Avatar Pro subscription", "AI spokesperson video PKR", "HeyGen credits Pakistan", "buy HeyGen Pro EasyPaisa"],
    "kling": ["Kling AI price Pakistan", "Kling AI video generator", "Kling subscription PKR", "Kling v1.5 credits", "buy Kling AI JazzCash"],
    "leonardo": ["Leonardo AI price Pakistan", "Leonardo AI Essential subscription", "Leonardo image generation PKR", "Leonardo Phoenix model", "buy Leonardo AI EasyPaisa"],
    "linkedin": ["LinkedIn Premium price Pakistan", "LinkedIn Business Career subscription", "InMail credits PKR", "LinkedIn Premium invitation", "buy LinkedIn Premium SadaPay"],
    "lovable": ["Lovable Pro price Pakistan", "Lovable dev subscription PKR", "Lovable AI app builder", "Lovable vs v0", "buy Lovable Pro EasyPaisa"],
    "midjourney": ["Midjourney v6.1 price Pakistan", "Midjourney Pro subscription PKR", "Midjourney Discord access", "fast GPU hours Midjourney", "buy Midjourney EasyPaisa"],
    "n8n": ["n8n Starter price Pakistan", "n8n workflow automation", "n8n self hosted cloud", "n8n subscription PKR", "buy n8n Starter JazzCash"],
    "netflix": ["Netflix Premium price Pakistan", "Netflix 4K Ultra HD screen", "Netflix monthly subscription PKR", "Netflix private screen", "buy Netflix EasyPaisa"],
    "nordvpn": ["NordVPN price Pakistan", "NordVPN Plus subscription", "NordVPN 3 Months access", "best VPN for Pakistan", "buy NordVPN SadaPay"],
    "notion": ["Notion Business price Pakistan", "Notion AI subscription PKR", "Notion workspace team", "Notion unlimited blocks", "buy Notion Business EasyPaisa"],
    "office365": ["Office 365 price Pakistan", "Microsoft 365 1TB OneDrive", "Office 365 5 devices PKR", "genuine Microsoft Office key", "buy Office 365 EasyPaisa"],
    "perplexity": ["Perplexity Pro price Pakistan", "Perplexity AI subscription PKR", "Perplexity Pro Claude Sonnet", "Perplexity search engine", "buy Perplexity Pro JazzCash"],
    "quillbot": ["QuillBot Premium price Pakistan", "QuillBot paraphrasing subscription", "QuillBot grammar plagiarism", "QuillBot premium PKR", "buy QuillBot EasyPaisa"],
    "replit": ["Replit Core price Pakistan", "Replit subscription PKR", "Replit Agent AI coding", "Replit cloud IDE credits", "buy Replit Core JazzCash"],
    "runway": ["Runway Gen-3 price Pakistan", "Runway ML subscription PKR", "Runway video generator", "Runway Gen-3 Alpha Turbo", "buy Runway ML EasyPaisa"],
    "semrush": ["SEMrush Pro price Pakistan", "SEMrush SEO subscription PKR", "SEMrush keyword research tool", "SEMrush shared account", "buy SEMrush Pro JazzCash"],
    "spotify": ["Spotify Premium price Pakistan", "Spotify Individual Family PKR", "Spotify ad free music", "Spotify subscription Pakistan", "buy Spotify Premium EasyPaisa"],
    "suno": ["Suno AI price Pakistan", "Suno v3.5 subscription", "AI music generator PKR", "Suno credits commercial rights", "buy Suno AI EasyPaisa"],
    "surfshark": ["Surfshark VPN price Pakistan", "Surfshark unlimited devices", "Surfshark subscription PKR", "fast VPN Pakistan", "buy Surfshark JazzCash"],
    "tradingview": ["TradingView Pro price Pakistan", "TradingView subscription PKR", "Pine Script indicators charts", "TradingView multi timeframe", "buy TradingView Pro EasyPaisa"],
    "turnitin": ["Turnitin Student account Pakistan", "Turnitin similarity report PKR", "non repository Turnitin check", "Turnitin AI detection index", "buy Turnitin account EasyPaisa"],
    "veo": ["Google Veo 3 price Pakistan", "Veo 3 Ultra video generation", "Google DeepMind Veo PKR", "Veo AI video access", "buy Veo 3 Ultra Pakistan"],
    "windows": ["Windows 11 Pro key Pakistan", "Windows 11 retail license key", "Windows 11 activation PKR", "genuine Windows 11 Pro", "buy Windows 11 key EasyPaisa"],
    "youtube": ["YouTube Premium price Pakistan", "YouTube ad free background play", "YouTube Music subscription PKR", "YouTube family invitation", "buy YouTube Premium EasyPaisa"]
}

CATEGORY_TO_GUIDE = {
    "AI Assistants": ("ai-tools-pakistan", "AI Assistants & Chatbots"),
    "Development": ("developers", "Developers & Coders"),
    "Design": ("creators", "Designers & Digital Creators"),
    "AI Video": ("best-ai-video-generators-pakistan", "AI Video Generators"),
    "AI Voice": ("creators", "Voice AI & Creators"),
    "Writing & SEO": ("creators", "Writers & Marketers"),
    "Productivity": ("productivity", "Productivity & Remote Work"),
    "Business": ("businesses", "Business & Professional Tools"),
    "Entertainment": ("creators", "Entertainment & Media"),
    "VPN & Security": ("businesses", "Privacy & Security"),
    "VPN &amp; Security": ("businesses", "Privacy & Security"),
    "Software": ("productivity", "Operating Systems & Software"),
}

def enrich_page(slug: str, dry_run: bool = False) -> bool:
    page_path = BASE / "tools" / slug / "index.html"
    if not page_path.exists():
        print(f"❌ Missing page: {page_path}")
        return False

    content = page_path.read_text(encoding="utf-8")
    original_content = content

    # 1. Detect Category
    cat_m = re.search(r'<span class=[\"\']category[\"\']>(.*?)</span>', content)
    cat = cat_m.group(1).strip() if cat_m else "AI Assistants"
    guide_slug, guide_label = CATEGORY_TO_GUIDE.get(cat, ("ai-tools-pakistan", "AI Tools"))

    # Detect Tool Name
    name_m = re.search(r'<h1>(.*?)</h1>', content)
    tool_name = name_m.group(1).strip() if name_m else slug.title()
    # clean tool name from title artifacts like " Price in Pakistan..."
    clean_name = re.sub(r'\s*(?:Subscription\s*)?Price in Pakistan.*', '', tool_name, flags=re.I).strip()
    if not clean_name:
        clean_name = slug.title()

    # 2. Add Target Search Queries & Keyword Clusters (.tool-seo-clusters) if not present
    if "tool-seo-clusters" not in content and slug in COMMERCIAL_TOOL_CLUSTERS:
        keywords = COMMERCIAL_TOOL_CLUSTERS[slug]
        pills_html = "\n".join([f'        <span class="kw-pill">{kw}</span>' for kw in keywords])
        clusters_section = f"""
    <section class="tool-seo-clusters">
      <h2>Target Search Queries &amp; Keyword Clusters</h2>
      <div class="keyword-pills-wrap">
{pills_html}
      </div>
    </section>
"""
        # Insert right after </article>
        article_end = "</article>"
        if article_end in content:
            content = content.replace(article_end, f"{article_end}\n{clusters_section}", 1)

    # 3. Add Verified Domestic Payment & Banking Rails (.pakistan-banking-support) if not present
    if "pakistan-banking-support" not in content:
        banking_rails_html = f"""
      <div class="pakistan-banking-support">
        <h3>Verified Domestic Payment &amp; Banking Rails for Pakistani Users</h3>
        <p>Pakistani users ordering {clean_name} or seeking assisted setup can rely on these verified payment channels:</p>
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
"""
        # Insert inside <section class="pricing-plans-section"> right after </div> that closes table-wrap
        table_wrap_end = "</div>\n    </section>"
        if table_wrap_end in content:
            content = content.replace(table_wrap_end, f"</div>\n{banking_rails_html}    </section>", 1)
        else:
            # Fallback: right before </section> of pricing-plans-section
            plans_m = re.search(r'(<section class=[\"\']pricing-plans-section[\"\']>.*?)(\s*</section>)', content, re.DOTALL)
            if plans_m:
                content = content[:plans_m.end(1)] + "\n" + banking_rails_html + content[plans_m.end(1):]

    # 4. Add Category Hub Links (.category-hub-links) if not present
    if "category-hub-links" not in content:
        hub_links_html = f"""
    <section class="category-hub-links">
      <h3>Explore Related Categories &amp; Pakistani Buying Guides</h3>
      <div class="hub-pills">
        <a href="../../guides/{guide_slug}/" class="hub-pill">Guides for {guide_label} &rarr;</a>
        <a href="../../guides/ai-tools-price-pakistan/" class="hub-pill">Pakistan AI Tools Price Index &rarr;</a>
        <a href="../../deals/" class="hub-pill">View All Active Deals &rarr;</a>
        <a href="../../tools/" class="hub-pill">Browse All 65 Verified Tools &rarr;</a>
      </div>
    </section>
"""
        # Insert right before </main>
        main_end = "</main>"
        if main_end in content:
            content = content.replace(main_end, f"{hub_links_html}  </main>", 1)

    if content != original_content:
        if not dry_run:
            page_path.write_text(content, encoding="utf-8")
        print(f"✅ Enriched {slug}/index.html")
        return True
    else:
        print(f"ℹ️ No changes needed for {slug}")
        return False

def main():
    dry_run = "--dry-run" in sys.argv
    count = 0
    for slug in COMMERCIAL_TOOL_CLUSTERS.keys():
        if enrich_page(slug, dry_run=dry_run):
            count += 1
    print(f"\nDone! Enriched {count} of {len(COMMERCIAL_TOOL_CLUSTERS)} commercial tool pages.")

if __name__ == "__main__":
    main()

