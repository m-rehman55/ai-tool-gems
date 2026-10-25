#!/usr/bin/env python3
"""
Retrofits all 32 legacy tool pages in tools/ with:
1. Dual price display: <strong>Rs. {pkr:,} <small>(${usd} USD)</small></strong>
2. Inverted Pyramid AEO Quick-Answer update: includes (${usd} USD) and global payment rails (Wise, USDT)
3. Responsive pricing table: <section class="pricing-plans-section"> with local PKR and worldwide USD & Crypto
4. WhatsApp buy button query string with USD reference
Preserves 100% of canonical URLs, titles, H1s, breadcrumbs, and internal link graph integrity.
"""

from pathlib import Path
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent

LEGACY_TOOLS = {
    "adobe": {"name": "Adobe Creative Cloud", "pkr": 1700, "usd": "6.99", "duration": "2 Months", "access": "Private Account", "warranty": "7 Days"},
    "allinone": {"name": "All-in-One Mega AI Portal", "pkr": 1999, "usd": "7.99", "duration": "1 Month", "access": "Private Portal", "warranty": "30 Days"},
    "canva": {"name": "Canva Pro Edu", "pkr": 900, "usd": "3.99", "duration": "1 Year", "access": "Invitation Access", "warranty": "30 Days"},
    "capcut": {"name": "CapCut Pro VIP", "pkr": 900, "usd": "3.99", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "chatgpt": {"name": "ChatGPT Plus", "pkr": 2300, "usd": "8.99", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "claude": {"name": "Claude Pro (3.5 Sonnet)", "pkr": 2200, "usd": "8.99", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "cursor": {"name": "Cursor AI Pro", "pkr": 2800, "usd": "10.99", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "deepseek": {"name": "DeepSeek Unlimited", "pkr": 1100, "usd": "4.49", "duration": "1 Month", "access": "Private Portal", "warranty": "7 Days"},
    "elevenlabs": {"name": "ElevenLabs Voice AI", "pkr": 3300, "usd": "12.99", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "figma": {"name": "Figma Pro Private", "pkr": 3000, "usd": "11.99", "duration": "2 Years", "access": "Private Account", "warranty": "30 Days"},
    "gamma": {"name": "Gamma Pro", "pkr": 23000, "usd": "89.99", "duration": "1 Year", "access": "Private Account", "warranty": "30 Days"},
    "gemini": {"name": "Google Gemini Pro", "pkr": 800, "usd": "3.99", "duration": "18 Months", "access": "Invitation Access", "warranty": "30 Days"},
    "grammarly": {"name": "Grammarly Premium", "pkr": 750, "usd": "2.99", "duration": "1 Month", "access": "Private / Shared", "warranty": "7 Days"},
    "grok": {"name": "SuperGrok / Grok 2", "pkr": 1800, "usd": "6.99", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "heygen": {"name": "HeyGen AI Avatar Pro", "pkr": 4200, "usd": "16.99", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "leonardo": {"name": "Leonardo AI Essential", "pkr": 1900, "usd": "7.49", "duration": "8,500 Credits", "access": "Private Account", "warranty": "7 Days"},
    "linkedin": {"name": "LinkedIn Premium", "pkr": 1500, "usd": "5.99", "duration": "2 Months", "access": "Invitation Access", "warranty": "7 Days"},
    "lovable": {"name": "Lovable Pro", "pkr": 1600, "usd": "6.49", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "midjourney": {"name": "Midjourney v6.1 Pro", "pkr": 2400, "usd": "9.99", "duration": "1 Month", "access": "Private / Discord", "warranty": "7 Days"},
    "n8n": {"name": "n8n Starter", "pkr": 7000, "usd": "26.99", "duration": "1 Year", "access": "Private Account", "warranty": "30 Days"},
    "netflix": {"name": "Netflix Premium 4K", "pkr": 400, "usd": "1.99", "duration": "1 Month", "access": "Shared Screen", "warranty": "7 Days"},
    "nordvpn": {"name": "NordVPN Plus", "pkr": 1800, "usd": "6.99", "duration": "3 Months", "access": "Private Account", "warranty": "7 Days"},
    "notion": {"name": "Notion Business", "pkr": 2200, "usd": "8.99", "duration": "3 Months", "access": "Invitation Access", "warranty": "30 Days"},
    "perplexity": {"name": "Perplexity Pro", "pkr": 1400, "usd": "5.49", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "quillbot": {"name": "QuillBot Premium", "pkr": 450, "usd": "1.99", "duration": "1 Month", "access": "Private / Shared", "warranty": "7 Days"},
    "replit": {"name": "Replit Core", "pkr": 3200, "usd": "12.49", "duration": "$40 Credits", "access": "Private Account", "warranty": "7 Days"},
    "runway": {"name": "Runway ML Gen-3 Pro", "pkr": 3500, "usd": "13.99", "duration": "1 Month", "access": "Private Account", "warranty": "7 Days"},
    "semrush": {"name": "SEMrush Pro", "pkr": 1500, "usd": "5.99", "duration": "1 Month", "access": "Shared Account", "warranty": "7 Days"},
    "surfshark": {"name": "Surfshark VPN", "pkr": 800, "usd": "3.49", "duration": "2 Months", "access": "Shared Account", "warranty": "7 Days"},
    "veo": {"name": "Veo 3 Ultra", "pkr": 2100, "usd": "8.49", "duration": "Unlimited", "access": "Shared Account", "warranty": "7 Days"},
    "windows": {"name": "Windows 11 Pro Key", "pkr": 1900, "usd": "7.99", "duration": "Lifetime", "access": "License Key", "warranty": "7 Days"},
    "youtube": {"name": "YouTube Premium", "pkr": 1200, "usd": "4.99", "duration": "3 Months", "access": "Invitation Access", "warranty": "30 Days"}
}

def generate_plans_section(slug: str, meta: dict) -> str:
    return f"""
    <section class="pricing-plans-section">
      <h2>Available subscription plans &amp; multi-currency pricing</h2>
      <p>Compare durations and pricing for local Pakistani customers (PKR) and worldwide clients (USD &amp; Crypto). All plans feature verified access and direct human WhatsApp support.</p>
      <div class="table-wrap">
        <table class="plans-table">
          <thead>
            <tr>
              <th>Plan &amp; Duration</th>
              <th>PKR Price</th>
              <th>USD Price</th>
              <th>Access Type</th>
              <th>Supported Payment Rails</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>{meta['name']} ({meta['duration']})</strong></td>
              <td><strong>Rs. {meta['pkr']:,}</strong></td>
              <td><strong>${meta['usd']} USD</strong></td>
              <td>{meta['access']}</td>
              <td>EasyPaisa, JazzCash, SadaPay, Bank IBFT, Wise, USDT (Crypto)</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
"""

def retrofit_page(slug: str, meta: dict, dry_run: bool = False) -> bool:
    page_path = BASE / "tools" / slug / "index.html"
    if not page_path.exists():
        print(f"❌ Missing page: {page_path}")
        return False

    content = page_path.read_text(encoding="utf-8")

    # 1. Update <div class="price"> to include USD if not already present
    # Example: <strong>Rs. 2,300</strong> -> <strong>Rs. 2,300 <small>($8.99 USD)</small></strong>
    price_pattern = re.compile(r'(<div class="price"><span>Current listed price</span><strong>Rs\.\s*[\d,]+)(</strong>)', re.IGNORECASE)
    if not "<small>($" in content:
        content = price_pattern.sub(rf'\1 <small>(${meta["usd"]} USD)\2', content, count=1)

    # 2. Update <p class="quick-answer"> to include USD and global rails if not already present
    if f"(${meta['usd']} USD)" not in content:
        # Match "Rs. 2,300 PKR" -> "Rs. 2,300 PKR ($8.99 USD)"
        content = re.sub(
            rf'(Rs\.\s*{meta["pkr"]:,}\s*PKR)',
            rf'\1 (${meta["usd"]} USD)',
            content,
            count=1,
            flags=re.IGNORECASE
        )
        # Match "via EasyPaisa, JazzCash, SadaPay, or Bank Transfer" -> add Wise or USDT Crypto
        if "or USDT" not in content and "Bank Transfer" in content:
            content = content.replace(
                "or Bank Transfer",
                "Bank Transfer, Wise, or USDT (Crypto)",
                1
            )

    # 3. Inject <section class="pricing-plans-section"> right after </article> if not present
    if "pricing-plans-section" not in content:
        plans_html = generate_plans_section(slug, meta)
        content = re.sub(r'(</article>)', rf'\1\n{plans_html}', content, count=1)

    # 4. Update WhatsApp buy button to mention USD
    # Example: Rs.%202%2C300. -> Rs.%202%2C300%20%2F%20%248.99%20USD.
    pkr_encoded = f"{meta['pkr']:,}".replace(",", "%2C")
    usd_encoded = f"%20%2F%20%24{meta['usd']}%20USD"
    if usd_encoded not in content:
        content = re.sub(
            rf'({pkr_encoded})(\.|\%20|\&)',
            rf'\1{usd_encoded}\2',
            content,
            count=1
        )

    if not dry_run:
        page_path.write_text(content, encoding="utf-8")
        print(f"✅ Retrofitted: tools/{slug}/index.html")
    else:
        print(f"[DRY RUN] Would retrofit: tools/{slug}/index.html")

    return True

def main():
    dry_run = "--dry-run" in sys.argv
    print(f"Starting retrofit for {len(LEGACY_TOOLS)} legacy tool pages (Dry Run: {dry_run})...\n")
    success_count = 0
    for slug, meta in LEGACY_TOOLS.items():
        if retrofit_page(slug, meta, dry_run=dry_run):
            success_count += 1
    print(f"\nDone: {success_count} / {len(LEGACY_TOOLS)} pages processed successfully.")

if __name__ == "__main__":
    main()
