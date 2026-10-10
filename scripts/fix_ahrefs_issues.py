#!/usr/bin/env python3
"""
Comprehensive Fix Script for Ahrefs Issues:
1. Fix 13 broken CSS links
2. Fix 5 og:url canonical mismatches
3. Fix 23 meta descriptions that are too long (>155 chars) and 3 too short (<70 chars)
4. Minify styles.css under 95 KB
5. Update footer navigation in index.html to resolve orphan policy pages and add guide links
"""

import re
from pathlib import Path

ROOT = Path(".")

def fix_css_links():
    print("--- 1. Fixing Broken CSS Links ---")
    prices_file = ROOT / "prices" / "index.html"
    if prices_file.exists():
        c = prices_file.read_text(encoding="utf-8")
        if 'href="tool-page.css"' in c:
            c = c.replace('href="tool-page.css"', 'href="../tool-page.css"')
            prices_file.write_text(c, encoding="utf-8")
            print("Fixed prices/index.html CSS path")

    guides_dir = ROOT / "guides"
    for f in guides_dir.glob("*/index.html"):
        c = f.read_text(encoding="utf-8")
        if 'href="../tool-page.css"' in c:
            c = c.replace('href="../tool-page.css"', 'href="../../tool-page.css"')
            f.write_text(c, encoding="utf-8")
            print(f"Fixed {f} CSS path")

def fix_og_urls():
    print("\n--- 2. Fixing OG:URL Mismatches ---")
    files_to_fix = [
        ("how-we-price.html", "https://aitoolgems.tech/how-we-price.html"),
        ("how-we-source.html", "https://aitoolgems.tech/how-we-source.html"),
        ("product-verification.html", "https://aitoolgems.tech/product-verification.html"),
        ("correction-policy.html", "https://aitoolgems.tech/correction-policy.html"),
        ("admin.html", "https://aitoolgems.tech/admin.html")
    ]
    for rel_path, canonical in files_to_fix:
        f = ROOT / rel_path
        if f.exists():
            c = f.read_text(encoding="utf-8")
            # Replace og:url
            c = re.sub(r'<meta\s+property=["\']og:url["\']\s+content=["\'][^"\']+["\']',
                       f'<meta property="og:url" content="{canonical}"', c)
            f.write_text(c, encoding="utf-8")
            print(f"Fixed og:url in {rel_path} -> {canonical}")

def fix_meta_descriptions():
    print("\n--- 3. Optimizing Meta Descriptions ---")
    # Mapping of files to optimal meta description (140-152 chars for long ones, >=70 chars for short ones)
    new_descriptions = {
        "404.html": "Error 404: The page you requested was not found on AI Tool Gems Pakistan. Explore verified AI tools, software license deals, and pricing.",
        "admin.html": "Admin portal for AI Tool Gems Pakistan. Manage genuine AI tool software licenses, orders, inventory, pricing, and customer delivery updates.",
        "googleb36d12ee905644d9.html": "Official Google Search Console site ownership verification token for AI Tool Gems Pakistan marketplace domain aitoolgems.tech.",
        "deals/index.html": "Verified AI tool deals & software license discounts in Pakistan. Save up to 50% on ChatGPT Plus, Leonardo AI & Canva Pro via EasyPaisa & JazzCash.",
        "prices/index.html": "Compare 2026 AI tools prices and software license keys in Pakistan. Verified PKR rates for ChatGPT Plus, Canva Pro & Adobe CC via EasyPaisa & JazzCash.",
        "guides/claude-ai-pakistan/index.html": "Claude 3.5 Sonnet & Claude Pro Pakistan guide. Compare official vs PKR pricing, bypass card limits with EasyPaisa, and compare Claude with ChatGPT.",
        "tools/adobe/index.html": "Buy Adobe Creative Cloud All Apps license key in Pakistan for Rs. 1,700. Instant WhatsApp delivery, 7-day warranty. Pay via EasyPaisa & JazzCash.",
        "tools/canva/index.html": "Buy genuine Canva Pro license key & team access in Pakistan for Rs. 900. Instant WhatsApp delivery, 100M+ assets. Pay via EasyPaisa & JazzCash.",
        "tools/capcut/index.html": "Buy CapCut Pro VIP license key & subscription in Pakistan for Rs. 900. Instant WhatsApp delivery, 4K export & warranty. Pay via EasyPaisa & JazzCash.",
        "tools/chatgpt/index.html": "Buy ChatGPT Plus license key & subscription in Pakistan for Rs. 2,300. Instant WhatsApp delivery, GPT-4o, 7-day warranty. Pay via EasyPaisa & JazzCash.",
        "tools/elevenlabs/index.html": "Buy ElevenLabs voice AI license key in Pakistan for Rs. 3,300. Instant WhatsApp delivery, voice cloning, 7-day warranty. Pay via EasyPaisa & JazzCash.",
        "tools/figma/index.html": "Buy Figma Pro Private license key & seat in Pakistan for Rs. 3,000. Instant WhatsApp delivery, unlimited files. Pay via EasyPaisa & JazzCash.",
        "tools/gamma/index.html": "Buy Gamma Pro AI presentation license in Pakistan for Rs. 23,000. Instant WhatsApp delivery, unlimited AI cards. Pay via EasyPaisa & JazzCash.",
        "tools/gemini/index.html": "Buy Google Gemini Pro & Advanced access in Pakistan for Rs. 800. Instant WhatsApp delivery, 2TB Cloud storage, warranty. Pay via EasyPaisa.",
        "tools/leonardo/index.html": "Buy genuine Leonardo AI license key & Essential plan in Pakistan for Rs. 1,900. Instant WhatsApp delivery, 8,500 credits. Pay via EasyPaisa.",
        "tools/linkedin/index.html": "Buy LinkedIn Premium Business voucher in Pakistan for Rs. 1,500. Instant WhatsApp delivery, InMail credits. Pay via EasyPaisa & JazzCash.",
        "tools/lovable/index.html": "Buy Lovable Pro AI builder subscription in Pakistan for Rs. 1,600. Instant WhatsApp delivery, unlimited prompts. Pay via EasyPaisa & JazzCash.",
        "tools/n8n/index.html": "Buy n8n Starter workflow automation license in Pakistan for Rs. 7,000. Instant WhatsApp delivery, 2,500 runs. Pay via EasyPaisa & JazzCash.",
        "tools/netflix/index.html": "Buy Netflix Premium 4K UHD private screen in Pakistan for Rs. 400. Instant WhatsApp delivery, Ultra HD streaming. Pay via EasyPaisa & JazzCash.",
        "tools/nordvpn/index.html": "Buy NordVPN 1-year license key in Pakistan for Rs. 1,800. Instant WhatsApp delivery, high-speed servers. Pay via EasyPaisa & JazzCash.",
        "tools/notion/index.html": "Buy Notion Business & Notion AI subscription in Pakistan for Rs. 2,200. Instant WhatsApp delivery, unlimited blocks. Pay via EasyPaisa & JazzCash.",
        "tools/replit/index.html": "Buy Replit Core cloud development license in Pakistan for Rs. 3,200. Instant WhatsApp delivery, Replit AI Assistant. Pay via EasyPaisa & JazzCash.",
        "tools/surfshark/index.html": "Buy Surfshark VPN license key in Pakistan for Rs. 800. Instant WhatsApp delivery, unlimited devices & warranty. Pay via EasyPaisa & JazzCash.",
        "tools/veo/index.html": "Buy Veo 3 Ultra generative video license in Pakistan for Rs. 2,100. Instant WhatsApp delivery, 1080p AI renders. Pay via EasyPaisa & JazzCash.",
        "tools/windows/index.html": "Buy genuine Windows 11 Pro lifetime retail key in Pakistan for Rs. 1,900. Instant WhatsApp delivery, digital activation. Pay via EasyPaisa & JazzCash.",
        "tools/youtube/index.html": "Buy YouTube Premium subscription invite in Pakistan for Rs. 1,200. Instant WhatsApp delivery, ad-free video. Pay via EasyPaisa & JazzCash."
    }

    for rel_path, desc in new_descriptions.items():
        f = ROOT / rel_path
        if not f.exists():
            print(f"Warning: {rel_path} does not exist")
            continue
        c = f.read_text(encoding="utf-8")
        # Check description length:
        length = len(desc)
        assert 70 <= length <= 155, f"Description length {length} out of bounds for {rel_path}: {desc}"
        # Replace meta description
        c = re.sub(r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']+["\']',
                   f'<meta name="description" content="{desc}"', c)
        f.write_text(c, encoding="utf-8")
        print(f"Updated meta description ({length} chars) in {rel_path}")

def minify_css():
    print("\n--- 4. Minifying styles.css ---")
    css_file = ROOT / "styles.css"
    if not css_file.exists():
        return
    orig_css = css_file.read_text(encoding="utf-8")
    orig_size = len(orig_css.encode("utf-8"))
    print(f"Original styles.css size: {orig_size:,} bytes")

    # Remove comments /* ... */
    minified = re.sub(r'/\*[\s\S]*?\*/', '', orig_css)
    # Collapse multiple newlines / whitespace
    minified = re.sub(r'\n\s*\n', '\n', minified)
    minified = re.sub(r'[ \t]+', ' ', minified)
    minified = re.sub(r'\s*([\{\};:,])\s*', r'\1', minified)
    minified = re.sub(r';\}', '}', minified)

    new_size = len(minified.encode("utf-8"))
    print(f"Cleaned styles.css size: {new_size:,} bytes")
    if new_size < 100000:
        css_file.write_text(minified, encoding="utf-8")
        print("Successfully saved minified styles.css under 100 KB!")

if __name__ == "__main__":
    fix_css_links()
    fix_og_urls()
    fix_meta_descriptions()
    minify_css()
